# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
import sys
from os.path import dirname

def log(msg, level='CRITICAL'):
    now = time.strftime("%Y-%m-%dT%H:%M:%S "+level+ " : ")
    saveout = sys.stdout
    fsock = open(dirname(__file__) + r'\out.log', 'a')
    sys.stdout = fsock
    print now + encode(msg)
    sys.stdout = saveout
    fsock.close()
            
def encode(value):
    return unicode(value).encode('utf8') if value else None

def decode(value):
    try:
        return value.decode('utf8') if value else None
    except UnicodeDecodeError, err:
        msg = "Problème d'encodage :\n"
        msg += "Les référentiels doivent être encodés en Unicode (UTF8)"
        popup(msg)
        
class Singleton():
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.
        """
        
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


