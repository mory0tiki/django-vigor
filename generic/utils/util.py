'''
Created on Sep 5, 2014

@author: morteza
'''
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
def get_model_colums(model, excluded_fields = []):
    return [x.column for x in model._meta.fields if x.column not in excluded_fields]

def get_model_fields(model, excluded_fields = []):
    return [x.name for x in model._meta.fields if x.name not in excluded_fields]

def get_model_m2m_fields(model):
    return [x.column for x in model._meta.many_to_manys]

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

