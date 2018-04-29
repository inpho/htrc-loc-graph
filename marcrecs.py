import os.path
from glob import glob
from gzip import GzipFile

from pymarc.marcxml import parse_xml_to_array

def parse_file(stream):
    for rec in parse_xml_to_array(marcfile):
        lccns = [s.strip() for f in rec.get_fields('010') for s in f.get_subfields('a')]
        oclcs = [s.replace('(OCoLC)','').strip() for f in rec.get_fields('035')
                    for s in f.get_subfields('a') if '(OCoLC)' in s]
        lccs = [s.strip() for f in rec.get_fields('050') for s in f.get_subfields('a')]
        try:
            print ';'.join(lccns), ';'.join(oclcs), ';'.join(lccs)
        except UnicodeEncodeError:
            pass


if __name__ == '__main__':
    import sys

    root = os.path.join(sys.argv[-1], 'BooksAll.*.xml')
    for filename in glob(root + '.gz'):
        with GzipFile(filename) as marcfile:
            parse_file(marcfile)

    for filename in glob(root):
        with open(filename) as marcfile:
            parse_file(marcfile)
