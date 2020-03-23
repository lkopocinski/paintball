#!/usr/bin/python3.8

import logging
import sys
from pathlib import Path

import click

from paintball.utils import parse_config
from paintball.knowledge_source import KnowledgeSource

from .constants import PAINT_BALL_GRAPH, IMPEDANCE_TABLE, SYNSETS_GRAPH
from .paint_ball import PaintBall, Params
from .plwn_utils import PLWN
from .utils import load_knowledge_source, load_graph, load_impedance_table

logging.basicConfig(level=logging.ERROR, format='%(message)s')
logger = logging.getLogger(__name__)


def log(message: str):
    logger.info(message)


@click.command()
@click.option('--config', required=True,
              type=click.Path(exists=True),
              help='Configuration file.')
def main(config):
    config = parse_config(Path(config))

    log("Loading knowledge source")
    knowledge_source = KnowledgeSource(config['knowledge_source'])

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
