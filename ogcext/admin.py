#-*- coding:utf-8 -*-
from django.contrib import admin
from ogcext.models import *
from skosxl.admin import *
from django.utils.translation import ugettext_lazy as _
from ogcext.views import loaddocreg, loadinit
from ogcext.models import AppSchema
from django.conf.urls import url, include
from smuggler.views import dump_app_data, dump_data, dump_model_data, load_data

from rdf_io.views import *
#from rdf_io.models import ConfigVar,TYPE_MODEL,ServiceBinding
from rdf_io.models import ConfigVar,ServiceBinding
from rdf_io.admin import ImportedResourceAdmin,  publish_set_action
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
    actions= ['publish_options', ]

    def get_changeform_initial_data(self, request):
        defaults= {'resource_type': TYPE_MODEL}
        try:
            defaults['graph'] = ConfigVar.objects.get(var='APPSCHEMA_BASE').value
        except:
            pass
        try:
            # import pdb; pdb.set_trace()
            defaults['target_repo'] = ServiceBinding.objects.get(title='AppSchema inferencing')
        except:
            pass
        return defaults
    
    def get_queryset(self, request):
        #qs = super(AppSchemaAdmin, self).get_queryset(request)
        # import pdb; pdb.set_trace()
        return  AppSchema.objects.all() # App.filter(Q(subtype=ContentType.objects.get_for_model(AppSchema) ))   

    def publish_options(self,request,queryset):
        """Batch publish with a set of mode options"""
        if 'apply' in request.POST:
            # The user clicked submit on the intermediate form.
            # Perform our update action:
            if request.POST.get('mode') == "CANCEL" :
                self.message_user(request,
                              "Cancelled publish action")
            else:
                checkuri = 'checkuri' in request.POST
                logfile= publish_set_action(queryset,'appschema',check=checkuri,mode=request.POST.get('mode'))
                self.message_user(request,
                              mark_safe('started publishing in {} mode for {} schemes at <A HREF="{}" target="_log">{}</A>'.format(request.POST.get('mode'),queryset.count(),logfile,logfile) ) )
            return HttpResponseRedirect(request.get_full_path())
        return render(request,
                      'admin/admin_publish.html',
                      context={'schemes':queryset, 
                        'pubvars': ConfigVar.getvars('PUBLISH') ,
                        'reviewvars': ConfigVar.getvars('REVIEW') ,
                        })

        
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