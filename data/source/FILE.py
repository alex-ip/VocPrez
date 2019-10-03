from data.source._source import Source
from os.path import join
import _config as config
from rdflib import Graph, URIRef, RDF, RDFS
from rdflib.namespace import DCTERMS, SKOS
import os
import dateutil.parser
from collections import OrderedDict
import pickle
from model.concept import Concept
from model.collection import Collection
from flask import g
import logging
from model.vocabulary import Vocabulary
import helper as h

if hasattr(config, 'DEFAULT_LANGUAGE:'):
    DEFAULT_LANGUAGE = config.DEFAULT_LANGUAGE
else:
    DEFAULT_LANGUAGE = 'en'


class PickleLoadException(Exception):
    pass


class FILE(Source):
    hierarchy = {}
    vocab_files_folder = ''

    # file extensions mapped to rdflib-supported formats
    # see supported rdflib formats at https://rdflib.readthedocs.io/en/stable/plugin_parsers.html?highlight=format
    MAPPER = {
        'ttl': 'turtle',
        'rdf': 'xml',
        'owl': 'xml',
    }

    def __init__(self, vocab_id, request, language=None):
        super().__init__(vocab_id, request, language)
        self.gr = FILE.load_pickle_graph(vocab_id)

    @staticmethod
    def collect(details):
        file_vocabs = {}
        # find all files in project_directory/data/source/vocab_files
        for path, subdirs, files in os.walk(join(config.APP_DIR, 'data', 'vocab_files')):
            for name in files:
                if name.split('.')[-1] in FILE.MAPPER:
                    # load file
                    file_path = os.path.join(path, name)
                    file_format = FILE.MAPPER[name.split('.')[-1]]
                    # load graph
                    gr = Graph().parse(file_path, format=file_format)
                    file_name = name.split('.')[0]
                    # pickle to directory/vocab_files/
                    with open(join(path, file_name + '.p'), 'wb') as f:
                        pickle.dump(gr, f)
                        f.close()

                    # extract vocab metadata
                    # Get the ConceptSchemes from the graph of the file
                    # Interpret the CS as a Vocab
                    q = '''
                        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        PREFIX dcterms: <http://purl.org/dc/terms/>
                        PREFIX owl: <http://www.w3.org/2002/07/owl#>
                        SELECT 
                            ?cs          # 0
                            ?title       # 1 
                            ?created     # 2
                            ?issued      # 3
                            ?modified    # 4
                            ?version     # 5
                            ?description # 6
                        WHERE {{
                            ?cs a skos:ConceptScheme .
                            OPTIONAL {{ 
                                ?cs skos:prefLabel ?title .
                                FILTER(lang(?title) = "{language}" || lang(?title) = "") 
                            }}
                            OPTIONAL {{ ?cs dcterms:created ?created }}
                            OPTIONAL {{ ?cs dcterms:issued ?issued }}
                            OPTIONAL {{ ?cs dcterms:modified ?modified }}
                            OPTIONAL {{ ?cs owl:versionInfo ?version }}
                            OPTIONAL {{ 
                                ?cs skos:definition ?description .
                                FILTER(lang(?description) = "{language}" || lang(?description) = "") 
                            }}
                        }}'''.format(language=DEFAULT_LANGUAGE)

                    vocab_id = str(name).split('.')[0]
                    for cs in gr.query(q):
                        file_vocabs[vocab_id] = Vocabulary(
                            vocab_id,
                            str(cs[0]).replace('/conceptScheme', ''),
                            str(cs[1]) or str(cs[0]) if str(cs[1]) else str(cs[0]),  # Need string, not None
                            str(cs[6]) if cs[6] is not None else None,
                            None,
                            dateutil.parser.parse(str(cs[2])) if cs[2] is not None else None,
                            dateutil.parser.parse(str(cs[4])) if cs[4] is not None else None,
                            str(cs[5]) if cs[5] is not None else None,  # versionInfo
                            config.VocabSource.FILE,
                            cs[0]
                        )
        g.VOCABS = {**g.VOCABS, **file_vocabs}

        logging.debug('FILE collect() complete.')
        # # Get register item metadata
        # for vocab_id in g.VOCABS:
        #     if vocab_id in g.VOCABS:
        #         if g.VOCABS[vocab_id]['source'] != config.VocabSource.FILE:
        #             continue
        #
        #         # Creators
        #         creators = []
        #         g = FILE.load_pickle_graph(vocab_id)
        #         for uri in g.subjects(RDF.type, SKOS.ConceptScheme):
        #             for creator in g.objects(uri, DCTERMS.creator):
        #                 creators.append(str(creator))
        #             break
        #         g.VOCABS[vocab_id]['creators'] = creators
        #
        #         # Date Created
        #         created = None
        #         # dct:created
        #         for uri in g.subjects(RDF.type, SKOS.ConceptScheme):
        #             for date in g.objects(uri, DCTERMS.created):
        #                 created = str(date)[:10]
        #         if not created:
        #             # dct:date
        #             for uri in g.subjects(RDF.type, SKOS.ConceptScheme):
        #                 for date in g.objects(uri, DCTERMS.date):
        #                     created = str(date)[:10]
        #         g.VOCABS[vocab_id]['created'] = created
        #
        #         # Date Modified
        #         modified = None
        #         for uri in g.subjects(RDF.type, SKOS.ConceptScheme):
        #             for date in g.objects(uri, DCTERMS.modified):
        #                 modified = str(date)[:10]
        #         g.VOCABS[vocab_id]['modified'] = modified
        #
        #         # Version
        #         version = None
        #         for uri in g.subjects(RDF.type, SKOS.ConceptScheme):
        #             for versionInfo in g.objects(uri, OWL.versionInfo):
        #                 version = versionInfo
        #         g.VOCABS[vocab_id]['version'] = version

    def list_collections(self):
        collections_uris = []
        collections = []
        for c in self.gr.subjects(predicate=RDF.type, object=SKOS.Collection):
            collections_uris.append(c)
        for collections_uri in collections_uris:
            for p, o in self.gr.predicate_objects(subject=collections_uri):
                if p in [SKOS.prefLabel, DCTERMS.title, RDFS.label]:
                    collections.append((
                        str(collections_uri), str(o)
                    ))
        return sorted(collections, key=lambda tup: tup[1])  # return sorted by prefLabel

    def list_concepts(self):
        vocabs = []
        # for s, p, o in self.g.triples((None, SKOS.inScheme, None)):
        #     label = ' '.join(str(s).split('#')[-1].split('/')[-1].split('_'))
        #     vocabs.append({
        #         'uri': str(s),
        #         'title': label
        #     })
        vocab = g.VOCABS[self.vocab_id]
        q = '''
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX dct: <http://purl.org/dc/terms/>
            SELECT DISTINCT 
                ?c          # 0
                ?pl         # 1
                ?d          # 2
                ?created    # 3
                ?modified   # 4
            WHERE {{
                ?c skos:inScheme <{concept_scheme_uri}> . 
                {{ 
                    ?c skos:prefLabel ?pl .
                    FILTER(lang(?pl) = "{language}" || lang(?pl) = "") 
                }}
                OPTIONAL {{ 
                    ?c skos:definition ?d .
                    FILTER(lang(?d) = "{language}" || lang(?d) = "") 
                }}
                OPTIONAL {{ 
                    ?c dct:created ?created . 
                }}
                OPTIONAL {{ 
                    ?c dct:modified ?modified . 
                }}
            }}
            ORDER BY ?pl
            '''.format(concept_scheme_uri=vocab.concept_scheme_uri, language=self.language)

        concepts = []
        for concept in self.gr.query(q):
            metadata = {
                'key': self.vocab_id,
                'uri': concept[0],
                'title': concept[1],
                'definition': concept[2] if concept[2] else None,
                'created': dateutil.parser.parse(concept[3]) if concept[3] else None,
                'modified': dateutil.parser.parse(concept[4]) if concept[4] else None
            }

            concepts.append(metadata)

        return concepts

    def get_collection(self):
        collection_uri = self.request.values.get('uri')
        prefLabel = None
        definition = None
        members_uris = []
        members = []
        source = None
        for p, o in self.gr.predicate_objects(subject=URIRef(collection_uri)):
            if p in [SKOS.prefLabel, DCTERMS.title, RDFS.label]:
                prefLabel = str(o)
            elif p in [SKOS.definition, DCTERMS.description, RDFS.comment]:
                definition = str(o)
            elif p == SKOS.member:
                members_uris.append(o)
            elif p == DCTERMS.source:
                source = str(o)

        for member_uri in members_uris:
            for o in self.gr.objects(subject=member_uri, predicate=SKOS.prefLabel):
                members.append({
                    'uri': str(member_uri),
                    'prefLabel': str(o)
                })

        return Collection(
            vocab_id=self.vocab_id,
            prefLabel=prefLabel,
            definition=definition,
            members=members,
            source=source,
        )

    def get_concept(self):
        concept_uri = self.request.values.get('uri')
        q = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX dct: <http://purl.org/dc/terms/>
            
            SELECT 
                ?predicate      # 0
                ?object         # 1
                ?predicateLabel # 2
                ?objectLabel    # 3
                ?prefLabel      # 4
            WHERE {{
                <{concept_uri}> ?predicate ?object .
                OPTIONAL {{
                    ?predicate rdfs:label ?predicateLabel .
                    FILTER(lang(?predicateLabel) = "{language}" || lang(?predicateLabel) = "")
                }}
                OPTIONAL {{
                    ?object skos:prefLabel|rdfs:label ?objectLabel .
                    # Don't filter prefLabel language
                    FILTER(?prefLabel = skos:prefLabel || lang(?objectLabel) = "{language}" || lang(?objectLabel) = "") 
                }}
            }}
            """.format(concept_uri=concept_uri, language=self.language)

        result = self.gr.query(q)

        assert result, 'FILE source is unable to query concepts for {}'.format(self.request.values.get('uri'))

        prefLabel = None

        related_objects = {}

        for r in result:
            predicateUri = str(r[0])

            # Special case for prefLabels
            if predicateUri == 'http://www.w3.org/2004/02/skos/core#prefLabel':
                predicateLabel = 'Multilingual Labels'
                preflabel_lang = 'en'  # because I don't know how to get lang out of an rdflib SPARQL query

                # Use default language or no language prefLabel as primary
                if (
                        (not prefLabel and not preflabel_lang)
                        or
                        (preflabel_lang == self.language)
                ):
                    prefLabel = str(r[1])  # Set current language prefLabel

                # # Omit current language string from list (remove this if we want to show all)
                # if preflabel_lang in ['', self.language]:
                #     continue

                # Apend language code to prefLabel literal
                related_object = '{} ({})'.format(str(r[1]), preflabel_lang)
                related_objectLabel = None
            else:
                predicateLabel = (str(r[2]) if r[2] is not None else h.make_title(str(r[0])))

                if not str(r[1]).startswith('http'):
                    related_object = str(r[1])
                    related_objectLabel = None
                else:
                    related_object = str(r[1])
                    related_objectLabel = (str(r[3]) if r[3] is not None else h.make_title(str(r[1])))

            relationship_dict = related_objects.get(predicateUri)
            if relationship_dict is None:
                relationship_dict = {'label': predicateLabel,
                                     'objects': {}}
                related_objects[predicateUri] = relationship_dict

            relationship_dict['objects'][related_object] = related_objectLabel

        related_objects = OrderedDict(
            [
                (
                    predicate, {
                        'label': related_objects[predicate]['label'],
                        'objects': OrderedDict(
                            [
                                (
                                    key,
                                    related_objects[predicate]['objects'][key]
                                ) for key in sorted(related_objects[predicate]['objects'].keys())
                             ]
                        )
                    }
                )
                for predicate in sorted(related_objects.keys())
            ]
        )

        return Concept(
            vocab_id=self.vocab_id,
            uri=concept_uri,
            prefLabel=prefLabel,
            related_objects=related_objects,
            semantic_properties=None,
            source=self,
        )

    def get_top_concepts(self):
        # same as parent query, only running against rdflig in-memory graph, not SPARQL endpoint
        vocab = g.VOCABS[self.vocab_id]
        q = '''
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            SELECT DISTINCT ?tc ?pl
            WHERE {{
                {{ GRAPH ?g 
                    {{
                        {{
                            <{concept_scheme_uri}> skos:hasTopConcept ?tc .                
                        }}
                        UNION 
                        {{
                            ?tc skos:topConceptOf <{concept_scheme_uri}> .
                        }}
                        {{ ?tc skos:prefLabel ?pl .
                            FILTER(lang(?pl) = "{language}" || lang(?pl) = "") 
                        }}
                    }}
                }}
                UNION
                {{
                    {{
                        <{concept_scheme_uri}> skos:hasTopConcept ?tc .                
                    }}
                    UNION 
                    {{
                        ?tc skos:topConceptOf <{concept_scheme_uri}> .
                    }}
                    {{ ?tc skos:prefLabel ?pl .
                        FILTER(lang(?pl) = "{language}" || lang(?pl) = "")
                    }}
                }}
            }}
            ORDER BY ?pl
            '''.format(concept_scheme_uri=vocab.concept_scheme_uri, language=self.language)
        top_concepts = Source.sparql_query(vocab.sparql_endpoint, q, vocab.sparql_username, vocab.sparql_password)

        if top_concepts is not None:
            # cache prefLabels and do not add duplicates. This prevents Concepts with sameAs properties appearing twice
            pl_cache = []
            tcs = []
            for tc in top_concepts:
                if tc[1] not in pl_cache:  # only add if not already in cache
                    tcs.append((tc[0], tc[1]))
                    pl_cache.append(tc[1])

            if len(tcs) == 0:
                q = '''
                    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                    SELECT DISTINCT ?tc ?pl
                    WHERE {{
                        {{ GRAPH ?g {{
                            {{
                                <{concept_scheme_uri}> skos:hasTopConcept ?tc .                
                            }}
                            UNION 
                            {{
                                ?tc skos:inScheme <{concept_scheme_uri}> .
                            }}
                            {{ ?tc skos:prefLabel ?pl .
                                FILTER(lang(?pl) = "{language}" || lang(?pl) = "") 
                            }}
                        }} }}
                        UNION
                        {{
                            {{
                                <{concept_scheme_uri}> skos:hasTopConcept ?tc .                
                            }}
                            UNION 
                            {{
                                ?tc skos:inScheme <{concept_scheme_uri}> .
                            }}
                            {{ ?tc skos:prefLabel ?pl .
                                FILTER(lang(?pl) = "{language}" || lang(?pl) = "")
                            }}
                        }}
                    }}
                    ORDER BY ?pl
                    '''.format(concept_scheme_uri=vocab.concept_scheme_uri, language=self.language)
                for tc in self.gr.query(q):
                    if tc[1] not in pl_cache:  # only add if not already in cache
                        tcs.append((tc[0], tc[1]))
                        pl_cache.append(tc[1])

            return tcs
        else:
            return None

    def get_concept_hierarchy(self):
        # same as parent query, only:
        #   running against rdflib in-memory graph, not SPARQL endpoint
        #   a single graph, not a multi-graph (since it's an RDF/XML or Turtle file)
        """
        Function to draw concept hierarchy for vocabulary
        """

        def build_hierarchy(bindings_list, broader_concept=None, level=0):
            """
            Recursive helper function to build hierarchy list from a bindings list
            Returns list of tuples: (<level>, <concept>, <concept_preflabel>, <broader_concept>)
            """
            level += 1  # Start with level 1 for top concepts
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
                                     and (binding_dict['broader_concept'] == broader_concept))
                                    ], key=lambda binding_dict: binding_dict['concept_preflabel'])

            for binding_dict in narrower_list:
                concept = binding_dict['concept']
                hierarchy += [(level,
                               concept,
                               binding_dict['concept_preflabel'],
                               binding_dict['broader_concept'] if binding_dict.get(
                                   'broader_concept') else None,
                               )
                              ] + build_hierarchy(bindings_list, concept, level)

            return hierarchy

        vocab = g.VOCABS[self.vocab_id]

        q = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX dct: <http://purl.org/dc/terms/>
            SELECT DISTINCT ?concept ?concept_preflabel ?broader_concept
            WHERE {{
                ?concept skos:inScheme <{vocab_uri}> .
                ?concept skos:prefLabel ?concept_preflabel .
                OPTIONAL {{ ?concept skos:broader ?broader_concept .
                    ?broader_concept skos:inScheme <{vocab_uri}> .
                    }}
                FILTER(lang(?concept_preflabel) = "{language}" || lang(?concept_preflabel) = "")
            }}
            ORDER BY ?concept_preflabel'''.format(vocab_uri=vocab.concept_scheme_uri, language=self.language)

        bindings_list = []
        for r in self.gr.query(q):
            bindings_list.append({
                # ?concept ?concept_preflabel ?broader_concept
                'concept': r[0],
                'concept_preflabel': r[1],
                'broader_concept': r[2],
            })

        assert bindings_list is not None, 'FILE concept hierarchy query failed'

        hierarchy = build_hierarchy(bindings_list)

        return Source.draw_concept_hierarchy(hierarchy, self.request, self.vocab_id)

    def get_object_class(self):
        uri = h.url_decode(self.request.values.get('uri'))
        for o in self.gr.objects(subject=URIRef(uri), predicate=RDF.type):
            return str(o)

    @staticmethod
    def load_pickle_graph(vocab_id):
        pickled_file_path = join(config.APP_DIR, 'data', 'vocab_files', vocab_id + '.p')
        if not os.path.isfile(pickled_file_path):  # no pickled file so re-make it
            if os.path.isfile(pickled_file_path.replace('.p', '.ttl')):
                gg = Graph().parse(pickled_file_path.replace('.p', '.ttl'), format='turtle')
            elif os.path.isfile(pickled_file_path.replace('.p', '.rdf')):
                gg = Graph().parse(pickled_file_path.replace('.p', '.rdf'), format='turtle')
            else:
                return None

            FILE.pickle_to_file(vocab_id, gg)

        try:
            with open(pickled_file_path, 'rb') as f:
                gr = pickle.load(f)
                f.close()
                return gr
        except Exception as e:
            print('EXCEPTION: ' + str(e))
            return None

    @staticmethod
    def pickle_to_file(vocab_id, g):
        logging.debug('Pickling file: {}'.format(vocab_id))
        path = os.path.join(config.APP_DIR, 'data', 'vocab_files', vocab_id)
        # TODO: Check if file_name already has extension
        with open(path + '.p', 'wb') as f:
            pickle.dump(g, f)
            f.close()

        g.serialize(path + '.ttl', format='turtle')


if __name__ == '__main__':
    details = {
        'vocab_files_folder_path': 'data/vocabs'
    }
    FILE.collect(details)
