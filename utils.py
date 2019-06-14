from collections import defaultdict

from graph import BaseGraph


def load_knowledge_source(file_path):
    ks_dict = defaultdict(list)

    with open(file_path, 'r') as f:
        for line in f:
            source, target, support = line.strip().split(';')
            ks_dict[source].append((target, support))

    return ks_dict


def prepare_graph(graph_path):
    graph = BaseGraph()
    graph.unpickle(graph_path)
    graph.generate_lemma_to_nodes_dict_lexical_units()
    return graph
