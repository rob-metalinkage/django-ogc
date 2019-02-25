# -*- coding: utf-8 -*-

from django.db import models

from skosxl.models import *

from django.utils.encoding import python_2_unicode_compatible

try:
    # python 3
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
    
from lxml import etree, objectify
from rdflib import Graph, URIRef, Literal, Namespace
# from skosxl.models import *


RDFTYPE_NODE=URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
RDFSLABEL_NODE=URIRef('http://www.w3.org/2000/01/rdf-schema#label')
RDFSCOMMENT_NODE=URIRef('http://www.w3.org/2000/01/rdf-schema#comment')
CONCEPT_NODE=URIRef('http://www.w3.org/2004/02/skos/core#Concept')
SCHEME_NODE=URIRef('http://www.w3.org/2004/02/skos/core#ConceptScheme')
COLLECTION_NODE=URIRef('http://www.w3.org/2004/02/skos/core#Collection')
DEFINITION_NODE=URIRef('http://www.w3.org/2004/02/skos/core#definition')
PREFLABEL_NODE=URIRef('http://www.w3.org/2004/02/skos/core#prefLabel')
NOTATION_NODE=URIRef('http://www.w3.org/2004/02/skos/core#notation')
HASTOPCONCEPT_NODE=URIRef('http://www.w3.org/2004/02/skos/core#hasTopConcept')
MEMBER=URIRef('http://www.w3.org/2004/02/skos/core#member')
OGC_URN_TYPE = URIRef('http://www.opengis.net/def/metamodel/URN')

GMX_MAP = { 'Dictionary': '//gmx:CodeListDictionary' ,
    'Definition' : '//gmx:CodeDefinition'}
GML32_MAP= { 'Dictionary': '//gml:Dictionary' ,
  'Definition' : '//gml:Definition'}
  
class GMLDict(ImportedConceptScheme):

    def save(self,*args,**kwargs):  
        #import pdb; pdb.set_trace()
        # save file - but doesnt parse it
        ImportedResource.save(self,*args,**kwargs)
        if self.file :
            tree = etree.parse(self.file.name)
        elif self.remote :
            tree = etree.parse(self.remote)
        if tree.getroot().nsmap.get('gmx') :
            map=GMX_MAP
        elif tree.getroot().nsmap.get('gml') == 'http://www.opengis.net/gml/3.2' :
            map=GML32_MAP
            
        self.savedgraph = self.extract_gmx_as_skos(tree, map)    
        scheme_obj = self.importSchemes(self.get_graph(),self.target_scheme, self.force_refresh)
            # update any references to imported schemes
            # print(self.schemes.all())

        # now SKOS imported should find graph as if parsed from RDF
        super(GMLDict, self).save(*args,**kwargs)

    pass
    
    class Meta:
        verbose_name ="GML Dictionary (XML)"
        verbose_name_plural = "GML Dictionaries"
        
    def extract_gmx_as_skos(self,tree,xpaths):
        """Extract a GML or GMX dictionary as a SKOS RDf model"""
        import pdb; pdb.set_trace()
        nsmap= { 'gml': 'http://www.opengis.net/gml/3.2'  , 'gmx' : 'http://www.isotc211.org/2005/gmx' }
        tgt = self.target_scheme
        if not tgt :
            # look for Dictionary element and get its identifier
            try:
                tgt = self.get_id(None,tree.getroot().xpath(xpaths['Dictionary'],namespaces=nsmap)[0], nsmap)
            except:
                try:
                    # use dfault namespace of XML document if set
                    tgt = tree.getroot().nsmap[None]
                except:
                    raise Exception("Cannot determine target namespace for Dictionary")
                    
            self.target_scheme = tgt
        uri = URIRef(tgt)    
        graph = None
        for codelist in tree.xpath(xpaths['Dictionary'],namespaces=nsmap):
            if not graph :
                graph = Graph()
                graph.namespace_manager.bind('skos', Namespace('http://www.w3.org/2004/02/skos/core#'), override=False)
            id = self.get_id(None,codelist,nsmap,needuri=False) 
 #           uri= URIRef( id ) 
 #           if not urlparse(id).scheme in ('http','https'):
 #               if not tgt.endswith(id):
 #                   uri = URIRef("/".join((tgt,id)) )
            graph.add ( (uri, RDFTYPE_NODE , SCHEME_NODE) )
            graph.add ( (uri, RDFSLABEL_NODE , Literal(id) ) )
            try:
                desc = codelist.xpath('./gml:description',namespaces=nsmap)[0].text
                graph.add ( (uri, DEFINITION_NODE , Literal(desc) ) )
            except:
                pass
            for code in codelist.xpath('./gml:identifier',namespaces=nsmap):
                    
                   graph.add ( (uri, NOTATION_NODE , Literal(code.text, datatype=OGC_URN_TYPE ) ) )
            for concept in codelist.xpath(xpaths['Definition'],namespaces=nsmap):
                id = self.get_id(str(uri),concept,nsmap)
                if not urlparse(id).scheme in ('http','https'):
                    id = "/".join((str(uri),id))
                duri = URIRef(id )
                graph.add ( (duri, RDFTYPE_NODE  , CONCEPT_NODE ) )
                try:
                    desc = concept.xpath('./gml:description',namespaces=nsmap)[0].text
                    graph.add ( (duri, DEFINITION_NODE , Literal(desc) ) )
                except:
                    pass
                try:
                    desc = concept.xpath('./gml:name',namespaces=nsmap)[0].text
                except:
                    desc = id
                graph.add ( (duri, RDFSLABEL_NODE , Literal(desc) ) )
            #print codelist.find('./gml:description',namespaces=nsmap).text
        return graph
       
    def get_id(self,uribase,node,nsmap, needuri=True): 
        """ Get id from gml:identifier if @codespace a valid HTTP namespace 
        
            revert to using gml:id if not possible
        """
        gmlid= node.xpath('./gml:identifier',namespaces=nsmap)
        if gmlid:
            id = gmlid[0].xpath('@codeSpace')[0]
            if not needuri or urlparse(id).scheme in ('http','https'):
                if not id[:-1] in '#/':
                    id = id +'/' 
                id = id + gmlid[0].text
                return id
        # FALL THROUGH TO FORCE USE OF GML:ID
        id = uribase
        if not id[:-1] in '#/':
            id = id +'/' 
        id = id + node.xpath('./@gml:id',namespaces=nsmap)[0]
        return id
        