# -*- coding: utf-8 -*-

from django.db import models

from skosxl.models import *

try:
    from django.utils.encoding import python_2_unicode_compatible
except:
    from six import python_2_unicode_compatible
    
from django.utils.translation import ugettext_lazy as _
from rdf_io.models import ImportedResource

try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen


import logging
logger = logging.getLogger(__name__)
  
try:
    # python 3
    from urllib.parse import urlparse

except ImportError:
    from urlparse import urlparse
#   from urllib.request import urlopen
    
from lxml import etree
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

class AppSchema(ImportedResource):
    verbose_name = 'Application Schema'

  
class SensorParameter(Concept):
    """ A sensor parameter is measured by a sensor type.
    
    This may be referenced by either an "observation procedure" or an "observed property". Parameters may be organised into generalisation hierarchies. Uses unadorned SKOS model, but may be extended later, for example to define UoM, precision etc. """
    
    class Meta :
        verbose_name="Sensed Parameter"
        verbose_name_plural="Sensed Parameters"
        
        
class SensorModel(Concept):
    class Meta :
        verbose_name="Sensor Model"
        verbose_name_plural="Sensor Models"
    
    senses = models.ManyToManyField( "sensorparameter",symmetrical=False,
        verbose_name=(_('parameters sensed')),
        help_text=_('References observable parameters sensed by this sensor. This should be the most specific reference available, allowing inferencing to identify the more general terms relevant to this parameter'))

class SensorModelSource(ImportedConceptScheme):
    class Meta :
        verbose_name='sensor model register'
  
    def save(self,*args,**kwargs):  
        # save first - to make file available
 
        if not self.force_bulk_only :
            target_repo = self.target_repo
            self.target_repo = None
            super(SensorModelSource, self).save(*args,**kwargs)
            self.target_repo = target_repo
        else:
            super(SensorModelSource, self).save(*args,**kwargs)
        parsedRDF = self.get_graph()
        # import the basic SKOS elements of the scheme using the era subclasses
        # def importScheme(self,gr, target_scheme,  force_refresh, schemegraph, schemeClass=Scheme, conceptClass=Concept,schemeDefaults={}, classDefaults={} ):
    
        scheme_objs_found = self.importSchemes(parsedRDF,self.target_scheme, self.force_refresh, schemeClass=Scheme, conceptClass=SensorModel, schemeDefaults={})
        # now process the specialised extension elements
        for scheme_obj in scheme_objs_found:
            self.getParams(scheme_obj,parsedRDF)
        
    def getParams(self, scheme_obj, gr):
        for c in self.getConcepts(URIRef(scheme_obj.uri),gr):
            try:
                sensor = SensorModel.objects.get(uri=str(c))
                #sensor.save()
            except Exception as e:
                logger.info ("Could not process parameters sensed by sensor %s , %s " % (c,e))

class SensorParameterSource(ImportedConceptScheme):
    class Meta :
        verbose_name='sensor parameter register'
  
    def save(self,*args,**kwargs):  
        # save first - to make file available
 
        if not self.force_bulk_only :
            target_repo = self.target_repo
            self.target_repo = None
            super(SensorParameterSource, self).save(*args,**kwargs)
            self.target_repo = target_repo
        else:
            super(SensorParameterSource, self).save(*args,**kwargs)
        parsedRDF = self.get_graph()
        # import the basic SKOS elements of the scheme using the era subclasses
        # def importScheme(self,gr, target_scheme,  force_refresh, schemegraph, schemeClass=Scheme, conceptClass=Concept,schemeDefaults={}, classDefaults={} ):
    
        scheme_objs_found = self.importSchemes(parsedRDF,self.target_scheme, self.force_refresh, schemeClass=Scheme, conceptClass=SensorParameter, schemeDefaults={})
        # now process the specialised extension elements
        for scheme_obj in scheme_objs_found:
            self.getParams(scheme_obj,parsedRDF)
        
    def getParams(self, scheme_obj, gr):
        for c in self.getConcepts(URIRef(scheme_obj.uri),gr):
            try:
                param = SensorParameter.objects.get(uri=str(c))
                #sensor.save()
            except Exception as e:
                logger.info ("Could not process parameters sensed by sensor %s , %s " % (c,e))

                
                
class GMLDict(ImportedConceptScheme):

    def __unicode__(self):
        return ( ' '.join( filter(None,('GMLDict:', self.description, '<',self.remote, str(self.file), '>' ))))
        
    def save(self,*args,**kwargs):  
        #import pdb; pdb.set_trace()
        # save file - but doesnt parse it
#        super(GMLDict, self).save(*args,**kwargs)
        ImportedResource.save(self,*args,**kwargs)
        if self.file :
            tree = etree.parse(self.file.name)
        elif self.remote :
            f = urlopen(self.remote)
            tree = etree.parse(f)
        if tree.getroot().nsmap.get('gmx') :
            map=GMX_MAP
        elif tree.getroot().nsmap.get('gml') == 'http://www.opengis.net/gml/3.2' :
            map=GML32_MAP
            
        self.savedgraph = self.extract_gmx_as_skos(tree, map)    
        scheme_obj = self.importSchemes(self.get_graph(),self.target_scheme, self.force_refresh)
            # update any references to imported schemes
            # logger.info(self.schemes.all())

        # now SKOS imported should find graph as if parsed from RDF
        kwargs['force_insert']=False
        super(GMLDict, self).save(*args,**kwargs)

    pass
    
    class Meta:
        verbose_name ="GML Dictionary (XML)"
        verbose_name_plural = "GML Dictionaries"
        
    def extract_gmx_as_skos(self,tree,xpaths):
        """Extract a GML or GMX dictionary as a SKOS RDf model"""
        # import pdb; pdb.set_trace()
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
            #logger.info codelist.find('./gml:description',namespaces=nsmap).text
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
        