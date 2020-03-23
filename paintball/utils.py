import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict

import yaml
from graph import BaseGraph

logging.basicConfig(level=logging.ERROR, format='%(message)s')
logger = logging.getLogger(__name__)


def parse_config(path: Path) -> Dict:
    with path.open('r', encoding='utf-8') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exception:
            logger.exception(exception)


def load_knowledge_source(path):
    ks_dict = defaultdict(list)

    with open(path, 'r') as f:
        for line in f:
            source, target, support = line.strip().split(';')
            ks_dict[source].append((target, support))

    return ks_dict


def load_impedance_table(path):
    it = defaultdict(lambda: defaultdict(float))

    with open(path) as f:
        headers = f.readline().strip().split(',')
        headers = [h.strip() for h in headers]

        for l in f:
            l = l.strip().split(',')
            row = l[0].strip()
            row = int(row)
            it[row] = defaultdict(float)
            for i in range(1, len(headers)):
                it[row][int(headers[i])] = float(l[i])

    return it


def load_graph(graph_path):
    graph = BaseGraph()
    graph.unpickle(graph_path)
    graph.generate_lemma_to_nodes_dict_lexical_units()
    return graph
