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

vals = [(str(v.notation), str(v.prefLabel)) 
            for v in loader.values() if isinstance(v, skos.Concept)]
for v in vals:
    print '\t'.join(v)
