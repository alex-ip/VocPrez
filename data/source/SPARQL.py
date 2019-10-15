import logging
import dateutil.parser
from flask import g
from data.source._source import Source
from model.vocabulary import Vocabulary
import _config as config
import re
import os

if hasattr(config, 'DEFAULT_LANGUAGE:'):
    DEFAULT_LANGUAGE = config.DEFAULT_LANGUAGE
else:
    DEFAULT_LANGUAGE = 'en'


class SPARQL(Source):
    """Source for a generic SPARQL endpoint
    """

    def __init__(self, vocab_id, request, language=None):
        super().__init__(vocab_id, request, language)

    @classmethod
    def collect(self, details):
        """
        For this source, one SPARQL endpoint is given for a series of vocabs which are all separate ConceptSchemes

        'ga-jena-fuseki': {
            'source': VocabSource.SPARQL,
            'sparql_endpoint': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
            'sparql_username': '<sparql_user>', # Optional username for SPARQL endpoint
            'sparql_password': '<sparql_password>', # Optional password for SPARQL endpoint
            #'uri_filter_regex': '.*', # Regular expression to filter vocabulary URIs - Everything
            #'uri_filter_regex': '^http(s?)://pid.geoscience.gov.au/def/voc/ga/', # Regular expression to filter vocabulary URIs - GA
            #'uri_filter_regex': '^https://gcmdservices.gsfc.nasa.gov', # Regular expression to filter vocabulary URIs - GCMD
            'uri_filter_regex': '^http(s?)://resource.geosciml.org/', # Regular expression to filter vocabulary URIs - CGI

        },
        """
        logging.debug('SPARQL collect()...')
        
        # Get all the ConceptSchemes from the SPARQL endpoint
        # Interpret each CS as a Vocab
        sparql_query = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT DISTINCT * WHERE {{
    {{ GRAPH ?g {{
        ?conceptScheme a skos:ConceptScheme .
        OPTIONAL {{ ?conceptScheme skos:prefLabel ?prefLabel .
            FILTER(lang(?prefLabel) = "{language}" || lang(?prefLabel) = "") }}
        OPTIONAL {{ ?conceptScheme dct:title ?title .
            FILTER(lang(?title) = "{language}" || lang(?title) = "") }}
        OPTIONAL {{ ?conceptScheme rdfs:label ?label .
            FILTER(lang(?label) = "{language}" || lang(?label) = "") }}
        OPTIONAL {{ ?conceptScheme dct:creator ?creator }}
        OPTIONAL {{ ?conceptScheme dct:created ?created }}
        OPTIONAL {{ ?conceptScheme dct:issued ?issued }}
        OPTIONAL {{ ?conceptScheme dct:date ?date }}
        OPTIONAL {{ ?conceptScheme dct:modified ?modified }}
        OPTIONAL {{ ?conceptScheme owl:versionInfo ?version }}
        OPTIONAL {{ ?conceptScheme skos:definition ?definition .
            FILTER(lang(?definition) = "{language}" || lang(?definition) = "") }}
        OPTIONAL {{ ?conceptScheme dct:description ?description .
            FILTER(lang(?description) = "{language}" || lang(?description) = "") }}
        FILTER not exists {{?alternateConceptScheme owl:sameAs ?conceptScheme}}
    }} }}
    UNION
    {{
        ?conceptScheme a skos:ConceptScheme .
        OPTIONAL {{ ?conceptScheme skos:prefLabel ?prefLabel .
            FILTER(lang(?prefLabel) = "{language}" || lang(?prefLabel) = "") }}
        OPTIONAL {{ ?conceptScheme dct:title ?title .
            FILTER(lang(?title) = "{language}" || lang(?title) = "") }}
        OPTIONAL {{ ?conceptScheme rdfs:label ?label .
            FILTER(lang(?label) = "{language}" || lang(?label) = "") }}
        OPTIONAL {{ ?conceptScheme dct:creator ?creator }}
        OPTIONAL {{ ?conceptScheme dct:created ?created }}
        OPTIONAL {{ ?conceptScheme dct:issued ?issued }}
        OPTIONAL {{ ?conceptScheme dct:date ?date }}
        OPTIONAL {{ ?conceptScheme dct:modified ?modified }}
        OPTIONAL {{ ?conceptScheme owl:versionInfo ?version }}
        OPTIONAL {{ ?conceptScheme skos:definition ?definition .
            FILTER(lang(?definition) = "{language}" || lang(?definition) = "") }}
        OPTIONAL {{ ?conceptScheme dct:description ?description .
            FILTER(lang(?description) = "{language}" || lang(?description) = "") }}
        FILTER not exists {{?alternateConceptScheme owl:sameAs ?conceptScheme}}
    }}
}} 
ORDER BY ?title'''.format(language=DEFAULT_LANGUAGE)
        #print(sparql_query)
        # record just the IDs & title for the VocPrez in-memory vocabs list
        concept_schemes = Source.sparql_query(details['sparql_endpoint'], 
                                              sparql_query, 
                                              sparql_username=details.get('sparql_username'), 
                                              sparql_password=details.get('sparql_password')
                                              )
        assert concept_schemes is not None, 'Unable to query conceptSchemes'
        
        vocab_record_dict = {}
        for conceptScheme in concept_schemes:
            # Handle CS URIs that end with '/' or a numeric version
            cs_uri = re.sub('^http(s?)://|/conceptScheme$', '', conceptScheme['conceptScheme']['value'])
            vocab_id = os.path.basename(cs_uri)
            while not vocab_id or re.match('^(\d|\.)+$', vocab_id):
                cs_uri = os.path.dirname(cs_uri)
                if not cs_uri:
                    vocab_id = None
                    break
                vocab_id = os.path.basename(cs_uri)
                    
            assert vocab_id, 'Unable to determine valid vocab ID for conceptScheme {}'.format(conceptScheme['conceptScheme']['value'])
            
            #TODO: Investigate putting regex into SPARQL query
            #print("re.search('{}', '{}')".format(details.get('uri_filter_regex'), conceptScheme['conceptScheme']['value']))
            if details.get('uri_filter_regex') and not re.search(details['uri_filter_regex'], conceptScheme['conceptScheme']['value']):
                logging.debug('Skipping vocabulary {}'.format(vocab_id))
                continue
            
            vocab_record = {
                'id': vocab_id,
                'uri': conceptScheme['conceptScheme']['value'].replace('/conceptScheme', ''),
                'title': (conceptScheme.get('prefLabel') or conceptScheme.get('title') or conceptScheme.get('label') or {'value': None}).get('value') or None,
                'description': (conceptScheme.get('definition') or conceptScheme.get('description') or {'value': None}).get('value') or None,
                'creator': (conceptScheme.get('creator') or {'value': None}).get('value') or None,
                'created': dateutil.parser.parse(conceptScheme.get('created').get('value')) if conceptScheme.get('created') is not None else None,
                # dct:issued not in Vocabulary
                # dateutil.parser.parse(conceptScheme.get('issued').get('value')) if conceptScheme.get('issued') is not None else None,
                'modified': dateutil.parser.parse(conceptScheme.get('modified').get('value')) if conceptScheme.get('modified') is not None else None,
                'versionInfo': (conceptScheme.get('version') or {'value': None}).get('value') or None,
                'data_source': config.VocabSource.SPARQL,
                'concept_scheme_uri': conceptScheme['conceptScheme']['value'],
                'sparql_endpoint': details['sparql_endpoint'],
                'sparql_username': details['sparql_username'],
                'sparql_password': details['sparql_password']
                }
            
            if vocab_id in vocab_record_dict.keys(): # Multiple records through duplicate predicates
                logging.debug('Multiple records found for vocab {}'.format(vocab_id))
                # If URIs are the same, then append string values (could be dodgy)
                if vocab_record_dict[vocab_id]['concept_scheme_uri'].lower() == vocab_record['concept_scheme_uri'].lower():
                    for key, value in vocab_record.items():
                        if (vocab_record_dict[vocab_id][key] != value) and type(value) == str:
                            logging.debug('Appending {} value {} to {}'.format(key, value, vocab_record_dict[vocab_id][key]))
                            # Comma-separated values should be OK for literals
                            vocab_record_dict[vocab_id][key] = vocab_record_dict[vocab_id][key] + ', ' + value if vocab_record_dict[vocab_id][key] else value
                # Just use alphapbetic comparison as a sloppy version check
                elif vocab_record_dict[vocab_id]['concept_scheme_uri'].lower() < vocab_record['concept_scheme_uri'].lower(): 
                    logging.debug('Replacing vocab {} with {}'.format(vocab_record_dict[vocab_id]['concept_scheme_uri'], vocab_record['concept_scheme_uri']))
                    vocab_record_dict[vocab_id] = vocab_record
                else:
                    logging.debug('NOT replacing vocab {} with {}'.format(vocab_record_dict[vocab_id]['concept_scheme_uri'], vocab_record['concept_scheme_uri']))
            else:
                vocab_record_dict[vocab_id] = vocab_record # New record - just add it
                
        # Create vocab objects in dict keyed by vocab_id
        sparql_vocabs = {vocab_id: Vocabulary(**vocab_record) for vocab_id, vocab_record in vocab_record_dict.items()}

        g.VOCABS = {**g.VOCABS, **sparql_vocabs}
        logging.debug('SPARQL collect() complete.')
