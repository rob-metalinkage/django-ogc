#-*- coding:utf-8 -*-
from django.conf.urls import url
from django.contrib import admin
from rdf_io.admin import ImportedResourceAdmin
# from rdf_io.models import ConfigVar,TYPE_MODEL,ServiceBinding
from rdf_io.models import ConfigVar, ServiceBinding
from rdf_io.views import *
from skosxl.admin import *

from ogcext.models import *
from ogcext.models import AppSchema
from ogcext.views import loaddocreg


#
# something like this should have allowed smuggler function to be visible on admin site.... but no joy :-(
#
# from uriredirect.models import RewriteRule

# class DummyModel2(RewriteRule):
 
	# class Meta:
		# verbose_name_plural = 'Dump URI redirect rules to JSON'
		# app_label = 'uriredirect'
        # proxy = True
        
# class DumpURIredirectAdmin(admin.ModelAdmin):
    # change_list_template = 'smuggler/change_list.html'
    # def get_urlsx(self):
        # view_name = '{}_{}_changelist'.format(
            # self.model._meta.app_label, self.model._meta.model_name)
        # return [ url('dump/' ,  self.admin_site.admin_view(dump_app_data) ) , ]

# admin.site.register(DummyModel2, DumpURIredirectAdmin)

class DummyModel(models.Model):
 
	class Meta:
		verbose_name_plural = 'Doc Register Loader'
		app_label = 'ogcext'
        
class UtilitiesAdmin(admin.ModelAdmin):
    def get_urls(self):
        view_name = '{}_{}_changelist'.format(
            self.model._meta.app_label, self.model._meta.model_name)
        return [ url(r'manage/' ,  loaddocreg ,name=view_name) ,  ]

admin.site.register(DummyModel, UtilitiesAdmin)


        
class AppSchemaAdmin(ImportedResourceAdmin):
    resourcetype = 'appschema'
    def get_changeform_initial_data(self, request):
        defaults= {'resource_type': TYPE_MODEL}
        try:
            defaults['graph'] = ConfigVar.objects.get(var='APPSCHEMA_BASE').value
        except:
            pass
        try:
            # import pdb; pdb.set_trace()
            defaults['target_repo'] = ServiceBinding.objects.get(title='APPSCHEMA load source to inferencer')
        except:
            pass
        return defaults
    
    def get_queryset(self, request):
        #qs = super(AppSchemaAdmin, self).get_queryset(request)
        # import pdb; pdb.set_trace()
        return  AppSchema.objects.all() # App.filter(Q(subtype=ContentType.objects.get_for_model(AppSchema) ))   


        
admin.site.register(AppSchema, AppSchemaAdmin)


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