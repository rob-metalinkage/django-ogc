# # -*- coding:utf-8 -*-
from django.shortcuts import render_to_response, redirect
from skosxl.models import *
from django.template import RequestContext
from django.shortcuts import get_object_or_404
# deprecated since 1.3
# from django.views.generic.list_detail import object_list
# but not used anyway?
# if needed.. from django.views.generic import ListView

from django.http import HttpResponse
import json



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
    
    if req.GET.get('stats') :
        statsonly = True
    else:
        statsonly = False
        
    tgt="http://www.opengis.net/def/docs" 
    src='/repos/ogc/ogc-na/sources/docregister/docs.php.js'
    creator = GenericMetaProp.objects.get(uri='http://purl.org/dc/elements/1.1/creator')
    contributor =GenericMetaProp.objects.get(uri= 'http://purl.org/dc/elements/1.1/contributor')
    seealso = GenericMetaProp.objects.get(uri= 'http://www.w3.org/2000/01/rdf-schema#seeAlso') 
    
    ( docscheme, created ) = Scheme.objects.get_or_create(uri=tgt, defaults={'pref_label':'OGC Documents' , 'changenote': 'loaded from %s ' % (src ,) , 'definition':'OGC document register with annotations and links'} )  
#    import pdb; pdb.set_trace()

    if ( not created ) : 
        Concept.objects.filter(scheme=docscheme).delete()
    with open(src, 'r') as f:
        docs_dict = json.load(f)
    
    publishers= {} 
    uri={}
    response = HttpResponse()
    for doc in docs_dict.values():
        if statsonly :
            if publishers.get(doc['publisher']) :
                publishers[doc['publisher']] = publishers[doc['publisher']] +1 
            else:
                publishers[doc['publisher']] = 1
            uri[ doc['URI'] ] = True
        else:
            (d, created) = Concept.objects.get_or_create(term=doc['identifier'], definition=doc['description'], pref_label=doc['title'] , scheme=docscheme)
            (collection,created) = Collection.objects.get_or_create(scheme=docscheme, pref_label=doc['type'] , uri="/".join((tgt,doc['type'].lower())))
            CollectionMember.objects.get_or_create(collection=collection, concept=d)
     
            Label.objects.get_or_create(concept=d, label_type=1 , label_text=doc['identifier'])
            if doc.get('creator') : 
                ConceptMeta.objects.get_or_create(subject=d, metaprop=creator, value=doc['creator'] )
            if doc.get('contributor') : 
                ConceptMeta.objects.get_or_create(subject=d, metaprop=contributor, value=doc['contributor'] )
            if doc.get('URL') : 
                ConceptMeta.objects.get_or_create(subject=d, metaprop=seealso, value=doc['URL'] )
            if doc.get('alternative') :
                Label.objects.get_or_create(concept=d, label_type=1 , label_text=doc['alternative'])
                
    response.write( { 'publishers' : publishers , 'uri' : uri } )
    return response
        
    