from pyldapi import Renderer, View
from flask import Response, render_template, g
from rdflib import Graph


class Collection:
    def __init__(
            self,
            vocab_id,
            prefLabel,
            definition,
            members,
            source,
    ):
        self.vocab_id = vocab_id
        self.prefLabel = prefLabel
        self.definition = definition
        self.members = members
        self.source = source


class CollectionRenderer(Renderer):
    def __init__(self, request, collection):
        self.views = self._add_skos_view()
        self.navs = []  # TODO: add in other nav items for Collection

        self.collection = collection

        super().__init__(
            request,
            request.values.get('uri'),
            self.views,
            'skos'
        )

    def _add_skos_view(self):
        return {
            'skos': View(
                'Simple Knowledge Organization System (SKOS)',
                'SKOS is a W3C recommendation designed for representation of thesauri, classification schemes, '
                'taxonomies, subject-heading systems, or any other type of structured controlled vocabulary.',
                ['text/html', 'application/json'] + self.RDF_MIMETYPES,
                'text/html',
                languages=['en'],  # default 'en' only for now
                namespace='http://www.w3.org/2004/02/skos/core#'
            )
        }

    def render(self):
        if self.view == 'alternates':
            return self._render_alternates_view()
        elif self.view == 'skos':
            if self.format in Renderer.RDF_MIMETYPES:
                return self._render_skos_rdf()
            else:
                return self._render_skos_html()

    def _render_skos_rdf(self):
        # get Collection RDF
        # TODO: re-assemble RDF from Concept object
        g = Graph()

        # serialise in the appropriate RDF format
        if self.format in ['application/rdf+json', 'application/json']:
            return g.serialize(format='json-ld')
        else:
            return g.serialize(format=self.format)

    def _render_skos_html(self):
        _template_context = {
            'vocab_id': self.request.values.get('vocab_id'),
            'vocab_title': g.VOCABS[self.request.values.get('vocab_id')].title,
            'uri': self.request.values.get('uri'),
            'collection': self.collection,
            'title': 'Collection: ' + self.collection.prefLabel,
            'navs': self.navs
        }

        return Response(
            render_template(
                'collection.html',
                **_template_context
            ),
            headers=self.headers
        )
