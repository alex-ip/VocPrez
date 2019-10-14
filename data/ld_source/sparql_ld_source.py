'''
Created on 14 Oct 2019

@author: u76345
'''
import abc
import logging
from pprint import pformat
from ._ld_source import LDSource

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # Initial logging level for this module
logger.debug('__name__ = {}'.format(__name__))


class SPARQLLDSource(LDSource):
    '''
    Abstract base class for all Linked Data sources
    '''
    def __init__(self, debug=False):
        '''
        LDSource Constructor
        '''
        super().__init__(debug=debug)
        
    
    def get_entities(self, filter_triple_list=[], prefixes=None):
        '''
        '''
        return
        
    def get_entity_details(self, entity_uri, prefixes=None):
        '''
        '''
        return
        

