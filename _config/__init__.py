from os import path
from data.source_FILE import FILE
from data.source_RVA import RVA
# RVA doesnt need to be imported as it's list_vocabularies method isn't used- vocabs from that are statically listed
from data.source_VOCBENCH import VOCBENCH

APP_DIR = path.dirname(path.dirname(path.realpath(__file__)))
TEMPLATES_DIR = path.join(APP_DIR, 'view', 'templates')
STATIC_DIR = path.join(APP_DIR, 'view', 'static')
LOGFILE = APP_DIR + '/flask.log'
DEBUG = True


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
VOCABS = {
    "Alteration Type - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': "Alteration Type - All Concepts",
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/alterationtype',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Borehole Drilling Method - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': "Borehole Drilling Method - All Concepts",
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/boreholedrillingmethod',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Mineral Resource Reporting Classification Method - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': "Mineral Resource Reporting Classification Method - All Concepts",
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/classification-method-used',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Commodity Code - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': "Commodity Code - All Concepts",
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/commodity-code',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Composition Category - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': "Composition Category - All Concepts",
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/compositioncategory',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Compound Material Constituent Part - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': "Compound Material Constituent Part - All Concepts",
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/compoundmaterialconstituentpartrole',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Consolidation Degree - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': "Consolidation Degree - All Concepts",
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/consolidationdegree',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Contact Type - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': "Contact Type - All Concepts",
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/contacttype',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Convention Code for Strike and Dip Measurements - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': "Convention Code for Strike and Dip Measurements - All Concepts",
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/conventioncode',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Deformation Style - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': "Deformation Style - All Concepts",
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/deformationstyle',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Description Purpose - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': "Description Purpose - All Concepts",
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/descriptionpurpose',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Orientation Determination Method - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': "Orientation Determination Method - All Concepts",
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/determinationmethodorientation',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Earth Resource Expression - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': "Earth Resource Expression - All Concepts",
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/earth-resource-expression',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Earth Resource Form - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': "Earth Resource Form - All Concepts",
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/earth-resource-form',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Earth Resource Material Role - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': "Earth Resource Material Role - All Concepts",
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/earth-resource-material-role',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Earth Resource Shape - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Earth Resource Shape - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/earth-resource-shape',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "End Use Potential - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'End Use Potential - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/end-use-potential',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Environmental Impact - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Environmental Impact - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/environmental-impact',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Event Environment - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Event Environment - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/eventenvironment',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Event Process - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Event Process - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/eventprocess',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Exploration Activity Type - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Exploration Activity Type - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/exploration-activity-type',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Exploration Result - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Exploration Result - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/exploration-result',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Fault Movement Sense - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Fault Movement Sense - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/faultmovementsense',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Fault Movement Type - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Fault Movement Type - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/faultmovementtype',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Fault Type - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Fault Type - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/faulttype',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Observation Method (Geologic Feature) - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Observation Method (Geologic Feature) - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/featureobservationmethod',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Foliation Type - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Foliation Type - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/foliationtype',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Genetic Category - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Genetic Category - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/geneticcategory',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Geologic Unit Morphology - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Geologic Unit Morphology - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/geologicunitmorphology',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Geologic Unit Part Role - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Geologic Unit Part Role - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/geologicunitpartrole',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Geologic Unit Type - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Geologic Unit Type - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/geologicunittype',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Lineation Type - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Lineation Type - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/lineationtype',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Simple Lithology - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Simple Lithology - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/lithology',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    #===========================================================================
    # "Simple Lithology - All Concepts": {
    # 'source': VocabSource.SPARQL,
    # 'title': 'Simple Lithology - All Concepts',
    # 'vocab_uri': 'http://resource.geosciml.org/classifierScheme/cgi/2016.01/simplelithology',
    # 'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    # 'download': 'rdf_test',
    # },
    #===========================================================================
    
    #===========================================================================
    # "lithology concepts": {
    # 'source': VocabSource.SPARQL,
    # 'title': 'lithology concepts',
    # 'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/lithology/',
    # 'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    # 'download': 'rdf_test',
    # },
    #===========================================================================

    #===========================================================================
    # "simplelithology": {
    # 'source': VocabSource.SPARQL,
    # 'title': 'simplelithology',
    # 'vocab_uri': 'http://resource.geosciml.org/classifierscheme/cgi/201211/simplelithology',
    # 'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    # 'download': 'rdf_test',
    # },
    #===========================================================================

    "Observation Method (Mapped Feature) - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Observation Method (Mapped Feature) - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/mappedfeatureobservationmethod',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Mapping Frame - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Mapping Frame - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/mappingframe',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Metamorphic Facies - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Metamorphic Facies - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/metamorphicfacies',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Metamorphic Grade - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Metamorphic Grade - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/metamorphicgrade',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Mine Status - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Mine Status - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/mine-status',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Mineral Occurrence Type - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Mineral Occurrence Type - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/mineral-occurrence-type',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Mining Activity - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Mining Activity - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/mining-activity',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Processing Activity - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Processing Activity - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/mining-processing-activity',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Particle Aspect Ratio - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Particle Aspect Ratio - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/particleaspectratio',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Particle Shape - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Particle Shape - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/particleshape',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Particle Type - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Particle Type - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/particletype',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Planar Polarity Code - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Planar Polarity Code - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/planarpolaritycode',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Proportion Term - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Proportion Term - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/proportionterm',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Raw Material Role - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Raw Material Role - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/raw-material-role',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Reserve Assessment Category - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Reserve Assessment Category - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/reserve-assessment-category',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Resource Assessment Category - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Resource Assessment Category - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/resource-assessment-category',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "oneGeology Europe precambrian timescale elements": {
    'source': VocabSource.SPARQL,
    'title': 'oneGeology Europe precambrian timescale elements',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/stratchart/',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Eras in the oneGeology Europe Precambrian timescale": {
    'source': VocabSource.SPARQL,
    'title': 'Eras in the oneGeology Europe Precambrian timescale',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/stratchart/Eras',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "One Geology Europe Precambrian Epoch definitions for Fenno-Scandian Shield": {
    'source': VocabSource.SPARQL,
    'title': 'One Geology Europe Precambrian Epoch definitions for Fenno-Scandian Shield',
    'vocab_uri': 'http://resource.geosciml.org/classifierscheme/cgi/2009/FennoScandianShieldProterozoicTimeScale',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Stratigraphic Rank - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Stratigraphic Rank - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/stratigraphicrank',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "UNFC Code - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'UNFC Code - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/unfc',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Value Qualifier - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Value Qualifier - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/valuequalifier',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Vocabulary Relation - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Vocabulary Relation - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/vocabularyrelation',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    "Waste Storage - All Concepts": {
    'source': VocabSource.SPARQL,
    'title': 'Waste Storage - All Concepts',
    'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/waste-storage',
    'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    'download': 'rdf_test',
    },

    #===========================================================================
    # 'rva-50': {
    #     'source': VocabSource.RVA,
    #     'title': 'Geologic Unit Type',
    #     'sparql': 'http://vocabs.ands.org.au/repository/api/sparql/ga_geologic-unit-type_v0-1',
    #     'download': 'https://vocabs.ands.org.au/registry/api/resource/downloads/196/ga_geologic-unit-type_v0-1.ttl'
    # },
    # 'rva-52': {
    #     'source': VocabSource.RVA,
    #     'title': 'Contact Type',
    #     'sparql': 'http://vocabs.ands.org.au/repository/api/sparql/ga_contact-type_v0-1',
    #     'download': 'https://vocabs.ands.org.au/registry/api/resource/downloads/202/ga_contact-type_v0-1.ttl'
    # },
    # 'rva-57': {
    #     'source': VocabSource.RVA,
    #     'title': 'Stratigraphic Rank',
    #     'sparql': 'http://vocabs.ands.org.au/repository/api/sparql/ga_stratigraphic-rank_v0-1',
    #     'download': 'https://vocabs.ands.org.au/registry/api/resource/downloads/217/ga-stratigraphic-rank.ttl'
    # },
    # 'jena-fuseki-igsn': {
    #     'source': VocabSource.SPARQL,
    #     'title': 'jena-fuseki-igsn (SPARQL)',
    #     'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    #     'download': 'rdf_test',
    #     'fuseki_dataset' : 'yes',
    #     'vocab_uri': 'http://pid.geoscience.gov.au/def/voc/ga/igsncode',
    # },
    # 'igsn-accessType': {
    #     'source': VocabSource.SPARQL,
    #     'title': 'IGSN Access Type (SPARQL)',
    #     'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    #     'download': 'rdf_test',
    #     'vocab_uri': 'http://pid.geoscience.gov.au/def/voc/ga/igsncode/accessType',
    # },
    # 'eventprocess': {
    #     'source': VocabSource.SPARQL,
    #     'title': 'Event Process (SPARQL)',
    #     'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    #     'download': 'rdf_test',
    #     'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/eventprocess',
    # },
    # 'CGI alteration_type': {
    #     'source': VocabSource.SPARQL,
    #     'title': 'CGI Alteration Type (SPARQL)',
    #     'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    #     'download': 'rdf_test',
    #     'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/alterationtype',
    # },
    # 'IGSN methodType': {
    #     'source': VocabSource.SPARQL,
    #     'title': 'IGSN Method Type (SPARQL)',
    #     'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    #     'download': 'rdf_test',
    #     'vocab_uri': 'http://pid.geoscience.gov.au/def/voc/ga/igsncode/methodType',
    # },
    # 'CGI Simple Lithology': {
    #     'source': VocabSource.SPARQL,
    #     'title': 'CGI Simple Lithology (SPARQL)',
    #     'sparql': 'http://dev2.nextgen.vocabs.ga.gov.au/fuseki/vocabs',
    #     'download': 'rdf_test',
    #     'vocab_uri': 'http://resource.geosciml.org/classifier/cgi/lithology',
    # },
    #===========================================================================
    # 'methodType': {
    #     'source': VocabSource.SPARQL,
    #     'title': 'Method Type',
    #     'sparql': 'http://52.65.31.119/fuseki/vocabs',
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
}

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


