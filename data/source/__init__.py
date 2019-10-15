import sys
from ._source import Source
from .FILE import *
from .GITHUB import *
from .RVA import *
from .SPARQL import *
from .VOCBENCH import *

def get_source_class(vocab_id):
    '''
    Function to return Source subclass corresponding to vocab_id
    '''
    return getattr(sys.modules[__name__], g.VOCABS.get(vocab_id).data_source)

