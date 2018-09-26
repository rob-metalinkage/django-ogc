# -*- coding: utf-8 -*-

from django.db import models

from skosxl.models import *

from django.utils.encoding import python_2_unicode_compatible

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


class GMLDict(ImportedConceptScheme):

    def save(self,*args,**kwargs):  
        #import pdb; pdb.set_trace()
        # save file - but doesnt parse it
        ImportedResource.save(self,*args,**kwargs)
        if self.file :
            tree = etree.parse(self.file.name)
        elif self.remote :
            tree = etree.parse(self.remote)
        self.savedgraph = self.extract_gmx_as_skos(tree)
        scheme_obj = self.importSchemes(self.get_graph(),self.target_scheme, self.force_refresh)
            # update any references to imported schemes
            # print(self.schemes.all())

        # now SKOS imported should find graph as if parsed from RDF
        super(GMLDict, self).save(*args,**kwargs)

    pass
    
    def extract_gmx_as_skos(self,tree):
        nsmap= { 'gml': 'http://www.opengis.net/gml/3.2'  , 'gmx' : 'http://www.isotc211.org/2005/gmx' }
        tgt = self.target_scheme
        if not tgt :
            tgt = tree.getroot().nsmap[None]
            self.target_scheme = tgt
        uri = URIRef(tgt)
        graph = None
        for codelist in tree.xpath('//gmx:CodeListDictionary',namespaces=nsmap):
            if not graph :
                graph = Graph()
                graph.namespace_manager.bind('skos', Namespace('http://www.w3.org/2004/02/skos/core#'), override=False)
            id = codelist.xpath('./@gml:id',namespaces=nsmap)[0]
            if not tgt.endswith(id):
                uri = URIRef("/".join((tgt,id)) )
            graph.add ( (uri, RDFTYPE_NODE , SCHEME_NODE) )
            graph.add ( (uri, RDFSLABEL_NODE , Literal(id) ) )
            desc = codelist.xpath('./gml:description',namespaces=nsmap)[0].text
            graph.add ( (uri, DEFINITION_NODE , Literal(desc) ) )
            for code in codelist.xpath('./gml:identifier',namespaces=nsmap):
                   graph.add ( (uri, NOTATION_NODE , Literal(code.text, datatype=OGC_URN_TYPE ) ) )
            for concept in codelist.xpath('//gmx:CodeDefinition',namespaces=nsmap):
                id = concept.xpath('./@gml:id',namespaces=nsmap)[0]
                duri = URIRef("/".join((uri,id)) )
                graph.add ( (duri, RDFTYPE_NODE  , CONCEPT_NODE ) )
                desc = concept.xpath('./gml:description',namespaces=nsmap)[0].text
                graph.add ( (duri, DEFINITION_NODE , Literal(desc) ) )
            #print codelist.find('./gml:description',namespaces=nsmap).text
        return graph