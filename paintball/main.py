#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sys

from .constants import PAINT_BALL_GRAPH, IMPEDANCE_TABLE, SYNSETS_GRAPH
from .paint_ball import PaintBall, Params
from .plwn_utils import PLWN
from .utils import load_knowledge_source, load_graph, load_impedance_table

logging.basicConfig(level=logging.ERROR, format='%(message)s')
logger = logging.getLogger(__name__)


def log(message):
    logger.info(message)


def main():
    log("Loading knowledge source")
    knowledge_source = load_knowledge_source(sys.argv[1])

    log("Loading paintball graph")
    graph = load_graph(PAINT_BALL_GRAPH)
    # graph = None

    log("Loading impedance table")
    impedance_table = load_impedance_table(IMPEDANCE_TABLE)

    log("\nSetting params:")
    params = Params(
        mikro=0.80,
        tau_0=0.45,
        epsilon=(0.5 / 4),
        tau_3=1.2,
        tau_4=1
    )
    log(params)

    pb = PaintBall(
        graph=graph,
        params=params,
        impedance_table=impedance_table,
        knowledge_source=knowledge_source,
        plwn=PLWN()
    )

    log("Loading synsets graph")
    syn_graph = load_graph(SYNSETS_GRAPH)

    log("Run algorithm")
    pb.run(syn_graph)


if __name__ == '__main__':
    main()
