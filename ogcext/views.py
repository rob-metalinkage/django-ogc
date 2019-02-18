# # -*- coding:utf-8 -*-
from django.shortcuts import render_to_response, redirect
from skosxl.models import *
from django.template import RequestContext
from django.shortcuts import get_object_or_404
# deprecated since 1.3
# from django.views.generic.list_detail import object_list
# but not used anyway?
# if needed.. from django.views.generic import ListView

from django.http import HttpResponse
import json



from importlib import import_module


def loadinit(req) :
    """
        ought to move this to rdf_io, and put in a module register process that triggers these for all modules rdf_io knows about
    """
    messages = {}
    if req.GET.get('pdb') :
        import pdb; pdb.set_trace()
    url_base = req.build_absolute_uri("/");
    loadlist = import_module('ogcext.fixtures.loadlist', 'ogcext.fixtures')
    for cfgname in loadlist.INITIAL_FIXTURES :
        cm = import_module("".join(('ogcext.fixtures.',cfgname)), 'dataweb.fixtures')
        messages.update( cm.loaddata(url_base) )
    return HttpResponse("loaded configurations:" + str(messages))  


