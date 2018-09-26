#-*- coding:utf-8 -*-
from django.contrib import admin
from ogc.models import GMLDict
from skosxl.admin import *
from django.utils.translation import ugettext_lazy as _


class GMLDictAdmin(ImportedConceptSchemeAdmin):
    pass
        
admin.site.register(GMLDict, GMLDictAdmin)

