
counts = dict()

with open('htcounts.txt') as countfile:
    for line in countfile:
        line = line.strip()
        if len(line.rsplit(' ', 1)) >= 2:
            area, count = line.rsplit(' ', 1)
            if count != '-':
                counts[area] = int(count)
'''
import logging
logging.basicConfig()
'''

import lcco
import networkx as nx
g = nx.Graph()
g.add_node("LoC", weight=max(counts.values()))
for node, count in counts.iteritems():
    g.add_node(node, weight=count)

for area in counts.keys():
    uri = lcco.LCCO_URI + area
    if lcco.loader.get(uri) and not lcco.loader.get(uri).broader:
        g.add_edge(area, "LoC")
    elif lcco.loader.get(uri):
        super_area = lcco.loader.get(uri).broader.keys()[0]
        super_area = super_area.replace(lcco.LCCO_URI, '')
        g.add_edge(area, super_area)


SHELLS = [["LoC"], [], [], []]
NODES = []
for node, data in g.nodes(data=True):
    try:
        if len(nx.shortest_path(g, node, "LoC")) > 4:
            NODES.append(node)
        elif not data['weight']:
            NODES.append(node)
        else:
            p = nx.shortest_path(g, node, "LoC")
            SHELLS[len(p)-1].append(node)
    except nx.exception.NetworkXNoPath:
        NODES.append(node)

print len(NODES)
g.remove_nodes_from(NODES)
g.remove_node("LoC")
import matplotlib.pyplot as plt
import math

plt.figure(figsize=(12,12))
pos = nx.spring_layout(g)
weights = [d['weight'] ** 0.5 for n,d in g.nodes(data=True)]
nx.draw_networkx_nodes(g, pos, alpha=0.25, node_size=weights)
nx.draw_networkx_edges(g, pos)
plt.show()
nx.write_gml(g, "htrc-loc.gml")

