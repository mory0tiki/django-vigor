'''
Created on May 17, 2014

@author: morteza
'''
import json
import logging
from string import upper, lower

from django.core.files import File 
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.db.models import Q
from django.http.response import HttpResponse, Http404
from django.middleware.csrf import get_token
from django.template.base import TemplateDoesNotExist
from django.views.generic import base
from django.views.generic.base import TemplateView
from rest_framework.renderers import JSONRenderer

from django.conf import settings
from vigor.generic.utils.file import save_file_to_temp
from vigor.generic.utils.http import JsonResponseStruct, render_post_params
from vigor.generic.utils.util import get_column_name


class View(base.View):
    """
    this class add action property to django View class.
    so you can map a url to a class-based view and 
    specified to use specific method to all for this url.
    e.g.:
        url(r'^Core/$', CoreView.as_view(action='test'))
    you have to have a method in your class that it's name is 'test'
    """
    # Can use this attribute to mention that dispatcher use this method to response.
    action = None;

    def initResponse(self):
        pass;

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names and not self.action:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        elif self.action:
            handler = getattr(self, self.action, self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed

        # Reset response variable
        self.initResponse()
        return handler(request, *args, **kwargs)


class CrudBasicView(View):
    '''
    BasicView
    
    we use this class to generalize django View generic view in out project
    
    To validate your data befor saving them you should override validate method of this class
    '''
    name = None
    model = None
    serializer = None
    serializerFilter = Q(id__isnull=False)
    putModelField = []
    getModelField = []
    postModelField = []
    listModelField = []
    fileModelField = []

    callbackUrl = {
                   'post' : '',
                   'put' : '',
                   'get' : '',
                   'delete' : ''
    }

    response = JsonResponseStruct()

    # Re-initialize response variable in each request
    # to clear previews data.
    def initResponse(self):
        self.response = JsonResponseStruct();
        self.response.hasError = True;
        self.response.message = "REQUEST_IS_NOT_VALID";

    def put(self, request, id, *args, **kwargs):

        try:
            data = render_post_params(request);
            if data and id:
                obj = self.model.objects.get(id=id)
                if obj:
                    if len(self.putModelField) > 0:
                        for field in self.putModelField:
                            if hasattr(obj, field) and (field in data):
                                column = get_column_name(self.model, field)
                                setattr(obj, column, File(open(save_file_to_temp(data[field]), 'r'))) if field in self.fileModelField else setattr(obj, column, data[field])
                        if self.validate(data, obj=obj):
                            obj.save()
                            self.response.hasError = False
                            self.response.message = upper(self.name) + "_UPDATED_SUCCESSFULLY";
                else:
                    self.response.message = upper(self.name) + "_IS_NOT_EXIST";

        except Exception, ex:
            self.response.extraMessage = str(ex);
            self.response.message = upper(self.name) + "_EDIT_FAILD";

        return HttpResponse(self.response);

    def delete(self, request, id, *args, **kwargs):

        try:
            if id:
                obj = self.model.objects.get(id=id);
                if obj:
                    obj.delete();
                    self.response.errorCode = 200;
                    self.response.hasError = False;
                    self.response.message = upper(self.name) + "_DELETED_SUCCESSFULLY";
                else:
                    self.response.message = upper(self.name) + "_IS_NOT_EXIST"
        except Exception, ex:
            self.response.extraMessage = str(ex);
            self.response.message = upper(self.name) + "_DELETE_FAILD";

        return HttpResponse(self.response);

    def post(self, request, *args, **kwargs):

        try:
            data = render_post_params(request);
            if data:
                obj = self.model();
                if len(self.postModelField) > 0:
                    for field in self.postModelField:
                        column = get_column_name(self.model, field)
                        if hasattr(obj, column) and (field in data):
                            setattr(obj, column, save_file_to_temp(data[field])) if field in self.fileModelField else setattr(obj, column, data[field])
                    if self.validate(data, obj=obj):
                        obj.save();
                        self.response.message = upper(self.name) + "_ADDED_SUCCESSFULLY"
                        if self.callbackUrl and self.callbackUrl.has_key('post'):
                            self.response.callbackUrl = self.callbackUrl['post'] + str(obj.id);
                        self.response.hasError = False;

        except Exception, ex:
            self.response.extraMessage = unicode(ex);
            self.response.message = upper(self.name) + "_ADD_FAILD";

        return HttpResponse(self.response);

    def pre_read(self, request, id, *args, **kwargs):
        """
        """
        return True

    def post_read(self, request, id, *args, **kwargs):
        """
        """
        return True

    def get(self, request, id=0, *args, **kwargs):

        try:
            self.response = JsonResponseStruct()
            self.pre_read(request, id, *args, **kwargs)
            if id:
                obj = self.model.objects.filter(self.serializerFilter).get(id=id)

                if obj:
                    objSerializer = self.serializer(obj);
                    self.response.data = json.loads(JSONRenderer().render(objSerializer.data));
                    self.response.hasError = False;
                    self.response.errorCode = 200;
                    self.response.message = "";
            else:
                objs = self.model.objects.filter(self.serializerFilter)
                paginator = Paginator(objs, settings.PAGE_ROW_NO)
                pageNo = request.GET.get('page');

                try:
                    page = paginator.page(pageNo);
                except PageNotAnInteger:
                    page = paginator.page(1);
                except EmptyPage:
                    page = paginator.page(paginator.num_pages);

                # if objs:
                objsSerializer = self.serializer(page, many=True);
                self.response.data = json.loads(JSONRenderer().render(objsSerializer.data));
                self.response.hasError = False;
                self.response.errorCode = 200;
                self.response.message = "";
            # else:
            #                     raise Exception(upper(self.name) + "_IS_NOT_EXIST");
            self.post_read(request, id, *args, **kwargs)
        except Exception as ex:
            self.response.extraMessage = unicode(ex)
            self.response.message = upper(self.name) + "_READ_FAILD";
        return HttpResponse(self.response);

    def validate(self, data, *args, **kwargs):
        """
        This method is called before save action in this class,
        so if you want to validate your data before saving it,
        you should override this method and put your validation in it.
        """
        return True
    
    
class StaticView(TemplateView):
    '''
    A class-base view that handles for serving static html files 
    
    Keyword arguments:
    page -- name of the page that client wants to load
    '''
    
    
    #application template path
    template_path = '';
    
    auth_required = {'GET': {'login_required' : settings.LOGIN_REQUIRED, 'permissions' : []}};
    logger = logging.getLoggerClass();
    
    def get(self, request, page='index', *args, **kwargs):
        self.createPermissionList(page);
        access = self.checkAuth(request);
        if access:
            return access;
        self.template_name = '%s/%s.html' % (self.template_path, page); #'index.html' if page == 'index' else 'CAuth/%s.html' % (page)
        csrfToken = get_token(request);
        response = super(StaticView, self).get(request, *args, **kwargs)
        # FIXME we have to read site language from db
        response.set_cookie('lang', 'fa-ir');
        response.set_cookie('debug', settings.DEBUG);
        try:
            return response.render()
        except TemplateDoesNotExist:
            raise Http404()
        
    """
    If you want to check permissions of the logged in user to
    load the html page, override this method in your app and check appropriate permissions. 
    """
    def createPermissionList(self, page):
        pass;

class BasicViewRelatives(View):
    """
    If your model has foreign key to another model and you want to
    get records from that model that are related to your model, 
    you can use this class to get list of records in JSON structure .
     
     You should add a url pattern like below:
         ^xxx/(?P<id>\[^/]+)/(?P<model_name>)\w+)/$
     and add a function as below to the class that is inherit from BaseViewRelatives 
         get_[lower case of model_name](self, foreign_key_id, page_no)
    """
    
    name = ''
    
    def get(self, request, id, model_name, *args, **kwargs):
        response = JsonResponseStruct()
        try:
            if hasattr(self, 'get_' + lower(model_name)):
                func = getattr(self, 'get_' + lower(model_name))
                records = func(id, request.GET.get('page'))
                response.data = json.loads(records)
                response.hasError = False
                response.errorCode = 200
                response.message = ""
    
        except Exception as ex:
            response.extraMessage = unicode(ex)
            response.message =  "%s_%s_READ_FAILD" % (self.name, model_name)
        return HttpResponse(response)
    
    def post(self, request, id, model_name, *args, **kwargs):
        response = JsonResponseStruct()
        try:
            if hasattr(self, 'post_' + lower(model_name)):
                func = getattr(self, 'post_' + lower(model_name))
                func(request, id)
                response.hasError = False
                response.errorCode = 200
                response.message  = "" 
        except Exception as ex:
            response.extraMessage = unicode(ex)
            response.message =  "%s_%s_ADDING_FAILD" % (self.name, model_name)
        
        return HttpResponse(response)
    
    def delete(self, request, id, model_name, *args, **kwargs):
        response = JsonResponseStruct()
        try:
            if hasattr(self, 'delete_' + lower(model_name)):
                func = getattr(self, 'delete_' + lower(model_name))
                func(request, id)
                response.hasError = False
                response.errorCode = 200
                response.message  = "%s_%s_DELETING_SUCCESSFULLY" % (self.name, model_name)
        except Exception as ex:
            response.extraMessage = unicode(ex)
            response.message =  "%s_%s_DELETING_FAILD" % (self.name, model_name)
        
        return HttpResponse(response)
