'''
Created on 14 Oct 2019

@author: u76345
'''
import logging
from .ld_entity import LDEntity, FilterTriple

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # Initial logging level for this module
logger.debug('__name__ = {}'.format(__name__))


class ConceptLDEntity(LDEntity):
    '''
    LDEntity subclass for skos:concept Linked Data entities
    '''
    _rdf_type = 'skos:Concept'
    
    _default_prefixes = {}

    def __init__(self, ld_source, debug=False):
        '''
        LDEntity Constructor
        '''
        _prefixes = None
        
        super().__init__(ld_source, debug)        
    
    def get_entities(self):
        '''
        Function to get all skos:Concepts
        '''
        filter_triple_list = [FilterTriple(None, 'rdf:type', self.rdf_type),
                              ]
        return super().get_entities(filter_triple_list=filter_triple_list,
                             prefixes = self.prefixes
                             )
        
    def get_entity_details(self, entity_uri, filter_triple_list=[]):
        '''
        '''
        return self.ld_source.get_entities(entity_uri=entity_uri, 
                                           filter_triple_list=filter_triple_list + [FilterTriple(None, 'rdf:type', self.rdf_type)],
                                           prefixes = self.prefixes
                                           )
        

