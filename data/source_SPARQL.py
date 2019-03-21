from data.source import Source
from SPARQLWrapper import SPARQLWrapper, JSON
import _config as config
from rdflib import Graph, RDF, URIRef
from rdflib.namespace import SKOS

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
        sparql = SPARQLWrapper(config.VOCABS.get(self.vocab_id).get('sparql'))
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
        OPTIONAL {
            {?vocab dct:title ?vocab_label .} 
            UNION {?vocab rdfs:label ?vocab_label .}
            }
        FILTER(lang(?concept_preflabel) = "en" || lang(?concept_preflabel) = "")
    }
}
ORDER BY ?vocab''')
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()['results']['bindings']

        #return [(x.get('c').get('value'), x.get('l').get('value')) for result in results]
        return {result['vocab']['value']: {'source': config.VocabSource.SPARQL,
                                           'title': result['vocab_label']['value']}
                for result in results
                }


    def list_collections(self):
        sparql = SPARQLWrapper(config.VOCABS.get(self.vocab_id).get('sparql'))
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
        
        SELECT DISTINCT *
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
        sparql.setReturnFormat(JSON)
        concepts = sparql.query().convert()['results']['bindings']

        return [(x.get('c').get('value'), x.get('l').get('value')) for x in concepts]

    def list_concepts(self):
        print("VOCAB ID")
        print(self.vocab_id)
        sparql = SPARQLWrapper(config.VOCABS.get(self.vocab_id).get('sparql'))

        query = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT DISTINCT *
        WHERE {{
            GRAPH ?graph {{
                ?c a skos:Concept .
                ?c skos:prefLabel ?pl .
                }}
                    FILTER(?s = <{}>)
        }}'''.format(config.VOCABS.get(self.vocab_id).get('vocab_uri'))
        print("List Concepts Query: " + str(query))
        sparql.setQuery(query)

        sparql.setReturnFormat(JSON)
        concepts = sparql.query().convert()['results']['bindings']

        return [(x.get('c').get('value'), x.get('pl').get('value')) for x in concepts]

    def get_vocabulary(self):
        sparql = SPARQLWrapper(config.VOCABS.get(self.vocab_id).get('sparql'))
        print("VOCAB ID: " + str(self.vocab_id))
        # get the basic vocab metadata
        # PREFIX%20skos%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2004%2F02%2Fskos%2Fcore%23%3E%0APREFIX%20dct%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0APREFIX%20owl%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2002%2F07%2Fowl%23%3E%0ASELECT%20*%0AWHERE%20%7B%0A%3Fs%20a%20skos%3AConceptScheme%20%3B%0Adct%3Atitle%20%3Ft%20%3B%0Adct%3Adescription%20%3Fd%20%3B%0Adct%3Acreator%20%3Fc%20%3B%0Adct%3Acreated%20%3Fcr%20%3B%0Adct%3Amodified%20%3Fm%20%3B%0Aowl%3AversionInfo%20%3Fv%20.%0A%7D

        query = '''PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT DISTINCT *
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
            FILTER(?s = <{}>)
            OPTIONAL {{?s dct:description ?d }}
            OPTIONAL {{?s dct:creator ?c }}
            OPTIONAL {{?s dct:created ?cr }}
            OPTIONAL {{?s dct:modified ?m }}
            OPTIONAL {{?s owl:versionInfo ?v }}
            }}
        }}
        ORDER BY ?s'''.format(config.VOCABS.get(self.vocab_id).get('vocab_uri'))
        print(query)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
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
        query = '''PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT DISTINCT ?s ?tc ?pl
        WHERE {{
            GRAPH ?graph {{
                {{
                    ?s skos:hasTopConcept ?tc .
                    ?tc skos:prefLabel ?pl .
                    FILTER(?s = <{0}>)
                    }}
                UNION {{
                    {{
                        {{?s skos:member ?tc .}}
                        UNION {{?tc skos:inScheme ?s .}}
                        }}
                    ?tc skos:prefLabel ?pl .
                    OPTIONAL {{?tc skos:broader ?broader_concept .}}
                    FILTER (!bound(?broader_concept))
                    FILTER(?s = <{0}>)
                    }}
                }}
            }}
        ORDER BY ?s ?tc'''.format(config.VOCABS.get(self.vocab_id).get('vocab_uri'))
        print(query)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
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
        # sparql.setReturnFormat(JSON)
        # top_concepts = sparql.query().convert()['results']['bindings']

        from model.vocabulary import Vocabulary
        self.uri = metadata['results']['bindings'][0]['s']['value']
        print("SELF.URI: " + str(self.uri))
        return Vocabulary(
            self.vocab_id,
            metadata['results']['bindings'][0]['s']['value'],
            metadata['results']['bindings'][0]['t']['value'],
            metadata['results']['bindings'][0]['d']['value']
                if metadata['results']['bindings'][0].get('d') is not None else None,
            metadata['results']['bindings'][0].get('c').get('value')
                if metadata['results']['bindings'][0].get('c') is not None else None,
            metadata['results']['bindings'][0].get('cr').get('value')
                if metadata['results']['bindings'][0].get('cr') is not None else None,
            metadata['results']['bindings'][0].get('m').get('value')
                if metadata['results']['bindings'][0].get('m') is not None else None,
            metadata['results']['bindings'][0].get('v').get('value')
                if metadata['results']['bindings'][0].get('v') is not None else None,
            [(x.get('tc').get('value'), x.get('pl').get('value')) for x in top_concepts],
            self.get_concept_hierarchy(),
            config.VOCABS.get(self.vocab_id).get('download')
        )

    def get_collection(self, uri):
        sparql = SPARQLWrapper(config.VOCABS.get(self.vocab_id).get('sparql'))
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
SELECT DISTINCT *

WHERE {{
    GRAPH ?graph {{
        {
            {{<{uri}> dct:title ?l .}}
            UNION {{<{uri}> rdfs:label ?l .}}
            }}
        OPTIONAL {{?s rdfs:comment ?c }}
        }}
    }}'''.format({'uri': uri})
       
        sparql.setQuery(q)
        sparql.setReturnFormat(JSON)
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
SELECT DISTINCT *

WHERE {{
    GRAPH ?graph {{
        <{}> skos:member ?m .
        ?m skos:prefLabel ?pl .
        }}
    }}
ORDER BY ?m'''.format(uri)
        sparql.setQuery(q)
        sparql.setReturnFormat(JSON)
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

        print("VOCAB ID" + str(self.vocab_id))

        sparql = SPARQLWrapper(config.VOCABS.get(self.vocab_id).get('sparql'))
        #=======================================================================
        # q = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        #     SELECT *
        #     WHERE {{
        #       <{}> skos:prefLabel ?pl .
        #       OPTIONAL {{?s skos:definition ?d }}
        #     }}'''.format(uri)
        #=======================================================================
        q = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT *

WHERE {{
    GRAPH ?graph {{
        <{}> skos:prefLabel ?pl .
        OPTIONAL {{?s skos:definition ?d .}}
        }}
    }}'''.format(uri)
        sparql.setQuery(q)
        sparql.setReturnFormat(JSON)
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
SELECT DISTINCT *

WHERE {{
    GRAPH ?graph {{
        <{}> skos:altLabel ?al .
        }}
    }}
ORDER BY ?al'''.format(uri)
        sparql.setQuery(q)
        sparql.setReturnFormat(JSON)
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
SELECT DISTINCT *
WHERE {{
    GRAPH ?graph {{
        <{}> skos:hiddenLabel ?hl .
        ?hl skos:prefLabel ?pl .
        }}
    }}
ORDER BY ?pl ?hl'''.format(uri)
        sparql.setQuery(q)
        sparql.setReturnFormat(JSON)
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
SELECT DISTINCT *

WHERE {{
    GRAPH ?graph {{
        <{}> skos:broader ?b .
        ?b skos:prefLabel ?pl .
    }}
ORDER BY ?b'''.format(uri)
        sparql.setQuery(q)
        sparql.setReturnFormat(JSON)
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
SELECT DISTINCT *

WHERE {{
    GRAPH ?graph {{
        <{}> skos:narrower ?n .
        ?n skos:prefLabel ?pl .
        }}
    }}
ORDER BY ?n'''.format(uri)
        sparql.setQuery(q)
        sparql.setReturnFormat(JSON)
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
SELECT DISTINCT *

WHERE {{
    GRAPH ?graph {{
        <{}> dct:source ?source .
        }}
    }}
ORDER BY ?source'''.format(uri)
        sparql.setQuery(q)
        sparql.setReturnFormat(JSON)
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
SELECT DISTINCT *

WHERE {{
    GRAPH ?graph {{
        <{}> skos:definition ?definition .
        }}
    }}
ORDER BY ?definition'''.format(uri)
        sparql.setQuery(q)
        sparql.setReturnFormat(JSON)
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
SELECT DISTINCT *
WHERE {{
    GRAPH ?graph {{
        <{}> skos:prefLabel ?prefLabel .
        }}
    }}
ORDER BY ?preflabel'''.format(uri)
        sparql.setQuery(q)
        sparql.setReturnFormat(JSON)
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
            contributor=metadata[0].get('cn').get('value') if metadata[0].get('cn') is not None else None,
            broaders=[{'uri': x.get('b').get('value'), 'prefLabel': x.get('pl').get('value')} for x in broaders] if broaders else [],
            narrowers=[{'uri': x.get('n').get('value'), 'prefLabel': x.get('pl').get('value')} for x in narrowers] if narrowers else [],
            exactMatches=None,
            closeMatches=metadata[0].get('cn').get('value') if metadata[0].get('cn') is not None else [],
            broadMatches=[],
            narrowMatches=[],
            relatedMatches=[],
            semantic_properties=[]
        )

    def get_concept_hierarchy(self):
        print("HERE")
        sparql = SPARQLWrapper(config.VOCABS.get(self.vocab_id).get('sparql'))
        sparql.setQuery(
            """PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT (COUNT(?mid) AS ?length) ?c ?pl ?parent
WHERE {{
    GRAPH ?graph {{
        ?c      a                                       skos:Concept .   
        ?cs     (skos:hasTopConcept | skos:narrower)*   ?mid .
        ?mid    (skos:hasTopConcept | skos:narrower)+   ?c .                      
        ?c      skos:prefLabel                          ?pl .
        ?c		(skos:topConceptOf | skos:broader)		?parent .
        FILTER (?cs = <{}>)
        }}
    }}
GROUP BY ?c ?pl ?parent
ORDER BY ?length ?parent ?pl
    """.format(self.uri)
        )
        print(self.uri)
        sparql.setReturnFormat(JSON)
        cs = sparql.query().convert()['results']['bindings']
        print(cs)
        hierarchy = []
        previous_parent_uri = None
        last_index = 0

        for c in cs:

            print(c)
            # insert all topConceptOf directly
            if str(c['parent']['value']) == self.uri:
                hierarchy.append((
                    int(c['length']['value']),
                    c['c']['value'],
                    c['pl']['value'],
                    None
                ))
            else:
                # If this is not a topConcept, see if it has the same URI as the previous inserted Concept
                # If so, use that Concept's index + 1
                this_parent = c['parent']['value']
                if this_parent == previous_parent_uri:
                    # use last inserted index
                    hierarchy.insert(last_index + 1, (
                        int(c['length']['value']),
                        c['c']['value'],
                        c['pl']['value'],
                        c['parent']['value']
                    ))
                    last_index += 1
                # This is not a TopConcept and it has a differnt parent from the previous insert
                # So insert it after it's parent
                else:
                    i = 0
                    parent_index = 0
                    for t in hierarchy:
                        if this_parent in t[1]:
                            parent_index = i
                        i += 1

                    hierarchy.insert(parent_index + 1, (
                        int(c['length']['value']),
                        c['c']['value'],
                        c['pl']['value'],
                        c['parent']['value']
                    ))

                    last_index = parent_index + 1
                previous_parent_uri = this_parent
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
        sparql = SPARQLWrapper(config.VOCABS.get(self.vocab_id).get('sparql'))
        #=======================================================================
        # q = '''
        #     SELECT ?c
        #     WHERE {{
        #         <{}> a ?c .
        #     }}
        # '''.format(uri)
        #=======================================================================
        q = '''SELECT ?c
WHERE {{
    GRAPH ?graph {{
        <{}> a ?c .
        }}
    }}'''.format(uri)
        sparql.setQuery(q)

        sparql.setReturnFormat(JSON)
        for c in sparql.query().convert()['results']['bindings']:
            if c.get('c')['value'] in self.VOC_TYPES:
                return c.get('c')['value']

        return None
