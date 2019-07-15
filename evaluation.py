import os

from collections import defaultdict
from graph import BaseGraph
from graph_tool.topology import shortest_distance
import sys

SYNSETS_GRAPH = 'res/plwn_synsets_graph.xml.gz'
RESULTS_PATH = sys.argv[1]


def load_graph(path):
    graph = BaseGraph()
    graph.unpickle(path)
    graph.generate_lemma_to_nodes_dict_synsets()
    return graph


def results_to_dict(path):
    results_dict = defaultdict(list)

    with open(path, 'r') as f:
        for line in f:
            try:
                lemma, target_syns_id, _ = line.split(';')
            except:
                continue
            results_dict[lemma].append(target_syns_id)

    return results_dict


def main():
    results_dict = results_to_dict(RESULTS_PATH)
    graph = load_graph(SYNSETS_GRAPH)

    for source_lemma, targets_synset_ids in results_dict.iteritems():
        for source_node in graph._lemma_to_nodes_dict[source_lemma]:

            distances = []
            for target_synset_id in targets_synset_ids:
                target_vertex = graph.get_node_for_synset_id(int(target_synset_id))
                distance = shortest_distance(graph.use_graph_tool(), source_node, target_vertex, max_dist=6, directed=False)
                distances.append(distance)

            min_dist = min(distances)
            if min_dist > 6:
                min_dist = -1

            print("{},{}".format(source_lemma, min_dist))


if __name__ == '__main__':
    main()
