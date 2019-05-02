from os import path
from data.source_FILE import FILE
from data.source_RVA import RVA
# RVA doesnt need to be imported as it's list_vocabularies method isn't used- vocabs from that are statically listed
from data.source_VOCBENCH import VOCBENCH
from SPARQLWrapper import SPARQLWrapper, JSON
import re
from owlrl import NONE

APP_DIR = path.dirname(path.dirname(path.realpath(__file__)))
TEMPLATES_DIR = path.join(APP_DIR, 'view', 'templates')
STATIC_DIR = path.join(APP_DIR, 'view', 'static')
LOGFILE = APP_DIR + '/flask.log'
DEBUG = True

def get_cgi_vocabs(sparql_endpoint, sparql_credentials=None):
    '''
    Function to return nested dict of form
    'CGI Simple Lithology': {
        'source': VocabSource.SPARQL,
        'title': 'CGI Simple Lithology (SPARQL)',
        'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
        'download': 'rdf_test',
        'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/lithology',
    },    
    '''
    
    sparql = '''PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>

SELECT distinct ?vocab ?vocab_title ?vocab_label
WHERE {
    GRAPH ?graph {
        {
            {?vocab a skos:Collection .}
            UNION 
            {?vocab a skos:ConceptScheme .}
            }
        OPTIONAL {?vocab dct:title ?vocab_title .} 
        OPTIONAL {?vocab rdfs:label ?vocab_label .}
        FILTER(REGEX(STR(?vocab), "^http://resource.geosciml.org/"))
    }
}
ORDER BY ?vocab'''
    
    sparql_wrapper = SPARQLWrapper(sparql_endpoint)
    sparql_wrapper.setReturnFormat(JSON)
    
    if sparql_credentials:
        sparql_wrapper.setCredentials(sparql_credentials['username'], sparql_credentials['password'])
        
    sparql_wrapper.setQuery(sparql)
        
    bindings_list = sparql_wrapper.query().convert()['results']['bindings']
    
    vocabs_dict = {}
    for binding in bindings_list:
        if not (binding.get('vocab_title') or binding.get('vocab_label')):
            continue
        
        try:
            vocab_id = re.search('[^/]+$', binding['vocab']['value']).group(0)
        except AttributeError:
            vocab_id = re.search('([^/]+)/$', binding['vocab']['value']).group(1) # trailing "/"
            
        try:
            version = re.search('/cgi/([^/]+)/' + vocab_id, binding['vocab']['value']).group(1)
            vocab_id += '_' + version
        except:
            version = None
            
        # Keep shortest URI
        if vocabs_dict.get(vocab_id):
            if len(binding['vocab']['value']) > len(vocabs_dict[vocab_id]['vocab_uri']):
                continue
    
        vocabs_dict[vocab_id] = {
            'source': VocabSource.SPARQL,
            'title': (binding['vocab_title']['value'] if binding.get('vocab_title') else None 
                      or binding['vocab_label']['value']),
            'sparql': sparql_endpoint,
            'download': '/ttl/' + vocab_id,
            'fuseki_dataset' : 'yes',
            'vocab_uri': binding['vocab']['value'],
            }
        
        if version:
            vocabs_dict[vocab_id]['title'] += ' (' + version + ')'
        
    return vocabs_dict

#
# -- VocPrez Settings --------------------------------------------------------------------------------------------------
#

# Home title
TITLE = 'VocPrez'


#
#   Vocabulary data sources
#
# Here is the list of vocabulary sources that this instance uses. FILE, SPARQL, RVA & VOCBENCH are implemented already
# and are on by default (e.g. VOCBENCH = None) but other sources, such as GitHub can be added. To enable them, add a new
# like like VocBench.XXX = None
class VocabSource:
    FILE = 1
    SPARQL = 2
    RVA = 3
    VOCBENCH = 4
    # GITHUB = 5

# VOCBANCH credentials
VB_ENDPOINT = ''
VB_USER = ''
VB_PASSWORD = ''

# Configure login credentials for different SPARQL endpoints here
SPARQL_CREDENTIALS = {
    'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs':
    {'username': 'vocabuser',
     'password': 'vuser1234%^&*'
      },
    'http://52.65.31.119/fuseki/vocabs':
    {'username': 'vocabmanager',
     'password': 'vocab1234%^&*'
      },
    }
#
#   Instance vocabularies
#
# Here you list the vocabularies that this instance of VocPrez knows about. Note that some vocab data sources, like
# VOCBENCH auto list vocabularies by implementing the list_vocabularies method and thus their vocabularies don't need to
# be listed here. FILE vocabularies too don't need to be listed here as they are automatically picked up by the system
# if the files are added to the data/ folder, as described in the DATA_SOURCES.md documentation file.
#===============================================================================
# VOCABS = {
#     'rva-50': {
#         'source': VocabSource.RVA,
#         'title': 'Geologic Unit Type',
#         'sparql': 'http://vocabs.ands.org.au/repository/api/sparql/ga_geologic-unit-type_v0-1',
#         'download': 'https://vocabs.ands.org.au/registry/api/resource/downloads/196/ga_geologic-unit-type_v0-1.ttl'
#     },
#     'rva-52': {
#         'source': VocabSource.RVA,
#         'title': 'Contact Type',
#         'sparql': 'http://vocabs.ands.org.au/repository/api/sparql/ga_contact-type_v0-1',
#         'download': 'https://vocabs.ands.org.au/registry/api/resource/downloads/202/ga_contact-type_v0-1.ttl'
#     },
#     'rva-57': {
#         'source': VocabSource.RVA,
#         'title': 'Stratigraphic Rank',
#         'sparql': 'http://vocabs.ands.org.au/repository/api/sparql/ga_stratigraphic-rank_v0-1',
#         'download': 'https://vocabs.ands.org.au/registry/api/resource/downloads/217/ga-stratigraphic-rank.ttl'
#     },
#     'jena-fuseki-igsn': {
#         'source': VocabSource.SPARQL,
#         'title': 'jena-fuseki-igsn (SPARQL)',
#         'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
#         'download': 'rdf_test',
#         'fuseki_dataset' : 'yes',
#         'vocab_uri': 'http://pid.geoscience.gov.au/def/voc/ga/igsncode',
#     },
#     'igsn-accessType': {
#         'source': VocabSource.SPARQL,
#         'title': 'IGSN Access Type (SPARQL)',
#         'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
#         'download': 'rdf_test',
#         'vocab_uri': 'http://pid.geoscience.gov.au/def/voc/ga/igsncode/accessType',
#     },
#     'eventprocess': {
#         'source': VocabSource.SPARQL,
#         'title': 'Event Process (SPARQL)',
#         'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
#         'download': 'rdf_test',
#         'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/eventprocess',
#     },
#     'CGI alteration_type': {
#         'source': VocabSource.SPARQL,
#         'title': 'CGI Alteration Type (SPARQL)',
#         'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
#         'download': 'rdf_test',
#         'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/alterationtype',
#     },
#     'IGSN methodType': {
#         'source': VocabSource.SPARQL,
#         'title': 'IGSN Method Type (SPARQL)',
#         'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
#         'download': 'rdf_test',
#         'vocab_uri': 'http://pid.geoscience.gov.au/def/voc/ga/igsncode/methodType',
#     },
#     'CGI Simple Lithology': {
#         'source': VocabSource.SPARQL,
#         'title': 'CGI Simple Lithology (SPARQL)',
#         'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
#         'download': 'rdf_test',
#         'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/lithology',
#     },
# }
#===============================================================================
    #===========================================================================
    # 'methodType': {
    #     'source': VocabSource.SPARQL,
    #     'title': 'Method Type',
    #     'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    #     'download': 'rdf_test',
    #     'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/alterationtype',
    # },



    # 'assoc': {
    #     'source': VocabSource.FILE,
    #     'title': 'ISO19115-1 Association Type Codes - File'
    # },
    # 'tenement_type': {
    #     'source': VocabSource.FILE,
    #     'title': 'Tenement Type'
    # },
    # 'Test_Rock_Types_Vocabulary': {
    #     'source': VocabSource.VOCBENCH,
    #     'title': 'Test Rock Types'
    # },
    # 'contact_type': {
    #     'source': VocabSource.FILE,
    #     'title': 'Contact Type - File'
    # },
    # 'ga-stratigraphic-rank': {
    #     'source': VocabSource.FILE,
    #     'title': 'Stratigraphic Rank File'
    # }
    #===========================================================================
VOCABS = get_cgi_vocabs('http://52.65.31.119/fuseki/vocabs', 
                        SPARQL_CREDENTIALS['http://52.65.31.119/fuseki/vocabs'])

#
# -- Startup tasks -----------------------------------------------------------------------------------------------------
#

# read in RDF vocab files on startup in vocab_files directory
FILE.init()
RVA.init()
#SPARQL.init()

# extend this instances' list of vocabs by using the known sources
VOCABS = {**VOCABS, **FILE.list_vocabularies()}  # picks up all vocab RDF (turtle) files in data/
#VOCABS = {**VOCABS, **VOCBENCH.list_vocabularies()}  # picks up all vocabs at the relevant VocBench instance


