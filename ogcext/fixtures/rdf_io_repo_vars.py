# Sets config vars for an inferencing chain for SKOS and RDF4J
from __future__ import unicode_literals

from django.conf import settings
import django.db.models.deletion
import django_extensions.db.fields
import rdf_io.models


from rdf_io.models import ConfigVar 
from django.contrib.contenttypes.models import ContentType

def loaddata(url_base):
    config,created = ConfigVar.objects.update_or_create(var='APPSCHEMAINFER',defaults={'value':'appschema_inferencer'})
    return ( {'configs': '3 vars set'} )
