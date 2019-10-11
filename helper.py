import urllib
import re
from rdflib import URIRef
import markdown
import os
import time
import pickle
import logging
import errno
import _config as config
from bs4 import BeautifulSoup
from flask import g

APP_DIR = os.path.dirname(os.path.abspath(__file__))


def render_concept_tree(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')

    #concept_hierarchy = soup.find(id='concept-hierarchy')

    uls = soup.find_all('ul')

    for i, ul in enumerate(uls):
        # Don't add HTML class nested to the first 'ul' found.
        if not i == 0:
            ul['class'] = 'nested'
            if ul.parent.name == 'li':
                temp = BeautifulSoup(str(ul.parent.a.extract()), 'html.parser')
                ul.parent.insert(0, BeautifulSoup('<span class="caret">', 'html.parser'))
                ul.parent.span.insert(0, temp)
    return soup


def url_encode(s):
    try:
        return urllib.parse.quote(s)
    except:
        pass


def url_decode(s):
    try:
        return urllib.parse.unquote(s)
    except:
        pass


def make_title(s):
    # make title from URI
    title = ' '.join(s.split('#')[-1].split('/')[-1].split('_')).title()

    # replace dashes and periods with whitespace
    title = re.sub('[-\.]+', ' ', title).title()

    return title


def parse_markdown(s):
    return markdown.markdown(s)


def is_email(email):
    """
    Check if the email is a valid email.
    :param email: The email to be tested.
    :return: True if the email matches the static regular expression, else false.
    :rtype: bool
    """
    pattern = r"[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
    return True if re.search(pattern, email) is not None else False


def strip_mailto(email):
    return email[7:]


def contains_mailto(email):
    if email[:7] == 'mailto:':
        return True
    return False


def is_url(url):
    """
    Check if the url is a valid url.
    :param url: The url to be tested.
    :type url: str
    :return: True if the url passes the validation, else false.
    :rtype: bool
    """
    if isinstance(url, URIRef):
        return True

    pattern = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return True if re.search(pattern, url) is not None else False

def cache_read(cache_file_name):
    '''
    Function to read object from cache if cache file is younger than cache_hours. Returns None on failure
    '''
    cache_seconds = config.VOCAB_CACHE_HOURS * 3600
    cache_file_path = os.path.join(config.VOCAB_CACHE_DIR, cache_file_name)
    
    if os.path.isfile(cache_file_path):
        # if the cache file is younger than cache_hours days, then try to read it
        cache_file_age = time.time() - os.stat(cache_file_path).st_mtime
        logging.debug('Cache file age: {0:.2f} hours'.format(cache_file_age / 3600))
        # if the cache file is older than VOCAB_CACHE_HOURS, ignore it
        if cache_file_age <= cache_seconds:
            try:
                with open(cache_file_path, 'rb') as f:
                    cache_object = pickle.load(f)
                    f.close()
                if cache_object: # Ignore empty file
                    logging.debug('Read cache file {}'.format(os.path.abspath(cache_file_path)))
                    return cache_object
            except Exception as e:
                logging.debug('Unable to read cache file {}: {}'.format(os.path.abspath(cache_file_path), e))
                pass
        else:
            logging.debug('Ignoring old cache file {}'.format(os.path.abspath(cache_file_path)))
        
    return

def cache_write(cache_object, cache_file_name):
    '''
    Function to write object to cache if cache file is older than cache_hours.
    '''
    cache_seconds = config.VOCAB_CACHE_HOURS * 3600
    cache_file_path = os.path.join(config.VOCAB_CACHE_DIR, cache_file_name)
    
    if os.path.isfile(cache_file_path):
        # if the cache file is older than VOCAB_CACHE_HOURS days, delete it
        cache_file_age = time.time() - os.stat(cache_file_path).st_mtime
        # if the cache file is older than VOCAB_CACHE_HOURS days, delete it
        if cache_seconds and cache_file_age > cache_seconds:
            logging.debug('Removing old cache file {}'.format(os.path.abspath(cache_file_path)))
            os.remove(cache_file_path)
        else:
            logging.debug('Retaining recent cache file {}'.format(os.path.abspath(cache_file_path)))
            return # Don't do anything - cache file is too young to die

    try:
        os.makedirs(config.VOCAB_CACHE_DIR)
        logging.debug('Cache directory {} created'.format(os.path.abspath(config.VOCAB_CACHE_DIR)))
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(config.VOCAB_CACHE_DIR):
            pass
        else:
            raise   
        
    if cache_object: # Don't write empty file
        with open(cache_file_path, 'wb') as cache_file:
            pickle.dump(cache_object, cache_file)
            cache_file.close()
        logging.debug('Cache file {} written'.format(cache_file_path))
    else:
        logging.debug('Empty object ignored')
         
def get_vocab_id_from_uri(concept_uri):
    '''
    Helper function to find the ID of a known vocab from a concept URI. Returns None if no match found.
    '''
    candidate_vocabs = {vocab_id: vocab for vocab_id, vocab in g.VOCABS.items()
                        if vocab.uri in concept_uri}
    
    # Deal with case where vocab URI has same root as concepts, e.g. 'https://data.naa.gov.au/def/agift/AGIFT'
    if not candidate_vocabs:
        candidate_vocabs = {vocab_id: vocab for vocab_id, vocab in g.VOCABS.items()
                            if os.path.dirname(vocab.uri) in concept_uri}
    
    matched_vocab_id = None
    
    longest_vocab_uri_length = 0
    for vocab_id, vocab in candidate_vocabs.items():
        if len(vocab.uri) > longest_vocab_uri_length:
            matched_vocab_id = vocab_id
            longest_vocab_uri_length = len(vocab.uri)
    
    return matched_vocab_id
        
    
    
    
    