
from rdf_io.models import Namespace, ObjectType,ObjectMapping,AttributeMapping , ChainedMapping 
from django.contrib.contenttypes.models import ContentType
from skosxl.models import Scheme



def loaddata(url_base):
    """
    run loading for module
    """
    load_base_namespaces(url_base)
    load_rdf_mappings(url_base)
    return ( {'ogcext': 'OGC specific object mappings'} )
    
def load_base_namespaces(url_base):
    """
        load namespaces for the meta model
    """
    Namespace.objects.get_or_create( uri='http://www.opengis.net/def/metamodel/', defaults = { 'prefix' : 'ogc' , 'notes': 'OGC defined object types' } )

 
    Namespace.objects.get_or_create( uri='http://www.opengis.net/def/metamodel/lid/', defaults = { 'prefix' : 'lid' , 'notes': 'LID - allows characterisation of resources such as VoiD:technicalFeatures against Linked Data API view names' } )
    print "loading base namespaces for OGC EXT"
    
def load_urirules(url_base) :
    """
        Load uriredirect rules for these object types.
    """
    pass

def load_rdf_mappings(url_base):
    """
        load RDF mappings for SKOS XL Objects
    """
    
    (object_type,created) = ObjectType.objects.get_or_create(uri="ogc:ApplicationSchema", defaults = { "label" : "Application Schema" })
    import pdb; pdb.set_trace()
    sm = ObjectMapping.new_mapping(object_type, "rdf_io:ImportedResource", "AppSchema", "graph", "graph" , filter='resource_type="CLASS"' , auto_push=False)
    # specific mapping
    am = AttributeMapping(scope=sm, attr="description", predicate="rdfs:comment", is_resource=False).save()
    am = AttributeMapping(scope=sm, attr="graph", predicate="ogc:sourceGraph", is_resource=True).save()
    am = AttributeMapping(scope=sm, attr="metaprops.value", predicate=":metaprops.metaprop", is_resource=False).save()


 
