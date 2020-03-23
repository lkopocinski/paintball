import logging
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
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


def load_impedance_table(path: Path):
    impedance_table = pd.read_csv(path, header=0, index_col=0, dtype=np.float64)

    has_missing_values = impedance_table.isna().values.any()
    if has_missing_values:
        raise ValueError("Impedance table malformed.")

    impedance_table.columns = impedance_table.columns.astype(int)
    impedance_table.index = impedance_table.index.astype(int)
    return impedance_table.T


def load_graph(path: Path):
    graph = BaseGraph()
    graph.unpickle(str(path))
    graph.generate_lemma_to_nodes_dict_lexical_units()
    return graph
