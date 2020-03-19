#-*- coding:utf-8 -*-
from django.contrib import admin
from ogcext.models import *
from skosxl.admin import *
from django.utils.translation import ugettext_lazy as _
from ogcext.views import loaddocreg, loadinit
from django.conf.urls import url, include
from smuggler.views import dump_app_data, dump_data, dump_model_data, load_data


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