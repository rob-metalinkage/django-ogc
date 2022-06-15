# Sets config vars for an inferencing chain for SKOS and RDF4J
from __future__ import unicode_literals

from rdf_io.models import ConfigVar


def loaddata(url_base):
    config,created = ConfigVar.objects.update_or_create(var='APPSCHEMAINFER',defaults={'value':'appschema_inferencer'})
    return ( {'configs': '3 vars set'} )
