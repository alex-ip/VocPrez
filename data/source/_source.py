import _config as config
from rdflib import Graph, URIRef
from rdflib.namespace import SKOS
import markdown
from flask import g
from SPARQLWrapper import SPARQLWrapper, JSON, BASIC
import dateutil
from model.concept import Concept
from collections import OrderedDict
from helper import make_title, url_decode, cache_read, cache_write
import logging
import base64
import requests
from time import sleep
import helper as h

# Default to English if no DEFAULT_LANGUAGE in config
if hasattr(config, 'DEFAULT_LANGUAGE:'):
    DEFAULT_LANGUAGE = config.DEFAULT_LANGUAGE
else:
    DEFAULT_LANGUAGE = 'en'


class Source:
    VOC_TYPES = [
        'http://purl.org/vocommons/voaf#Vocabulary',
        'http://www.w3.org/2004/02/skos/core#ConceptScheme',
        'http://www.w3.org/2004/02/skos/core#ConceptCollection',
        'http://www.w3.org/2004/02/skos/core#Concept',
    ]

    def __init__(self, vocab_id, request, language=None):
        self.vocab_id = vocab_id
        self.request = request
        self.language = language or DEFAULT_LANGUAGE
        
        self._graph = None # Property for rdflib Graph object to be populated on demand
        self._vocabulary = None # Property for Vocabulary object to be populated on demand

    @staticmethod
    def collect(details):
        """
        Specialised Sources must implement a collect method to get all the vocabs of their sort, listed in
        _config/__init__.py, at startup
        """
        pass

    def list_collections(self):
        
        sparql_query = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT *
WHERE {{
    {{ GRAPH ?graph {{
        ?collection a skos:Collection .
        {{?collection (rdfs:label | skos:prefLabel) ?label .
        FILTER(lang(?label) = "{language}" || lang(?label) = "") 
        }}
    }} }}
    UNION
    {{
        ?collection a skos:Collection .
        {{?collection (rdfs:label | skos:prefLabel) ?label .
        FILTER(lang(?label) = "{language}" || lang(?label) = "") 
        }}
    }} 
}}'''.format(language=self.language)
        collections = Source.sparql_query(self.vocabulary.sparql_endpoint, sparql_query, self.vocabulary.sparql_username, self.vocabulary.sparql_password)

        return [(x.get('collection').get('value'), x.get('label').get('value')) for x in collections]

    def list_concepts(self):
        
        sparql_query = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX ldv: <http://purl.org/linked-data/version#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT DISTINCT ?concept ?prefLabel ?d ?created ?modified
WHERE {{
    {{ GRAPH ?graph {{
            {{<{concept_scheme_uri}> a skos:ConceptScheme .
            ?concept skos:inScheme <{concept_scheme_uri}> .}}
        union
        union
        {{<{concept_scheme_uri}> a skos:ConceptScheme .
        <{concept_scheme_uri}> (ldv:currentVersion | owl:sameAs)+ ?equivalentConceptScheme .
        ?equivalentConceptScheme a skos:ConceptScheme .
        ?concept skos:inScheme ?equivalentConceptScheme .}}
        {{ ?concept skos:prefLabel ?prefLabel .
        FILTER(lang(?prefLabel) = "{language}" || lang(?prefLabel) = "") 
        }}
        OPTIONAL {{ ?concept skos:definition ?d .
        FILTER(lang(?d) = "{language}" || lang(?d) = "") 
        }}
        OPTIONAL {{ ?concept dct:created ?created . }}
        OPTIONAL {{ ?concept dct:modified ?modified . }}
    }} }}
    UNION
    {{
            {{<{concept_scheme_uri}> a skos:ConceptScheme .
            ?concept skos:inScheme <{concept_scheme_uri}> .}}
        union
            {{<{concept_scheme_uri}> ldv:currentVersion ?currentVersionConceptScheme .
            ?concept skos:inScheme ?currentVersionConceptScheme .}}
        union
            {{<{concept_scheme_uri}> ldv:currentVersion ?currentVersionConceptScheme .
            ?currentVersionConceptScheme owl:sameAs ?equivalentCurrentVersionConceptScheme .
            ?concept skos:inScheme ?equivalentCurrentVersionConceptScheme .}}
        union
            {{<{concept_scheme_uri}> owl:sameAs ?equivalentConceptScheme .
            ?concept skos:inScheme ?equivalentConceptScheme .}}
        {{ ?concept skos:prefLabel ?prefLabel .
        FILTER(lang(?prefLabel) = "{language}" || lang(?prefLabel) = "") 
        }}
        OPTIONAL {{ ?concept skos:definition ?d .
        FILTER(lang(?d) = "{language}" || lang(?d) = "") 
        }}
        OPTIONAL {{ ?concept dct:created ?created . }}
        OPTIONAL {{ ?concept dct:modified ?modified . }}
    }}
}}
ORDER BY ?prefLabel'''.format(concept_scheme_uri=self.vocabulary.concept_scheme_uri, 
                        language=self.language)
        concepts = Source.sparql_query(self.vocabulary.sparql_endpoint, sparql_query, self.vocabulary.sparql_username, self.vocabulary.sparql_password)

        concept_items = []
        for concept in concepts:
            metadata = {
                'key': self.vocab_id,
                'uri': concept['concept']['value'],
                'title': concept['prefLabel']['value'],
                'definition': concept.get('d')['value'] if concept.get('d') else None,
                'created': dateutil.parser.parse(concept['created']['value']) if concept.get('created') else None,
                'modified': dateutil.parser.parse(concept['modified']['value']) if concept.get('modified') else None
            }

            concept_items.append(metadata)

        return concept_items
    
    
    def get_vocabulary(self):
        """
        Function to return vocabulary - overridden in subclasses
        Get a vocab from the cache
        :return:
        :rtype:
        """       
        return g.VOCABS[self.vocab_id]


    def get_collection(self, uri):
        sparql_query = '''PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT *
WHERE {{ 
    {{ GRAPH ?graph {{
        {{ <{collection_uri}> (rdfs:label | skos:prefLabel) ?label .
        FILTER(lang(?label) = "{language}" || lang(?label) = "") }}
        OPTIONAL {{?s rdfs:comment ?comment .
        FILTER(lang(?comment) = "{language}" || lang(?comment) = "") }}
    }} }}
    UNION
    {{
        {{ <{collection_uri}> (rdfs:label | skos:prefLabel) ?label .
        FILTER(lang(?label) = "{language}" || lang(?label) = "") }}
        OPTIONAL {{?s rdfs:comment ?comment .
        FILTER(lang(?comment) = "{language}" || lang(?comment) = "") }}
    }}
}}'''.format(collection_uri=uri, 
                language=self.language)
        metadata = Source.sparql_query(self.vocabulary.sparql_endpoint, sparql_query, self.vocabulary.sparql_username, self.vocabulary.sparql_password)

        # get the collection's members
        sparql_query = '''PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT *
WHERE {{
    {{ GRAPH ?graph {{
        <{}> skos:member ?m .
        {{ ?n skos:prefLabel ?prefLabel .
        FILTER(lang(?prefLabel) = "{language}" || lang(?prefLabel) = "") }}
    }} }}
    UNION
    {{
        <{}> skos:member ?m .
        {{ ?n skos:prefLabel ?prefLabel .
        FILTER(lang(?prefLabel) = "{language}" || lang(?prefLabel) = "") }}
    }}
}}'''.format(collection_uri=uri, 
                            language=self.language)
        members = Source.sparql_query(self.vocabulary.sparql_endpoint, sparql_query, self.vocabulary.sparql_username, self.vocabulary.sparql_password)

        from model.collection import Collection
        return Collection(
            self.vocab_id,
            uri,
            metadata[0]['label']['value'],
            metadata[0].get('comment').get('value') if metadata[0].get('comment') is not None else None,
            [(x.get('m').get('value'), x.get('m').get('value')) for x in members]
        )

    def get_concept(self):
        concept_uri=self.request.values.get('uri')
        
        
        # Don't filter prefLabel language - we need to show multilingual preflabels with language tags
        sparql_query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>

select *

WHERE {{
    {{ GRAPH ?graph {{
        <{concept_uri}> ?predicate ?object .
        optional {{GRAPH ?predicateGraph {{?predicate rdfs:label ?predicateLabel .}} 
            FILTER(lang(?predicateLabel) = "{language}" || lang(?predicateLabel) = "")
            }}
        optional {{?object (skos:prefLabel | rdfs:label) ?objectLabel .
            FILTER(?predicate = skos:prefLabel || lang(?objectLabel) = "{language}" || lang(?objectLabel) = "") 
        }}
    }} }}
    UNION
    {{
        <{concept_uri}> ?predicate ?object .
        optional {{GRAPH ?predicateGraph {{?predicate rdfs:label ?predicateLabel .}} 
            FILTER(lang(?predicateLabel) = "{language}" || lang(?predicateLabel) = "")
            }}
        optional {{?object (skos:prefLabel | rdfs:label) ?objectLabel .
            FILTER(?predicate = skos:prefLabel || lang(?objectLabel) = "{language}" || lang(?objectLabel) = "")
        }}
    }}
}}""".format(concept_uri=concept_uri, 
             language=self.language)   
        #print(sparql_query)
        result = Source.sparql_query(self.vocabulary.sparql_endpoint, sparql_query, self.vocabulary.sparql_username, self.vocabulary.sparql_password)
        
        assert result, 'Unable to query concepts for {}'.format(self.request.values.get('uri'))
        
        #print(str(result).encode('utf-8'))

        prefLabel = None
        
        related_objects = {}
        
        for row in result:
            predicateUri = row['predicate']['value']
                
            # Special case for prefLabels
            if predicateUri == 'http://www.w3.org/2004/02/skos/core#prefLabel':
                predicateLabel = 'Multilingual Labels'
                preflabel_lang = row['object'].get('xml:lang')
                
                # Use default language or no language prefLabel as primary
                if ((not prefLabel and not preflabel_lang) or 
                    (preflabel_lang == self.language)
                    ):
                    prefLabel = row['object']['value'] # Set current language prefLabel
                    
                # Omit current language string from list (remove this if we want to show all)
                if preflabel_lang in ['', self.language]:
                    continue
                    
                # Apend language code to prefLabel literal
                related_object = '{} ({})'.format(row['object']['value'], preflabel_lang)
                related_objectLabel = None
            else:
                predicateLabel = (row['predicateLabel']['value'] if row.get('predicateLabel') and row['predicateLabel'].get('value') 
                                  else make_title(row['predicate']['value']))
            
                if row['object']['type'] == 'literal':
                    related_object = row['object']['value']
                    related_objectLabel = None
                elif row['object']['type'] == 'uri':
                    related_object = row['object']['value']
                    related_objectLabel = (row['objectLabel']['value'] if row.get('objectLabel') and row['objectLabel'].get('value') 
                                           else make_title(row['object']['value'])) 
            
            relationship_dict = related_objects.get(predicateUri)
            if relationship_dict is None:
                relationship_dict = {'label': predicateLabel,
                                     'objects': {}}
                related_objects[predicateUri] = relationship_dict
                
            relationship_dict['objects'][related_object] = related_objectLabel
            
        
        related_objects = OrderedDict([(predicate, {'label': related_objects[predicate]['label'],
                                                    'objects': OrderedDict([(key, related_objects[predicate]['objects'][key]) 
                                                                            for key in sorted(related_objects[predicate]['objects'].keys())
                                                                            ])
                                                    }
                                        )
                                       for predicate in sorted(related_objects.keys())
                                       ])
        
        #print(repr(related_objects).encode('utf-8'))
        
        return Concept(
            vocab_id=self.vocab_id,
            uri=concept_uri,
            prefLabel=prefLabel,
            related_objects=related_objects,
            semantic_properties=None,
            source=self,
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
                             ], key=lambda binding_dict: binding_dict['concept_preflabel']['value']) 
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
        
        
        
                 
        sparql_query = '''PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX ldv: <http://purl.org/linked-data/version#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT distinct ?concept ?concept_preflabel ?broader_concept
WHERE {{
    {{ GRAPH ?graph {{
        {{<{concept_scheme_uri}> a skos:ConceptScheme .
        ?concept skos:inScheme <{concept_scheme_uri}> .}}
        union
        {{<{concept_scheme_uri}> a skos:ConceptScheme .
        <{concept_scheme_uri}> (ldv:currentVersion | owl:sameAs)+ ?equivalentConceptScheme .
        ?equivalentConceptScheme a skos:ConceptScheme .
        ?concept skos:inScheme ?equivalentConceptScheme .}}
        ?concept skos:prefLabel ?concept_preflabel .
        OPTIONAL {{ ?concept skos:broader ?broader_concept .
            {{ ?broader_concept skos:inScheme <{concept_scheme_uri}> .}}
            union
            {{ ?broader_concept skos:inScheme ?equivalentConceptScheme .}}
        }}
        FILTER(lang(?concept_preflabel) = "{language}" || lang(?concept_preflabel) = "")
    }} }}
    UNION
    {{
        {{<{concept_scheme_uri}> a skos:ConceptScheme .
        ?concept skos:inScheme <{concept_scheme_uri}> .}}
        union
        {{<{concept_scheme_uri}> a skos:ConceptScheme .
        <{concept_scheme_uri}> (ldv:currentVersion | owl:sameAs)+ ?equivalentConceptScheme .
        ?equivalentConceptScheme a skos:ConceptScheme .
        ?concept skos:inScheme ?equivalentConceptScheme .}}
        ?concept skos:prefLabel ?concept_preflabel .
        OPTIONAL {{ ?concept skos:broader ?broader_concept .
            {{ ?broader_concept skos:inScheme <{concept_scheme_uri}> .}}
            union
            {{ ?broader_concept skos:inScheme ?equivalentConceptScheme .}}
        }}
        FILTER(lang(?concept_preflabel) = "{language}" || lang(?concept_preflabel) = "")
    }}
}}
ORDER BY ?concept_preflabel'''.format(concept_scheme_uri=self.vocabulary.concept_scheme_uri, language=self.language)
        #print(sparql_query)
        bindings_list = Source.sparql_query(self.vocabulary.sparql_endpoint, sparql_query, self.vocabulary.sparql_username, self.vocabulary.sparql_password)
        #print(bindings_list)
        assert bindings_list is not None, 'SPARQL concept hierarchy query failed'
         
        hierarchy = build_hierarchy(bindings_list)
        #print(hierarchy)
 
        return Source.draw_concept_hierarchy(hierarchy, self.request, self.vocab_id)


    def get_object_class(self):
        #print('get_object_class uri = {}'.format(url_decode(self.request.values.get('uri'))))
        
        sparql_query = '''SELECT DISTINCT * 
WHERE {{ 
    {{ GRAPH ?graph {{
        <{uri}> a ?class .
    }} }}
    UNION
    {{
        <{uri}> a ?class .
    }}
}}'''.format(uri=url_decode(self.request.values.get('uri')))
        uri_classes = Source.sparql_query(self.vocabulary.sparql_endpoint, sparql_query, self.vocabulary.sparql_username, self.vocabulary.sparql_password)
        assert uri_classes is not None, 'SPARQL class query failed'
        #print(uri_classes)
        # look for classes we understand (SKOS)
        for uri_class in uri_classes:
            if uri_class['class']['value'] in Source.VOC_TYPES:
                return uri_class['class']['value']

        return None

    @staticmethod
    def get_prefLabel_from_uri(uri):
        return ' '.join(str(uri).split('#')[-1].split('/')[-1].split('_'))

    @staticmethod
    def get_narrowers(uri, depth):
        """
        Recursively get all skos:narrower properties as a list.

        :param uri: URI node
        :param depth: The current depth
        :param graph: The graph
        :return: list of tuples(tree_depth, uri, prefLabel)
        :rtype: list
        """
        depth += 1

        # Some RVA sources won't load on first try, so ..
        # if failed, try load again.
        graph = None
        max_attempts = 10
        for i in range(max_attempts):
            try:
                graph = Graph().parse(uri + '.ttl', format='turtle')
                break
            except:
                logging.warning('Failed to load resource at URI {}. Attempt: {}.'.format(uri, i+1))
        if not graph:
            raise Exception('Failed to load Graph from {}. Maximum attempts exceeded {}.'.format(uri, max_attempts))

        items = []
        for s, p, o in graph.triples((None, SKOS.broader, URIRef(uri))):
            items.append((depth, str(s), Source.get_prefLabel_from_uri(s)))
        items.sort(key=lambda x: x[2])
        count = 0
        for item in items:
            count += 1
            new_items = Source.get_narrowers(item[1], item[0])
            items = items[:count] + new_items + items[count:]
            count += len(new_items)
        return items

    @staticmethod
    def draw_concept_hierarchy(hierarchy, request, vocab_id):
        tab = '\t'
        previous_length = 1

        text = ''
        tracked_items = []
        for item in hierarchy:
            mult = None

            if item[0] > previous_length + 2: # SPARQL query error on length value
                for tracked_item in tracked_items:
                    if tracked_item['name'] == item[3]:
                        mult = tracked_item['indent'] + 1

            if mult is None:
                found = False
                for tracked_item in tracked_items:
                    if tracked_item['name'] == item[3]:
                        found = True
                if not found:
                    mult = 0

            if mult is None: # else: # everything is normal
                mult = item[0] - 1

            # Default to showing local URLs unless told otherwise
            if (not hasattr(config, 'LOCAL_URLS')) or config.LOCAL_URLS:
                uri = request.url_root + 'object?vocab_id=' + vocab_id + '&uri=' + h.url_encode(item[1])
            else:
                uri = item[1]

            t = tab * mult + '* [' + item[2] + '](' + uri + ')\n'
            text += t
            previous_length = mult
            tracked_items.append({'name': item[1], 'indent': mult})

        return markdown.markdown(text)


    def get_top_concepts(self):
        # Get defined top concepts (if any)
        sparql_query = '''PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX ldv: <http://purl.org/linked-data/version#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT DISTINCT ?top_concept ?prefLabel
WHERE {{
    {{ GRAPH ?graph {{
        {{
            <{concept_scheme_uri}> a skos:ConceptScheme .
            {{
                {{<{concept_scheme_uri}> skos:hasTopConcept ?top_concept .}}
                union
                {{?top_concept skos:topConceptOf <{concept_scheme_uri}> .}}
            }}
        }}
        union
        {{
            <{concept_scheme_uri}> a skos:ConceptScheme .
            <{concept_scheme_uri}> (ldv:currentVersion | owl:sameAs)+ ?equivalentConceptScheme .
            ?equivalentConceptScheme a skos:ConceptScheme .
            {{
                {{?equivalentConceptScheme skos:hasTopConcept ?top_concept .}}
                union
                {{?top_concept skos:topConceptOf ?equivalentConceptScheme .}}
            }}
        }}
        ?top_concept skos:prefLabel ?prefLabel .
        FILTER(lang(?prefLabel) = "{language}" || lang(?prefLabel) = "")
    }} }}
    UNION
    {{
        {{
            <{concept_scheme_uri}> a skos:ConceptScheme .
            {{
                {{<{concept_scheme_uri}> skos:hasTopConcept ?top_concept .}}
                union
                {{?top_concept skos:topConceptOf <{concept_scheme_uri}> .}}
            }}
        }}
        union
        {{
            <{concept_scheme_uri}> a skos:ConceptScheme .
            <{concept_scheme_uri}> (ldv:currentVersion | owl:sameAs)+ ?equivalentConceptScheme .
            ?equivalentConceptScheme a skos:ConceptScheme .
            {{
                {{?equivalentConceptScheme skos:hasTopConcept ?top_concept .}}
                union
                {{?top_concept skos:topConceptOf ?equivalentConceptScheme .}}
            }}
        }}
        ?top_concept skos:prefLabel ?prefLabel .
        FILTER(lang(?prefLabel) = "{language}" || lang(?prefLabel) = "")
    }}
}}
ORDER BY ?prefLabel
'''.format(concept_scheme_uri=self.vocabulary.concept_scheme_uri,
                                   language=self.language)
        #print(sparql_query)
        top_concepts = Source.sparql_query(self.vocabulary.sparql_endpoint, sparql_query, self.vocabulary.sparql_username, self.vocabulary.sparql_password) or []
        
        top_concept_list = []
        for top_concept in top_concepts:
            top_concept_list.append((top_concept.get('top_concept').get('value'), top_concept.get('prefLabel').get('value')))

        # If no top concepts defined, get member concepts without broaders
        if len(top_concept_list) == 0: 
            sparql_query = '''PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX ldv: <http://purl.org/linked-data/version#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT DISTINCT ?top_concept ?prefLabel
WHERE {{
    {{ GRAPH ?graph {{
        {{<{concept_scheme_uri}> a skos:ConceptScheme .}}
        union
        {{
            <{concept_scheme_uri}> a skos:ConceptScheme .
            <{concept_scheme_uri}> (ldv:currentVersion | owl:sameAs)+ ?equivalentConceptScheme .
            ?equivalentConceptScheme a skos:ConceptScheme .
        }}
        {{ ?top_concept skos:inScheme <{concept_scheme_uri}> .}}
        union
        {{ ?top_concept skos:inScheme ?equivalentConceptScheme .}}
        OPTIONAL {{ ?top_concept skos:broader ?broader_concept .
            {{ ?broader_concept skos:inScheme <{concept_scheme_uri}> .}}
            union
            {{ ?broader_concept skos:inScheme ?equivalentConceptScheme .}}
        }}
        ?top_concept skos:prefLabel ?prefLabel .
        FILTER((broader_concept = "") && (lang(?prefLabel) = "{language}" || lang(?prefLabel) = ""))
    }} }}
    UNION
    {{
        {{<{concept_scheme_uri}> a skos:ConceptScheme .}}
        union
        {{
            <{concept_scheme_uri}> a skos:ConceptScheme .
            <{concept_scheme_uri}> (ldv:currentVersion | owl:sameAs)+ ?equivalentConceptScheme .
            ?equivalentConceptScheme a skos:ConceptScheme .
        }}
        {{ ?top_concept skos:inScheme <{concept_scheme_uri}> .}}
        union
        {{ ?top_concept skos:inScheme ?equivalentConceptScheme .}}
        OPTIONAL {{ ?top_concept skos:broader ?broader_concept .
            {{ ?broader_concept skos:inScheme <{concept_scheme_uri}> .}}
            union
            {{ ?broader_concept skos:inScheme ?equivalentConceptScheme .}}
        }}
        ?top_concept skos:prefLabel ?prefLabel .
        FILTER((broader_concept = "") && (lang(?prefLabel) = "{language}" || lang(?prefLabel) = ""))
    }}
}}
ORDER BY ?prefLabel
'''.format(concept_scheme_uri=self.vocabulary.concept_scheme_uri,
           language=self.language)
            #print(sparql_query)
            top_concepts = Source.sparql_query(self.vocabulary.sparql_endpoint, sparql_query, self.vocabulary.sparql_username, self.vocabulary.sparql_password) or []
            for top_concept in top_concepts:
                top_concept_list.append((top_concept.get('top_concept').get('value'), top_concept.get('prefLabel').get('value')))

        return top_concept_list

    @staticmethod
    def sparql_query(endpoint, sparql_query, sparql_username=None, sparql_password=None):
        sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(sparql_query)
        sparql.setReturnFormat(JSON)

        if sparql_username and sparql_password:            
            sparql.setHTTPAuth(BASIC)
            sparql.setCredentials(sparql_username, sparql_password)
            
        try:
            return sparql.query().convert()['results']['bindings']
        except Exception as e:
            logging.debug('SPARQL query failed: {}'.format(e))
            logging.debug('endpoint={}\nsparql_username={}\nsparql_password={}\n{}'.format(endpoint, sparql_username, sparql_password, sparql_query))
            return None
        
    
    @staticmethod
    def submit_sparql_query(endpoint, sparql_query, sparql_username=None, sparql_password=None, accept_format='json'):
        '''
        Function to submit a sparql query and return the textual response
        '''
        #logging.debug('sparql_query = {}'.format(sparql_query))
        accept_format = {'json': 'application/json',
                         'xml': 'application/rdf+xml',
                         'turtle': 'application/turtle'
                         }.get(accept_format) or 'application/json'
        headers = {'Accept': accept_format,
                   'Content-Type': 'application/sparql-query',
                   'Accept-Encoding': 'UTF-8'
                   }
        if (sparql_username and sparql_password):
            #logging.debug('Authenticating with username {} and password {}'.format(sparql_username, sparql_password))
            headers['Authorization'] = 'Basic ' + base64.encodebytes('{}:{}'.format(sparql_username, sparql_password).encode('utf-8')).strip().decode('utf-8')
            
        params = None
        
        retries = 0
        while True:
            try:
                response = requests.post(endpoint, 
                                       headers=headers, 
                                       params=params, 
                                       data=sparql_query, 
                                       timeout=config.SPARQL_TIMEOUT)
                #logging.debug('Response content: {}'.format(str(response.content)))
                assert response.status_code == 200, 'Response status code {} != 200'.format(response.status_code)
                return response.text
            except Exception as e:
                logging.warning('SPARQL query failed: {}'.format(e))
                retries += 1
                if retries <= config.MAX_RETRIES:
                    sleep(config.RETRY_SLEEP_SECONDS)
                    continue # Go around again
                else:
                    break
                
        raise(BaseException('SPARQL query failed'))


    @staticmethod
    def get_graph(endpoint, sparql_query, sparql_username=None, sparql_password=None):
        '''
        Function to return an rdflib Graph object containing the results of a query
        '''
        result_graph = Graph()
        response = Source.submit_sparql_query(endpoint, sparql_query, sparql_username=sparql_username, sparql_password=sparql_password, accept_format='xml')
        #print(response.encode('utf-8'))
        result_graph.parse(data=response)
        return result_graph
    
    
    @property
    def graph(self):
        cache_file_name = self.vocab_id + '.p'
        
        if self._graph is not None:
            return self._graph
        
        self._graph = cache_read(cache_file_name)        
        if self._graph is not None:
            return self._graph
        
        
        
        sparql_query = '''PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX ldv: <http://purl.org/linked-data/version#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

CONSTRUCT {{ ?subject ?predicate ?object }}
WHERE  {{ 
    {{ GRAPH ?graph {{
        {{    # conceptScheme
            ?subject ?predicate ?object .
            ?subject a skos:ConceptScheme .
            <{uri}> a skos:ConceptScheme .
        }}
        union
        {{    # conceptScheme members as subjects
            ?subject ?predicate ?object .
            {{
                {{<{uri}> a skos:ConceptScheme .
                ?subject skos:inScheme <{uri}> .}}
                union
                {{<{uri}> a skos:ConceptScheme .
                <{uri}> (ldv:currentVersion | owl:sameAs)+ ?equivalentConceptScheme .
                ?equivalentConceptScheme a skos:ConceptScheme .
                ?subject skos:inScheme ?equivalentConceptScheme .}}
            }}
        }}
        union
        {{    # conceptScheme members as objects
            ?subject ?predicate ?object .
            {{
                {{<{uri}> a skos:ConceptScheme .
                ?object skos:inScheme <{uri}> .}}
                union
                {{<{uri}> a skos:ConceptScheme .
                <{uri}> (ldv:currentVersion | owl:sameAs)+ ?equivalentConceptScheme .
                ?equivalentConceptScheme a skos:ConceptScheme .
                ?object skos:inScheme ?equivalentConceptScheme .}}
            }}
        }}
    }} }}
    UNION
    {{
        {{    # conceptScheme
            ?subject ?predicate ?object .
            ?subject a skos:ConceptScheme .
            <{uri}> a skos:ConceptScheme .
        }}
        union
        {{    # conceptScheme members as subjects
            ?subject ?predicate ?object .
            {{
                {{<{uri}> a skos:ConceptScheme .
                ?subject skos:inScheme <{uri}> .}}
                union
                {{<{uri}> a skos:ConceptScheme .
                <{uri}> (ldv:currentVersion | owl:sameAs)+ ?equivalentConceptScheme .
                ?equivalentConceptScheme a skos:ConceptScheme .
                ?subject skos:inScheme ?equivalentConceptScheme .}}
            }}
        }}
        union
        {{    # conceptScheme members as objects
            ?subject ?predicate ?object .
            {{
                {{<{uri}> a skos:ConceptScheme .
                ?object skos:inScheme <{uri}> .}}
                union
                {{<{uri}> a skos:ConceptScheme .
                <{uri}> (ldv:currentVersion | owl:sameAs)+ ?equivalentConceptScheme .
                ?equivalentConceptScheme a skos:ConceptScheme .
                ?object skos:inScheme ?equivalentConceptScheme .}}
            }}
        }}
    }}
    FILTER(STRSTARTS(STR(?predicate), STR(rdfs:))
        || STRSTARTS(STR(?predicate), STR(skos:))
        || STRSTARTS(STR(?predicate), STR(dct:))
        || STRSTARTS(STR(?predicate), STR(ldv:))
        || STRSTARTS(STR(?predicate), STR(owl:))
        )
}}'''.format(uri=self.vocabulary.uri)
        #print(sparql_query)
        self._graph = Source.get_graph(self.vocabulary.sparql_endpoint, sparql_query, sparql_username=self.vocabulary.sparql_username, sparql_password=self.vocabulary.sparql_password)
        cache_write(self._graph, cache_file_name)
        return self._graph
            

    @property
    def vocabulary(self):
        '''
        Property returning Vocabulary object with URI self.vocab_id
        '''
        if self._vocabulary is None:
            self._vocabulary = self.get_vocabulary()
            if self._vocabulary.hasTopConcept is None:
                self._vocabulary.hasTopConcept = self.get_top_concepts()
            if self._vocabulary.concept_hierarchy is None:
                self._vocabulary.concept_hierarchy = self.get_concept_hierarchy()
            if self._vocabulary.source is None:
                self._vocabulary.source = self
            
        return self._vocabulary
    
            


    # @staticmethod
    # def sparql_query_in_memory_graph(vocab_id, sparql_query):
    #     # get the graph from the pickled file
    #     graph = Source.load_pickle_graph(vocab_id)
    #
    #     # put the query to the graph
    #     for r in graph.query(sparql_query):
    #
    #
    #
    # @staticmethod
    # def sparql_query_sparql_endpoint(vocab_id, sparql_query):
    #     pass
