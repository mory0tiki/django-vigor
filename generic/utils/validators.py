'''
Created on Sep 12, 2014

@author: morteza
'''
from django.core.validators import RegexValidator

def phone_validator(value):
        
        RegexValidator(regex = '1?\W*([2-9][0-8][0-9])\W*([2-9][0-9]{2})\W*([0-9]{4})(\se?x?t?(\d*))?',
                                   message = 'Enter valid phone number',
                                                      code = 'invalid_phone_number')
