from __future__ import print_function

import json
import os
import os.path

from jq import jq
import bz2file as bz2

PATH = '/media/jammurdo/HTRC/efs/'
JQ_TRANSFORM = '{"htid" : .metadata.volumeIdentifier, "lccn" : .metadata.lccn, "oclc" : .metadata.oclc}'

for root, dirs, files in os.walk(PATH):
    for filename in files:
        filename = os.path.join(root, filename)
        with bz2.BZ2File(filename) as bzfile:
            data = jq(JQ_TRANSFORM).transform(text=bzfile.read().decode('utf8'))
            print(data['htid'], ';'.join(data['lccn']), ';'.join(data['oclc']))

