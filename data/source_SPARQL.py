from data.source import Source
from SPARQLWrapper import SPARQLWrapper, JSON
import _config as config
from rdflib import Graph, RDF, URIRef
from rdflib.namespace import SKOS
from pprint import pprint

class SPARQL(Source):
    """Source for SPARQL endpoint
    """

    hierarchy = {}

    def __init__(self, vocab_id, request):
        super().__init__(vocab_id, request)

    @staticmethod
    def init():
        # print('Building concept hierarchy for source type RVA ...')
        # # build conceptHierarchy
        # for item in config.VOCABS:
        #     if config.VOCABS[item]['source'] == config.VocabSource.RVA:
        #         RVA.hierarchy[item] = RVA.build_concept_hierarchy(item)
        pass

    @classmethod
    def list_vocabularies(self):
        '''
        Return dict templated from source_VOCBENCG
        '''
        sparql = self.get_sparqlwrapper()
        sparql.setQuery('''PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>

SELECT distinct ?vocab ?vocab_label
WHERE {
    GRAPH ?graph {
        {
            {?vocab a skos:Collection .}
            UNION {?vocab a skos:ConceptScheme .}
            }
        OPTIONAL {?vocab dct:title ?vocab_title .
            FILTER(lang(?vocab_title) = "en" || lang(?vocab_title) = "")
            } 
        OPTIONAL {?vocab rdfs:label ?vocab_label .
            FILTER(lang(?vocab_label) = "en" || lang(?vocab_label) = "")
            }
    }
}
ORDER BY ?vocab''')
        
        results = sparql.query().convert()['results']['bindings']

        #return [(x.get('c').get('value'), x.get('l').get('value')) for result in results]
        return {result['vocab']['value']: {'source': config.VocabSource.SPARQL,
                                           'title': (result['vocab_title']['value'] 
                                                     if result.get('vocab_title')
                                                     else result['vocab_label']['value'] if result.get('vocab_label')
                                                     else '')}
                for result in results
                }


    def list_collections(self):
        sparql = self.get_sparqlwrapper()
        print("LIST COLLECTIONS")
        #=======================================================================
        # sparql.setQuery('''
        #     PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        #     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        #     SELECT *
        #     WHERE {
        #       ?c a skos:Concept .
        #       ?c rdfs:label ?l .
        #     }''')
        #=======================================================================
        sparql.setQuery('''PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX dct: <http://purl.org/dc/terms/>
        
        SELECT DISTINCT ?c ?l
        WHERE {
            GRAPH ?graph {
                {
                    {?c a skos:Collection .}
                    UNION {?c a skos:ConceptScheme .}
                    }
                OPTIONAL {
                    {?c dct:title ?l .} 
                    UNION {?c rdfs:label ?l .}
                    }
                }
            }
        ORDER BY ?c ?l''')
        
        concepts = sparql.query().convert()['results']['bindings']

        return [(x.get('c').get('value'), x.get('l').get('value')) for x in concepts]

    def list_concepts(self):
        sparql = self.get_sparqlwrapper()

        query = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?c ?pl
WHERE {{
    GRAPH ?graph {{
        {{
            {{<{vocab_uri}> a skos:ConceptScheme .}}
            UNION {{<{vocab_uri}> a skos:Collection .}}
            }}
        {{
            {{<{vocab_uri}> skos:member ?c .}}
            UNION {{?c skos:inScheme <{vocab_uri}> .}}
            }}
        ?c a skos:Concept .
        ?c skos:prefLabel ?pl .
        FILTER((LANG(?pl) = "en") || (LANG(?pl) = ""))
        }}
    }}'''.format(vocab_uri=config.VOCABS.get(self.vocab_id).get('vocab_uri'))
        print("List Concepts Query: " + str(query))
        sparql.setQuery(query)

        
        concepts = sparql.query().convert()['results']['bindings']

        concept_items = []
        for concept in concepts:
            metadata = {}
            metadata.update({'key': self.vocab_id})
            try:
                metadata.update({'uri': concept['c']['value']})
            except:
                metadata.update({'uri': None})
            try:
                metadata.update({'title': concept['pl']['value']})
            except:
                metadata.update({'title': None})
            try:
                metadata.update({'date_created': concept['date_created']['value'][:10]})
            except:
                metadata.update({'date_created': None})
            try:
                metadata.update({'date_modified': concept['date_modified']['value'][:10]})
            except:
                metadata.update({'date_modified': None})

            concept_items.append(metadata)

        return concept_items

    def get_vocabulary(self):
        sparql = self.get_sparqlwrapper()
        # get the basic vocab metadata
        # PREFIX%20skos%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2004%2F02%2Fskos%2Fcore%23%3E%0APREFIX%20dct%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0APREFIX%20owl%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2002%2F07%2Fowl%23%3E%0ASELECT%20*%0AWHERE%20%7B%0A%3Fs%20a%20skos%3AConceptScheme%20%3B%0Adct%3Atitle%20%3Ft%20%3B%0Adct%3Adescription%20%3Fd%20%3B%0Adct%3Acreator%20%3Fc%20%3B%0Adct%3Acreated%20%3Fcr%20%3B%0Adct%3Amodified%20%3Fm%20%3B%0Aowl%3AversionInfo%20%3Fv%20.%0A%7D

        query = '''PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT DISTINCT ?s ?t ?d ?c ?cr ?m ?v
        WHERE {{
        GRAPH ?graph 
        {{
            {{
            {{?s a skos:ConceptScheme .}}
            UNION {{?s a skos:Collection .}}
            }}
            {{
            {{?s dct:title ?t .}}
            UNION {{?s rdfs:label ?t .}}
            }}
            FILTER(?s = <{vocab_uri}>)
            OPTIONAL {{?s dct:description ?d }}
            OPTIONAL {{?s dct:creator ?c }}
            OPTIONAL {{?s dct:created ?cr }}
            OPTIONAL {{?s dct:modified ?m }}
            OPTIONAL {{?s owl:versionInfo ?v }}
            }}
        }}
        ORDER BY ?s'''.format(vocab_uri=config.VOCABS.get(self.vocab_id).get('vocab_uri'))
        print(query)
        sparql.setQuery(query)
        
        metadata = sparql.query().convert()

        # get the vocab's top concepts
        #=======================================================================
        # sparql.setQuery('''
        #     PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        #     SELECT *
        #     WHERE {
        #       ?s skos:hasTopConcept ?tc .
        #       ?tc skos:prefLabel ?pl .
        #     }''')
        #=======================================================================
        query = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT DISTINCT ?tc ?pl
WHERE {{
    GRAPH ?graph {{
        {{
            <{vocab_uri}> skos:hasTopConcept ?tc .
            ?tc skos:prefLabel ?pl .
            FILTER((LANG(?pl) = "en") || (LANG(?pl) = ""))
            }}
        UNION {{
            {{
                {{<{vocab_uri}> skos:member ?tc .}}
                UNION {{?tc skos:inScheme <{vocab_uri}> .}}
                }}
            ?tc skos:prefLabel ?pl .
            OPTIONAL {{?tc skos:broader ?broader_concept .
                {{
                {{<{vocab_uri}> skos:member ?broader_concept .}}
                UNION {{?broader_concept skos:inScheme <{vocab_uri}> .}}
                    }}
                }}
            FILTER (!bound(?broader_concept))
            FILTER((LANG(?pl) = "en") || (LANG(?pl) = ""))
            }}
        }}
    }}
ORDER BY ?tc'''.format(vocab_uri=config.VOCABS.get(self.vocab_id).get('vocab_uri'))
        print(query)
        sparql.setQuery(query)
        
        top_concepts = sparql.query().convert()['results']['bindings']

        # TODO: check if there are any common ways to ascertain if a vocab/ConceptScheme has any Collections
        # # get the vocab's collections
        # sparql.setQuery('''
        #     PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        #     SELECT *
        #     WHERE {
        #       ?s skos:hasTopConcept ?tc .
        #       ?tc skos:prefLabel ?pl .
        #     }''')
        # 
        # top_concepts = sparql.query().convert()['results']['bindings']

        from model.vocabulary import Vocabulary
        self.uri = metadata['results']['bindings'][0]['s']['value']
        print("SELF.URI: " + str(self.uri))
        return Vocabulary(
            id=self.vocab_id,
            uri=metadata['results']['bindings'][0]['s']['value'],
            title=metadata['results']['bindings'][0]['t']['value'],
            description=metadata['results']['bindings'][0]['d']['value']
                if metadata['results']['bindings'][0].get('d') is not None else None,
            creator=metadata['results']['bindings'][0].get('c').get('value')
                if metadata['results']['bindings'][0].get('c') is not None else None,
            created=metadata['results']['bindings'][0].get('cr').get('value')
                if metadata['results']['bindings'][0].get('cr') is not None else None,
            modified=metadata['results']['bindings'][0].get('m').get('value')
                if metadata['results']['bindings'][0].get('m') is not None else None,
            versionInfo=metadata['results']['bindings'][0].get('v').get('value')
                if metadata['results']['bindings'][0].get('v') is not None else None,
            hasTopConcepts=[(x.get('tc').get('value'), x.get('pl').get('value')) for x in top_concepts],
            conceptHierarchy=self.get_concept_hierarchy(),
            accessURL=None,
            downloadURL=config.VOCABS.get(self.vocab_id).get('download')
        )

    def get_collection(self, uri):
        sparql = self.get_sparqlwrapper()
        print("GET COLLECTION")
        #=======================================================================
        # q = '''PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        #     SELECT *
        #     WHERE {{
        #       <{}> rdfs:label ?l .
        #       OPTIONAL {{?s rdfs:comment ?c }}
        #     }}'''.format(uri)
        #=======================================================================
        q = '''PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dct: <http://purl.org/dc/terms/>
SELECT DISTINCT ?l ?c

WHERE {{
    GRAPH ?graph {{
        {
            {{<{uri}> dct:title ?l .}}
            UNION {{<{uri}> rdfs:label ?l .}}
            }}
        OPTIONAL {{?s rdfs:comment ?c }}
        }}
    }}'''.format(uri=uri)
       
        sparql.setQuery(q)
        
        metadata = sparql.query().convert()['results']['bindings']

        # get the collection's members
        #=======================================================================
        # q = ''' PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        #     SELECT *
        #     WHERE {{
        #       <{}> skos:member ?m .
        #       ?n skos:prefLabel ?pl .
        #     }}'''.format(uri)
        #=======================================================================
        q = ''' PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?m ?pl

WHERE {{
    GRAPH ?graph {{
        <{uri}> skos:member ?m .
        ?m skos:prefLabel ?pl .
        FILTER((LANG(?pl) = "en") || (LANG(?pl) = ""))
        }}
    }}
ORDER BY ?m'''.format(uri=uri)
        sparql.setQuery(q)
        
        members = sparql.query().convert()['results']['bindings']

        from model.collection import Collection
        return Collection(
            self.vocab_id,
            uri,
            metadata[0]['l']['value'],
            metadata[0].get('c').get('value') if metadata[0].get('c') is not None else None,
            [(x.get('m').get('value'), x.get('m').get('value')) for x in members]
        )

    def get_concept(self, uri):
        print("Get Concept")
        print("VOCAB ID" + str(self.vocab_id))

        sparql = self.get_sparqlwrapper()
        #=======================================================================
        # q = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        #     SELECT *
        #     WHERE {{
        #       <{}> skos:prefLabel ?pl .
        #       OPTIONAL {{?s skos:definition ?d }}
        #     }}'''.format(uri)
        #=======================================================================
        q = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?pl ?d

WHERE {{
    GRAPH ?graph {{
        <{uri}> skos:prefLabel ?pl .
        OPTIONAL {{?s skos:definition ?d .}}
        FILTER((LANG(?pl) = "en") || (LANG(?pl) = ""))
        }}
    }}'''.format(uri=uri)
        sparql.setQuery(q)
        
        metadata = None
        try:
            metadata = sparql.query().convert()['results']['bindings']
        except:
            pass

        # get the concept's altLabels
        #=======================================================================
        # q = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        #     SELECT *
        #     WHERE {{
        #       <{}> skos:altLabel ?al .
        #     }}'''.format(uri)
        #=======================================================================
        q = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?al

WHERE {{
    GRAPH ?graph {{
        <{uri}> skos:altLabel ?al .
        }}
    }}
ORDER BY ?al'''.format(uri=uri)
        sparql.setQuery(q)
        
        altLabels = None
        try:
            altLabels = sparql.query().convert()['results']['bindings']
        except:
            pass

        # get the concept's hiddenLabels
        #=======================================================================
        # q = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        #     SELECT *
        #     WHERE {{
        #       <{}> skos:hiddenLabel ?hl .
        #       ?hl skos:prefLabel ?pl .
        #     }}'''.format(uri)
        #=======================================================================
        q = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?hl ?pl
WHERE {{
    GRAPH ?graph {{
        <{uri}> skos:hiddenLabel ?hl .
        ?hl skos:prefLabel ?pl .
        FILTER((LANG(?pl) = "en") || (LANG(?pl) = ""))
        }}
    }}
ORDER BY ?pl ?hl'''.format(uri=uri)
        sparql.setQuery(q)
        
        hiddenLabels = None
        try:
            hiddenLabels = sparql.query().convert()['results']['bindings']
        except:
            pass

        # get the concept's broaders
        #=======================================================================
        # q = ''' PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        #     SELECT *
        #     WHERE {{
        #       <{}> skos:broader ?b .
        #       ?b skos:prefLabel ?pl .
        #     }}'''.format(uri)
        #=======================================================================
        q = ''' PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?b ?pl

WHERE {{
    GRAPH ?graph {{
        <{uri}> skos:broader ?b .
        ?b skos:prefLabel ?pl .
        FILTER((LANG(?pl) = "en") || (LANG(?pl) = ""))
        }}
    }}
ORDER BY ?b'''.format(uri=uri)
        sparql.setQuery(q)
        print(q)
        
        broaders = None
        try:
            broaders = sparql.query().convert()['results']['bindings']
        except:
            pass

        # get the concept's narrowers
        #=======================================================================
        # q = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        #     SELECT *
        #     WHERE {{
        #       <{}> skos:narrower ?n .
        #       ?n skos:prefLabel ?pl .
        #     }}'''.format(uri)
        #=======================================================================
        q = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?n ?pl

WHERE {{
    GRAPH ?graph {{
        <{uri}> skos:narrower ?n .
        ?n skos:prefLabel ?pl .
        FILTER((LANG(?pl) = "en") || (LANG(?pl) = ""))
        }}
    }}
ORDER BY ?n'''.format(uri=uri)

        sparql.setQuery(q)
        
        narrowers = None
        try:
            narrowers = sparql.query().convert()['results']['bindings']
        except:
            pass

        # get the concept's source
        #=======================================================================
        # q = '''PREFIX dct: <http://purl.org/dc/terms/>
        #             SELECT *
        #             WHERE {{
        #               <{}> dct:source ?source .
        #             }}'''.format(uri)
        #=======================================================================
        q = '''PREFIX dct: <http://purl.org/dc/terms/>
SELECT DISTINCT ?source

WHERE {{
    GRAPH ?graph {{
        <{uri}> dct:source ?source .
        }}
    }}
ORDER BY ?source'''.format(uri=uri)
        sparql.setQuery(q)
        
        source = None
        try:
            source = sparql.query().convert()['results']['bindings'][0]['source']['value']
        except:
            pass

        # get the concept's definition
        #=======================================================================
        # q = ''' PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        #                     SELECT *
        #                     WHERE {{
        #                       <{}> skos:definition ?definition .
        #                     }}'''.format(uri)
        #=======================================================================
        q = ''' PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?definition

WHERE {{
    GRAPH ?graph {{
        <{uri}> skos:definition ?definition .
        }}
    }}
ORDER BY ?definition'''.format(uri=uri)
        sparql.setQuery(q)
        
        definition = None
        try:
            definition = sparql.query().convert()['results']['bindings'][0]['definition']['value']
        except:
            pass

        # get the concept's prefLabel
        #=======================================================================
        # q = ''' PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        #                             SELECT *
        #                             WHERE {{
        #                               <{}> skos:prefLabel ?prefLabel .
        #                             }}'''.format(uri)
        #=======================================================================
        q = ''' PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?prefLabel
WHERE {{
    GRAPH ?graph {{
        <{uri}> skos:prefLabel ?prefLabel .
        FILTER((LANG(?prefLabel) = "en") || (LANG(?prefLabel) = ""))
        }}
    }}
ORDER BY ?preflabel'''.format(uri=uri)
        sparql.setQuery(q)
        
        try:
            prefLabel = sparql.query().convert()['results']['bindings'][0]['prefLabel']['value']
        except:
            pass

        from model.concept import Concept
        return Concept(
            vocab_id=self.vocab_id,
            uri=uri,
            prefLabel=prefLabel,
            definition=definition,
            altLabels=[x.get('al').get('value') for x in altLabels],
            hiddenLabels=[x.get('hl').get('value') for x in hiddenLabels],
            source=source,
            contributors=metadata[0].get('cn').get('value') if metadata[0].get('cn') is not None else None,
            broaders=[{'uri': x.get('b').get('value'), 'prefLabel': x.get('pl').get('value')} for x in broaders] if broaders else [],
            narrowers=[{'uri': x.get('n').get('value'), 'prefLabel': x.get('pl').get('value')} for x in narrowers] if narrowers else [],
            exactMatches=None,
            closeMatches=metadata[0].get('cn').get('value') if metadata[0].get('cn') is not None else [],
            broadMatches=[],
            narrowMatches=[],
            relatedMatches=[],
            semantic_properties=[],
            date_created=None,
            date_modified=None
        )

    def get_concept_hierarchy(self):
        '''
        Function to draw concept hierarchy for vocabulary
        '''
        def build_hierarchy(bindings_list, broader_concept=None, level=0):
            '''
            Recursive helper function to build hierarchy list from a bindings list
            Returns list of tuples: (<level>, <concept>, <concept_preflabel>, <broader_concept>)
            '''
            level += 1 # Start with level 1 for top concepts
            hierarchy = []
           
            narrower_list = sorted([binding_dict 
                                    for binding_dict in bindings_list
                                    if 
                                        # Top concept
                                        ((broader_concept is None) 
                                         and (binding_dict.get('broader_concept') is None))
                                    or 
                                        # Narrower concept
                                        ((binding_dict.get('broader_concept') is not None) 
                                         and (binding_dict['broader_concept']['value'] == broader_concept))
                             ], key=lambda binding_dict: binding_dict['concept']['value']) 
            #print(broader_concept, narrower_list)
            for binding_dict in narrower_list: 
                concept = binding_dict['concept']['value']              
                hierarchy += [(level,
                               concept,
                               binding_dict['concept_preflabel']['value'],
                               binding_dict['broader_concept']['value'] if binding_dict.get('broader_concept') else None,
                               )
                              ] + build_hierarchy(bindings_list, concept, level)
            #print(level, hierarchy)
            return hierarchy
                
        sparql = self.get_sparqlwrapper()
        query = '''PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>

SELECT distinct ?concept ?concept_preflabel ?broader_concept

WHERE {{
    GRAPH ?graph {{
        {{
            {{<{vocab_uri}> a skos:Collection .}}
            UNION {{<{vocab_uri}> a skos:ConceptScheme .}}
            }}
        {{
            {{<{vocab_uri}> skos:member ?concept .}}
            UNION {{?concept skos:inScheme <{vocab_uri}> .}}
            }}
        ?concept skos:prefLabel ?concept_preflabel .
        OPTIONAL {{?concept skos:definition ?concept_description .}}
        OPTIONAL {{?concept skos:broader ?broader_concept .}}
        FILTER(lang(?concept_preflabel) = "en" || lang(?concept_preflabel) = "")
    }}
}}
ORDER BY ?concept'''.format(vocab_uri=self.uri)
        print(query)
        sparql.setQuery(query)
        
        bindings_list = sparql.query().convert()['results']['bindings']
        
        hierarchy = build_hierarchy(bindings_list)

        return Source.draw_concept_hierarchy(hierarchy, self.request, self.vocab_id)


    @staticmethod
    def build_concept_hierarchy(vocab_id):
        g = Graph().parse(config.VOCABS[vocab_id]['download'], format='turtle')

        # get uri
        uri = None
        for s, p, o in g.triples((None, RDF.type, SKOS.ConceptScheme)):
            uri = str(s)

        # get TopConcept
        topConcepts = []
        for s, p, o in g.triples((URIRef(uri), SKOS.hasTopConcept, None)):
            topConcepts.append(str(o))

        hierarchy = []
        if topConcepts:
            topConcepts.sort()
            for tc in topConcepts:
                hierarchy.append((1, tc, Source.get_prefLabel_from_uri(tc)))
                hierarchy += Source.get_narrowers(tc, 1)
            return hierarchy
        else:
            raise Exception('topConcept not found')

    def get_object_class(self, uri):
        sparql = self.get_sparqlwrapper()
        #=======================================================================
        # q = '''
        #     SELECT ?c
        #     WHERE {{
        #         <{}> a ?c .
        #     }}
        # '''.format(uri)
        #=======================================================================
        q = '''SELECT DISTINCT ?c
WHERE {{
    GRAPH ?graph {{
        <{uri}> a ?c .
        }}
    }}'''.format(uri=uri)
        sparql.setQuery(q)

        
        for c in sparql.query().convert()['results']['bindings']:
            if c.get('c')['value'] in self.VOC_TYPES:
                return c.get('c')['value']

        return None

    def get_sparqlwrapper(self, 
                          return_format=JSON,
                          method='GET'):
        '''
        Helper function to set up and return a SPARQLWrapper instance
        '''
        sparql_wrapper = SPARQLWrapper(config.VOCABS.get(self.vocab_id).get('sparql'))
        sparql_wrapper.setReturnFormat(return_format)
        sparql_wrapper.setMethod(method)
        
        if (hasattr(config, 'SPARQL_CREDENTIALS')
            and config.SPARQL_CREDENTIALS.get(config.VOCABS.get(self.vocab_id).get('sparql'))):
            sparql_credentials = config.SPARQL_CREDENTIALS[config.VOCABS.get(self.vocab_id).get('sparql')]
            sparql_wrapper.setCredentials(sparql_credentials['username'], sparql_credentials['password'])
        
        return sparql_wrapper
    
    def get_rdf(self, return_format="turtle"):
        '''
        Function to return SKOS RDF for vocab
        '''
        sparql_wrapper = self.get_sparqlwrapper(return_format=return_format)

        #query = '''describe <{vocab_uri}>'''.format(vocab_uri=config.VOCABS.get(self.vocab_id).get('vocab_uri'))
        query='''PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>
describe *
from <{vocab_uri}>
{{
    {{<{vocab_uri}> a skos:Collection .
    <{vocab_uri}> skos:member ?concept .}}
    UNION 
    {{<{vocab_uri}> a skos:ConceptScheme .
    ?concept skos:inScheme <{vocab_uri}> .}}
    }}
'''.format(vocab_uri=config.VOCABS.get(self.vocab_id).get('vocab_uri'))
        print(query)
        sparql_wrapper.setQuery(query)
        pprint(sparql_wrapper.__dict__)
        return sparql_wrapper.query().response.read()
        