'''
Created on Sep 15, 2014

@author: morteza
'''

class Colorify(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    
    @staticmethod
    def warning(msg):
        return Colorify.WARNING + msg + Colorify.ENDC
    
    @staticmethod
    def fail(msg):
        return Colorify.FAIL + msg + Colorify.ENDC
        