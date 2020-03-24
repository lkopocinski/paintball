#!/usr/bin/python3.8

import logging
from pathlib import Path

import click

from paintball.knowledge_source import KnowledgeSource
from paintball.utils import parse_config, load_transmittance, load_graph, \
    load_impedance_table
from .paint_ball import PaintBall, Params
from .plwn_utils import PLWN

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
    knowledge_source = KnowledgeSource(
        source_dir=Path(config['knowledge_source'])
    )

    log("Loading graph")
    graph = load_graph(path=Path(config['graph']))

    log("Loading impedance table")
    impedance_table = load_impedance_table(
        path=Path(config['impedance_table'])
    )

    log("Loading transmittance table")
    transmittance_table = load_transmittance(
        path=Path(config['transmittance_table'])
    )

    log("Setting params")
    params = Params(**config['params'])

    pb = PaintBall(
        graph=graph,
        params=params,
        knowledge_source=knowledge_source,
        impedance_table=impedance_table,
        transmittance_table=transmittance_table,
        plwn=PLWN()
    )

    log("Loading synset graph")
    synset_graph = load_graph(path=Path(config['synset_graph']))

    log("Run algorithm")
    pb.run(synset_graph)


if __name__ == '__main__':
    main()
