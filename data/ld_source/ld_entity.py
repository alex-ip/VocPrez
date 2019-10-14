'''
Created on 14 Oct 2019

@author: u76345
'''
import abc
import logging
import os
import sys
from glob import glob
import re
import inspect
from importlib import import_module
from pprint import pformat

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # Initial logging level for this module
logger.debug('__name__ = {}'.format(__name__))


class FilterTriple(object):
    '''
    Class to manage a single filter triple, with None for unknowns
    '''
    def __init__(self, triple_subject=None, triple_predicate=None, triple_object=None, invert_match=False):
        '''
        Constructor for class FilterTriple
        '''
        self.subject = triple_subject
        self.predicate = triple_predicate
        self.object = triple_object
        self.invert_match = invert_match
        assert self.predicate and (self.subject or self.object) and not (self.subject and self.object), 'Must specify predicate and either subject or object for filtering' 

class LDEntityException(BaseException):
    '''
    Custom Exception class for class LDEntity
    '''

class LDEntity(object):
    '''
    Abstract base class for all Linked Data entities
    '''
    __metaclass__ = abc.ABCMeta
    
    _rdf_type = None # This property must be set by subclasses
    
    _subclasses = {}
    
    _default_prefixes = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'skos': 'http://www.w3.org/2004/02/skos/core#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'dct': 'http://purl.org/dc/terms/',
        'owl': 'http://www.w3.org/2002/07/owl#',
        }

    @abc.abstractmethod
    def __init__(self, ld_source, debug=False):
        '''
        LDEntity Constructor
        '''
        # Initialise and set debug property
        self._debug = None
        self.debug = debug
        
        self._prefixes = None # Will be set on demand
        
        self.ld_source = ld_source        
            
    @abc.abstractmethod
    def get_entities(self, filter_triple_list=[]):
        '''
        '''
        return self.ld_source.get_entities(filter_triple_list=filter_triple_list + [FilterTriple(None, 'rdf:type', self.rdf_type)],
                                           prefixes = self.prefixes
                                           )
        

    @abc.abstractmethod
    def get_entity_details(self, entity_uri, filter_triple_list=[]):
        '''
        '''
        return self.ld_source.get_entities(entity_uri=entity_uri, 
                                           filter_triple_list=filter_triple_list + [FilterTriple(None, 'rdf:type', self.rdf_type)],
                                           prefixes = self.prefixes
                                           )
        

    @property
    def prefixes(self):
        '''
        Property to set class _prefixes attribute by gathering all superclass prefixes overridden with subclass ones
        '''
        if not hasattr(type(self), '_prefixes'): # Class _prefixes hasn't been set yet
            type(self)._prefixes = {}
            if issubclass(type(self), LDEntity): # If parent class might have prefixes
                for superclass in inspect.getmro(type(self))[-2::-1]: # Look through all superclasses starting from LDEntity
                    print(superclass)
                    if hasattr(superclass, '_default_prefixes'): # If this class might have default prefixes
                        type(self)._prefixes.update(superclass._default_prefixes)

        return type(self)._prefixes
    
    @property
    def rdf_type(self):
        return type(self)._rdf_type
    
    @property
    def debug(self):
        return self._debug
    
    @debug.setter
    def debug(self, debug_value):
        if self._debug != debug_value or self._debug is None:
            self._debug = debug_value
            
            if self._debug:
                logger.setLevel(logging.DEBUG)
                logging.getLogger(self.__module__).setLevel(logging.DEBUG)
            else:
                logger.setLevel(logging.INFO)
                logging.getLogger(self.__module__).setLevel(logging.INFO)
                
        logger.debug('Logger {} set to level {}'.format(logger.name, logger.level))
        logging.getLogger(self.__module__).debug('Logger {} set to level {}'.format(self.__module__, logger.level))
    
    @staticmethod    
    def get_ld_entity(ld_source, rdf_type, *args, **kwargs):  
        '''
        Class factory function to return subclass of LDEntity for specified rdf_type
        ''' 
        def register_subclasses():
            '''
            Helper function to register all LDEntity subclasses keyed by class rdf_type property
            Used by get_ld_entity class factory function
            '''
            ld_entity_module_dir = os.path.dirname(__file__)
            sys.path.append(ld_entity_module_dir)                               
            for ld_entity_subclass_module_name in [re.sub('\.\w+$', '.' + os.path.splitext(os.path.basename(module_path))[0], __name__)
                for module_path in glob(os.path.join(ld_entity_module_dir, '*_ld_entity.py'))
                ]:
                print('ld_entity_subclass_module_name = {}'.format(ld_entity_subclass_module_name))
                ld_entity_subclass_module = import_module(ld_entity_subclass_module_name)
                for ld_entity_subclass_name, ld_entity_subclass in inspect.getmembers(ld_entity_subclass_module):
                    if (inspect.isclass(ld_entity_subclass) 
                        and issubclass(ld_entity_subclass, LDEntity)
                        and ld_entity_subclass is not LDEntity
                        ):
                        logger.debug('LDEntity subclass {} registered for RDF type {}'.format(ld_entity_subclass_name,
                                                                                              ld_entity_subclass._rdf_type
                                                                                              )
                                     )
                        LDEntity._subclasses[ld_entity_subclass._rdf_type] = ld_entity_subclass

        try:
            if not LDEntity._subclasses:
                register_subclasses()
                
            ld_entity_subclass = LDEntity._subclasses[rdf_type]
            logger.debug('Created LDEntity instance for {}'.format(rdf_type))
        except Exception as e:
            print(e)
            raise LDEntityException('Unsupported RDF type: {}'.format(rdf_type))
        
        return ld_entity_subclass(ld_source=ld_source, *args, **kwargs)