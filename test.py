from collections import namedtuple
import logging
import string
import sys

import rdflib
import skos

# https://www.filosophy.org/post/32/python_function_execution_deadlines__in_simple_examples/
import signal
def deadline(timeout, *args):
    def decorate(f):
        def handler(signum, frame):
            raise RuntimeError("Function Timed Out")

        def new_f(*args):

            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout)
            return f(*args)
            signa.alarm(0)

        new_f.__name__ = f.__name__
        return new_f
    return decorate

LCCO_URI = 'http://inkdroid.org/lcco/'
LCC = namedtuple('LCC', ['cls', 'subcls', 'topic'])

# create RDF graph
graph = rdflib.Graph()
with open('data/lcco.rdf') as skosfile:
    graph.parse('data/lcco.rdf')

# create SKOS representation
loader = skos.RDFLoader(graph)

def parse_lcc(lcc):
    cls = lcc[0]
    if len(lcc) > 1:
        if len(lcc) > 2 and lcc[1] in string.uppercase and lcc[2] in string.uppercase:
            subcls = lcc[1:3]
            topic = lcc[3:]
        elif lcc[1] in string.uppercase:
            subcls = lcc[1]
            topic = lcc[2:]
        else:
            subcls = None
            topic = lcc[1:]
    else:
        subcls = None
        topic = None
    return LCC(cls, subcls, topic)

def get_closest(lcc):
    # FIRST SELECT CLOSEST
    if loader.get(LCCO_URI + lcc, False):
        closest = lcc

    parsed = parse_lcc(lcc)
    if parsed.cls != 'E' and parsed.cls != 'F':
        cur_uri = LCCO_URI + parsed.cls
    else:
        cur_uri = LCCO_URI + 'E-F'

    next_uri = [narrow for narrow, obj in loader[cur_uri].narrower.iteritems()
                    if in_range(lcc,str(obj.notation))]

    while next_uri:
        cur_uri = next_uri[0]
        next_uri = [narrow for narrow, obj in loader[cur_uri].narrower.iteritems() 
                        if in_range(lcc,str(obj.notation))]

    return str(loader[cur_uri].notation)

def get_next(lcc, find_closest=True):
    closest = get_closest(lcc) if find_closest else lcc
    closest_uri = LCCO_URI + closest
    if loader[closest_uri].broader:
        return str(loader[closest_uri].broader.values()[0].notation)
    else:
        return ''
    
def in_range(lcc, candidate):
    lcc = parse_lcc(lcc)
    candidate = parse_lcc(candidate)
    if lcc.cls != candidate.cls:
        if (lcc.cls == 'E' or lcc.cls =='F') and candidate.cls == 'E-F':
            return True
        return False
    elif candidate.subcls and lcc.subcls != candidate.subcls:
        return False
    elif not candidate.subcls and candidate.topic and lcc.subcls:
        return False
    elif candidate.topic:
        if not lcc.topic:
            return False
        elif lcc.topic == candidate.topic:
            return True
        elif ' ' in candidate.topic:
            return False
        elif '-' in candidate.topic and '-' not in lcc.topic:
            topic_range = candidate.topic.split('-')
            if '.' in topic_range[0]:
                topic_range[0] = topic_range[0].split('.')[0]
            if '.' in topic_range[1]:
                if topic_range[1].startswith('.'): 
                    topic_range[1] = topic_range[0]
                else:
                    topic_range[1] = topic_range[1].split('.')[0]
            if topic_range[1] and topic_range[1][0] not in string.digits:
                topic_range[1] = topic_range[0]
            if '.' in lcc.topic:
                topic = lcc.topic.split('.')[0]
            else: 
                topic = lcc.topic
            topic_range[0] = topic_range[0].replace('(','').replace(')', '')
            topic_range[1] = topic_range[1].replace('(','').replace(')', '')
            return int(topic_range[0]) <= int(topic) <= int(topic_range[1])
        elif '-' in candidate.topic and '-' in lcc.topic:
            lcc_range = lcc.topic.split('-')
            topic_range = candidate.topic.split('-')
            if '.' in topic_range[0]:
                topic_range[0] = topic_range[0].split('.')[0]
            if '.' in topic_range[1]:
                if topic_range[1].startswith('.'): 
                    topic_range[1] = topic_range[0]
                else:
                    topic_range[1] = topic_range[1].split('.')[0]
            if topic_range[1] and topic_range[1][0] not in string.digits:
                topic_range[1] = topic_range[0]
            if '.' in lcc_range[0]:
                lcc_range[0] = lcc_range[0].split('.')[0]
            if '.' in lcc_range[1]:
                if lcc_range[1].startswith('.'): 
                    lcc_range[1] = lcc_range[0]
                else:
                    lcc_range[1] = lcc_range[1].split('.')[0]
            if lcc_range[1] and lcc_range[1][0] not in string.digits:
                lcc_range[1] = lcc_range[0]
            topic_range[0] = topic_range[0].replace('(','').replace(')', '')
            topic_range[1] = topic_range[1].replace('(','').replace(')', '')
            lcc_range[0] = lcc_range[0].replace('(','').replace(')', '')
            lcc_range[1] = lcc_range[1].replace('(','').replace(')', '')
            return int(topic_range[0]) <= int(lcc_range[0])\
                    and int(lcc_range[1]) <= int(topic_range[1])
            
        else:
            return False
    else:
        return True

@deadline(1)
def get_cats(cat):
    cats = [cat]
    try:
        cat = get_closest(cat)
    except KeyError:
        return []

    while cat:
        new_cat = get_next(cat, False)
        if cat != new_cat:
            cats.append(cat)
            cat = new_cat
        else:
            break

    if len(cats) > 1 and cats[0] == cats[1]:
        return cats[1:]
    else:
        return cats

if __name__ == '__main__':
    import sys
    from itertools import chain
    BLACKLIST = []
    with open(sys.argv[-1]) as infile:    
        for row in infile:
            row = row.strip().split('\t')
            print row[0], row[-1],
            cats = []
            for cat in row[-1].split(';'):
                cat = cat.upper()
                try:
                    if cat not in BLACKLIST:
                        cats.extend(get_cats(cat))
                except (ValueError, RuntimeError) as e:
                    BLACKLIST.append(cat)
            print len(cats), ';'.join(cats)

    for item in sorted(BLACKLIST):
        print item
