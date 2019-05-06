#-*- coding:utf-8 -*-
from django.contrib import admin
from ogcext.models import *
from skosxl.admin import *
from django.utils.translation import ugettext_lazy as _


class GMLDictAdmin(ImportedConceptSchemeAdmin):
    pass
        
admin.site.register(GMLDict, GMLDictAdmin)

class SensorModelSourceAdmin(ImportedConceptSchemeAdmin):
    pass
        
admin.site.register(SensorModelSource, SensorModelSourceAdmin)

class SensorParameterSourceAdmin(ImportedConceptSchemeAdmin):
    pass
        
admin.site.register(SensorParameterSource, SensorParameterSourceAdmin)

class SensorModelAdmin(ConceptAdmin):
    pass
        
admin.site.register(SensorModel, SensorModelAdmin)

class SensorParameterAdmin(ConceptAdmin):
    pass
        
admin.site.register(SensorParameter, SensorParameterAdmin)