'''
Created on Sep 5, 2014

@author: morteza
'''
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
import json



def load_translation_file():
    try:
        trans = open(settings.STATICFILES_DIRS[0] + ("/translations/translate_%s.json" % (settings.LANGUAGE_CODE)))
        return json.load(trans);
    except Exception as ex:
#         logger.error(str(ex));
        print str(ex)
        raise

def get_model_colums(model, excluded_fields = []):
    return [x.column for x in model._meta.fields if x.column not in excluded_fields]

def get_model_fields(model, excluded_fields = []):
    return [x.name for x in model._meta.fields if x.name not in excluded_fields]

def get_model_m2m_fields(model):
    return [x.column for x in model._meta.many_to_manys]


def get_related_model(model):
    """
        returns all one-to-many related models of the model

        return: a dict with model's name as key 
    """
    related_models = {}
    try:
        for field in model._meta.fields:
            if field.get_internal_type() == 'ForeignKey':
                rel = field.rel.to
                related_models[rel._meta.model_name] = rel
    except Exception as ex:
        raise ex
    return related_models


def get_column_name(model, field):
    tmp = [x.column for x in model._meta.fields if x.name == field or x.column == field]
    if tmp:
        return tmp[0]
    elif hasattr(model(), field):
        return field
        

def pagination (query_set, records_per_page, page_no):
    
    paginator = Paginator(query_set, records_per_page)
    
    try:
        page = paginator.page(page_no)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    
    return page

def validate_request_data(data, key_list, *args, **kwargs):
    for k in key_list:
        if not data.has_key(k):
            raise Exception(load_translation_file('VALUE_NOT_EXIST' % (k)))   


class HashKeyGenerator:
    '''
    This class is used to create a sha key 
    from username
    '''
    
    import logging
    
    logger = logging.getLogger();
    def generateKey(self, inputStr):
        import random, sha
        
        try:
            salt = sha.new(str(random.random())).hexdigest()[:5]
            activation_key = sha.new(salt+inputStr).hexdigest();
        except Exception as ex:
#             self.logger.error(str(ex));
            return None;
        return activation_key


