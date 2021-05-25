# # -*- coding:utf-8 -*-
from skosxl.models import *
from django.template import RequestContext
from django.shortcuts import get_object_or_404
# deprecated since 1.3
# from django.views.generic.list_detail import object_list
# but not used anyway?
# if needed.. from django.views.generic import ListView
from django.utils.text import slugify
from django.utils.html import strip_tags
from django.http import HttpResponse
import json
import requests


from importlib import import_module


def loadinit(req) :
    """
        ought to move this to rdf_io, and put in a module register process that triggers these for all modules rdf_io knows about
    """
    messages = {}
    if req.GET.get('pdb') :
        import pdb; pdb.set_trace()
    url_base = req.build_absolute_uri("/");
    loadlist = import_module('ogcext.fixtures.loadlist', 'ogcext.fixtures')
    for cfgname in loadlist.INITIAL_FIXTURES :
        cm = import_module("".join(('ogcext.fixtures.',cfgname)), 'dataweb.fixtures')
        messages.update( cm.loaddata(url_base) )
    return HttpResponse("loaded configurations:" + str(messages))  


def loaddocreg(req):
    """ Load the OGC doc register via API into equivalent SKOS Concept Scheme 
    
    Will assume the doc register also includes non-OGC - so two collections created at the top - OGC docs and normative references.
    Also flag those that are specifications, so they can be used in specification-related logic, such as candidates for profiles."""
 
    if req.GET.get('pdb') :
        import pdb; pdb.set_trace()
        
    if req.GET.get('stats') :
        statsonly = True
    else:
        statsonly = False
        
    tgt="http://www.opengis.net/def/docs" 
    if req.GET.get('file'):
        src='/repos/ogc/NamingAuthority/incubation/bibliography/bibliography.json'
        with open(src, 'r') as f:
            docs_dict = json.load(f)
    else:
        if req.GET.get('src'):
            src=req.GET.get('src')
        else:
            src='https://portal.opengeospatial.org/public_ogc/api/docs.php?CITE=1'
        with requests.get(src) as f:
            docs_dict = f.json()

    creator = GenericMetaProp.objects.get(uri='http://purl.org/dc/elements/1.1/creator')
    contributor =GenericMetaProp.objects.get(uri= 'http://purl.org/dc/elements/1.1/contributor')
    specdate =GenericMetaProp.objects.get(uri= 'http://purl.org/dc/terms/created')
    seealso = GenericMetaProp.objects.get(uri= 'http://www.w3.org/2000/01/rdf-schema#seeAlso')
    Namespace.objects.get_or_create(prefix='policy',uri="http://www.opengis.net/def/metamodel/ogc-na/")
    doctype,created = GenericMetaProp.objects.get_or_create(uri= 'http://www.opengis.net/def/metamodel/ogc-na/doctype')     
    
    ( docscheme, created ) = Scheme.objects.get_or_create(uri=tgt, defaults={'pref_label':'OGC Documents' , 'changenote': 'loaded from %s ' % (src ,) , 'definition':'OGC document register with annotations and links'} )  
    if ( not created ) : 
        Concept.objects.filter(scheme=docscheme).delete()
        Collection.objects.filter(scheme=docscheme).delete()
    
#    ( topcollection, created ) = Collection.objects.get_or_create(scheme=docscheme, pref_label='Document lists by document type'  , uri="/".join((tgt,"")) ) 

    
    publishers= {} 
    uri={}
    response = HttpResponse()
    max = -1
    if req.GET.get('max'):
        max=int(req.GET.get('max'))
    
    for num,doc in enumerate(docs_dict.values()):
        if num == max:
            break
        if publishers.get(doc['publisher']) :
            publishers[doc['publisher']] = publishers[doc['publisher']] +1 
        else:
            publishers[doc['publisher']] = 1
        if statsonly :
            uri[ doc['URI'] ] = True
        else:
            (d, created) = Concept.objects.get_or_create(term=slugify(doc['identifier']), definition=strip_tags(doc['description']).translate( {ord(c):None for c in '\n\t\r' }).encode('ascii',errors='ignore').decode(), pref_label=doc['title'].encode('ascii',errors='ignore').decode() , scheme=docscheme)
            (collection,created) = Collection.objects.get_or_create(scheme=docscheme , pref_label=doc['type'].encode('ascii',errors='ignore').decode(), uri="/".join((tgt,doc['type'].encode('ascii',errors='ignore').decode().lower())))
            ConceptMeta.objects.get_or_create(subject=d, metaprop=doctype, value="".join(("<http://www.opengis.net/def/doc-type/",doc['type'].encode('ascii',errors='ignore').decode().lower(),">") ) )
            
#            CollectionMember.objects.get_or_create(collection=topcollection, subcollection=collection)
            CollectionMember.objects.get_or_create(collection=collection, concept=d)
     
            Notation.objects.get_or_create(concept=d,code=doc.get('identifier').encode('ascii',errors='ignore').decode(), codetype="http://www.opengis.net/def/metamodel/ogc-na/doc_no")
            Label.objects.get_or_create(concept=d, label_type=1 , label_text=doc['identifier'].encode('utf-8').decode())
            #if doc.get('spec_id') :
            #    Notation.objects.get_or_create(concept=d,code=doc.get('spec_id'), codetype="http://www.opengis.net/def/metamodel/ogc-na/cite_spec_id")
            if doc.get('creator') : 
                ConceptMeta.objects.get_or_create(subject=d, metaprop=creator, value=doc['creator'].encode('utf-8').decode() )
            if doc.get('contributor') : 
                ConceptMeta.objects.get_or_create(subject=d, metaprop=contributor, value=doc['contributor'].encode('utf-8').decode() )
            if doc.get('date') : 
                ConceptMeta.objects.get_or_create(subject=d, metaprop=specdate, value= '"{}"^^xsd:date'.format(doc['date']))
            if doc.get('URL') : 
                ConceptMeta.objects.get_or_create(subject=d, metaprop=seealso, value=doc['URL'].encode('ascii',errors='ignore').decode().join(('<','>'))  )
            if doc.get('alternative') and  doc.get('alternative') != doc['title']:
                Label.objects.get_or_create(concept=d, label_type=1 , label_text=doc['alternative'].encode('ascii',errors='ignore').decode())
                
    response.write( '<A HREF="/admin/skosxl/scheme/%d/change/" target="_new">Show Scheme' % ( docscheme.id, ) )
    return response
        
    