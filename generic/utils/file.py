'''
Created on Sep 1, 2014

@author: morteza
'''
import base64
from os import path
from uuid import uuid4

from django.conf.settings import TEMP_DIR


def save_file_to_temp(data, *args, **kwargs):
    try:
        image = data.split(',')[1];
        if image:
            image_decoded = base64.b64decode(image);
            file_name = path.join(TEMP_DIR, str(uuid4()));
            file_obj = open(file_name, 'wb');
            file_obj.write(image_decoded);
            file_obj.close();
    except Exception as ex:
        file_name = None;
    
    return file_name;
