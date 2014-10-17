'''
Created on Sep 1, 2014

@author: morteza
'''
import json
import ast


class JsonResponseStruct:
    '''
    We use this class to generalization json responses
    __repr__ function of this class return json string by default so you can pass the class without serialization to HttpResponse.
    
    '''
    def __init__(self):
        self.hasError= True
        self.errorCode = 500
        self.message= None
        self.extraMessage= None
        self.data = None
        self.pagination = {
                'total_rows': 0,    # Total rows of records
                'first_index': 0,   # index of first row of current page
                'last_index': 0,    # index of last row of current page
                'num_pages': 0,     # number of pages
                'current_page': 0,  # index of current page
                }
        self.callbackUrl = None
        
    def __repr__(self):
        return json.dumps(self.__dict__)

def render_post_params(request, *args, **kwargs):
        result = None
        try:
            print request.body
            result = ast.literal_eval(request.body)

#            if request.is_ajax() or request.method != "POST":
#                result = ast.literal_eval(request.body)["data"]
#            else:
#                if request.method == "POST":
#                    result = request.POST.dict()#ast.literal_eval(str(request.POST.dict()))
#                    print result
        except Exception as ex:
            print ex
            return None
        return result
   

try:
        from django.utils.encoding import smart_unicode as smart_text
except ImportError:
        from django.utils.encoding import smart_text
import re
import unicodedata
def slugify(value):
    #underscore, tilde and hyphen are alowed in slugs
    value = unicodedata.normalize('NFKC', smart_text(value))
    prog = re.compile(r'[^~\w\s-]', flags=re.UNICODE)
    value = prog.sub('', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)
