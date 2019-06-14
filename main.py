#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from constants import PAINT_BALL_GRAPH, IMPEDANCE_TABLE, SYNSETS_GRAPH
from utils import load_knowledge_source, load_graph, load_impedance_table
from paint_ball import PaintBall, Params
from plwn_utils import PLWN


def main():
    knowledge_source = load_knowledge_source(sys.argv[1])
    graph = load_graph(PAINT_BALL_GRAPH)
    impedance_table = load_impedance_table(IMPEDANCE_TABLE)

    params = Params(
        mikro=0.95,
        tau_0=0.5,
        epsilon=0.05,
        tau_3=2.5,
        tau_4=1
    )

    pb = PaintBall(
        graph=graph,
        params=params,
        impedance_table=impedance_table,
        knowledge_source=knowledge_source,
        plwn=PLWN()
    )

    syn_graph = load_graph(SYNSETS_GRAPH)
    pb.run(syn_graph)


if __name__ == '__main__':
    main()
