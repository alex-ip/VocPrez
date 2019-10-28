'''
Created on 14 Oct 2019

@author: u76345
'''
import abc
import logging
from pprint import pformat
from .ld_entity import LDEntity, FilterTriple

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # Initial logging level for this module
logger.debug('__name__ = {}'.format(__name__))


class LDSourceException(BaseException):
    '''
    Custom Exception class for class LDSource
    '''

class LDSource(object):
    '''
    Abstract base class for all Linked Data sources
    '''
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def __init__(self, debug=False):
        '''
        LDSource Constructor
        '''
        # Initialise and set debug property
        self._debug = None
        self.debug = debug
        
    
    @abc.abstractmethod
    def get_entities(self, filter_triple_list=[], prefixes=None):
        '''
        '''
        return
        
    @abc.abstractmethod
    def get_entity_details(self, entity_uri, prefixes=None):
        '''
        '''
        return
        

