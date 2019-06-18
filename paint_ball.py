#!/usr/bin/python
# -*- coding: utf-8 -*-

import operator
import logging

import graph_tool as gt
from graph_tool.topology import label_largest_component

from collections import defaultdict, OrderedDict

logger = logging.getLogger(__name__)


def log(message):
    logger.info(message)


class Params(object):
    __slots__ = ['mikro', 'tau_0', 'epsilon', 'tau_3', 'tau_4']

    def __init__(self, mikro, tau_0, epsilon, tau_3, tau_4):
        self.mikro = mikro
        self.tau_0 = tau_0
        self.epsilon = epsilon
        self.tau_3 = tau_3
        self.tau_4 = tau_4

    def __str__(self):
        return "\tDecay - {}\n" \
               "\tTau 0 - {}\n" \
               "\tEpsilon - {}\n" \
               "\tTau 3 - {}\n" \
               "\tTau 4 - {}\n" \
            .format(
                self.mikro,
                self.tau_0,
                self.epsilon,
                self.tau_3,
                self.tau_4,
            )


class PaintBall:
    """
    µ (mikro) – a decay factor, defines what portion of activity is spread the next node, applied with each traversed
    link, in range (0, 1)

    τ0 (tau_0) – minimal activity level threshold

    ϵ (epsilon) – stop threshold defining the minimal activity level for sustaining further spreading
    let ϵ = τ0/4

    τ3 (tau_3) – strong support threshold

    τ4 (tau_4) – strong support threshold

    """

    def __init__(self, graph, params, impedance_table, knowledge_source, plwn):
        self.graph = graph

        self.decay = params.mikro
        self.tau_0 = params.tau_0
        self.epsilon = params.epsilon
        self.tau_4 = params.tau_4
        self.tau_3 = params.tau_3

        self._transmitance_dict = self.make_transmitance_dict()
        self._init_transmitance()
        self._impedance_table = impedance_table
        self._knowledge_source = knowledge_source

        self.plwn = plwn

    @staticmethod
    def make_transmitance_dict():
        transmitance = defaultdict(float)

        transmitance[11] = 1  # hypernymy
        transmitance[10] = 0.7  # hyponymy
        transmitance[12] = 0.4  # antonymy
        transmitance[14] = 0.6  # meronymy
        transmitance[15] = 0.6  # holonymy
        transmitance[13] = 1  # converse
        transmitance[53] = 0.7  # feminity
        transmitance[55] = 0.7  # young being
        transmitance[57] = 0.7  # augmentativity
        transmitance[888] = 1  # synonymy
        transmitance[777] = 1  # synonymy bis

        return transmitance

    def _init_transmitance(self, edge_weight=1.0):
        self.graph.create_edge_attribute('weight', 'float', value=edge_weight)

        for edge in self.graph.all_edges():
            try:
                edge.weight = self._transmitance_dict[edge.rel_id]
            except KeyError:
                edge.weight = 0

    def _setup_initial_activation(self, lemma_activations):
        Q = defaultdict(float)

        for la in lemma_activations:
            for node in la.nodes:
                Q[node] += la.activation

        T = {node: activation for node, activation in Q.items() if activation > self.tau_0}
        T = OrderedDict(sorted(T.items(), key=operator.itemgetter(1), reverse=True))
        return T

    def _act_replication(self, node, activation_value, Q):
        log("\n# NODE {} : {:>15} - activation: {:>3} - lu_id: {:>5} #".format(node, node.lu.lemma, activation_value, node.lu.lu_id))
        log("EDGES: ")
        for edge in node.all_edges():
            log("{:>20} ===> {:>20} lu_id: {:>5} node_id: {:>5} - weight: {:>3} - relation_id: {:>3} -".format(
                node.lu.lemma, edge.target().lu.lemma, edge.target().lu.lu_id, edge.target(), edge.weight, edge.rel_id))

        if activation_value < self.epsilon:
            log("Returning act_replication")
            return

        for edge in node.all_edges():
            self._act_rep_trans(node, edge, self._f_T(edge, self.decay * activation_value), Q)

    def _act_rep_trans(self, node, edge, activation_value, Q):
        if node == edge.target():
            log("The same")
            return
        node = edge.target()
        log("\n# NODE {} : {:>15} - activation: {:>3} - lu_id: {:>5} #".format(node, node.lu.lemma, activation_value, node.lu.lu_id))
        log("EDGES: ")
        for edge in node.all_edges():
            log("{:>20} ===> {:>20} lu_id: {:>5} node_id: {:>5} - weight: {:>3} - relation_id: {:>3} -".format(edge.source().lu.lemma, edge.target().lu.lemma, edge.target().lu.lu_id, edge.target(), edge.weight, edge.rel_id))

        if activation_value < self.epsilon:            
            log("Returning act_rep_trans")
            return

        for edge_prim in edge.target().all_edges():
            self._act_rep_trans(node, edge_prim, self._f_I(edge, edge_prim, self._f_T(edge_prim, self.decay * activation_value)), Q)

        Q[edge.target()] = Q[edge.target()] + activation_value

    def _f_T(self, edge, activation_value):
        return edge.weight * activation_value

    def _f_I(self, edge_in, edge_out, activation_value):
        val = self._get_impedance(edge_in.rel_id, edge_out.rel_id) * activation_value
        log("{} {} impedance {}  activation {} \n".format(edge_in.rel_id, edge_out.rel_id, val, activation_value))

        return self._get_impedance(edge_in.rel_id, edge_out.rel_id) * activation_value

    def _get_impedance(self, in_rel_id, out_rel_id):
        try:
            return self._impedance_table[in_rel_id][out_rel_id]
        except KeyError:
            return 1

    def find_place_in_graph(self, Q, syn_graph):
        Q_synset = self.synset_activation(Q)

        log("\nQ_synset:")
        for synset_id, activation in Q_synset.iteritems():
            log("{} {}".format(synset_id, activation))

        lead_nodes = self.find_subgraphs(Q_synset, syn_graph)
        return lead_nodes

    def synset_activation(self, Q):
        _Q_synset = defaultdict(float)

        for node, activation_value in Q.iteritems():
            synset_id = node.synset_id
            if synset_id != -1:
                _Q_synset[synset_id] += activation_value

        Q_synset = defaultdict(float)
        for synset_id, activation_value in _Q_synset.iteritems():
            activated = self._delta(1, activation_value, self.plwn.synset_len(synset_id))
            if activated:
                Q_synset[synset_id] = activation_value

        return Q_synset

    def find_subgraphs(self, Q_synset, syn_graph):
        nodes = dict()

        for syn_id, activation_value in Q_synset.iteritems():
            if activation_value > self.tau_3:
                try:
                    node = syn_graph.get_node_for_synset_id(syn_id)
                    nodes[node.use_graph_tool()] = node
                except Exception:
                    continue

        filt = syn_graph.use_graph_tool().new_vertex_property('boolean')
        for vertex, node in nodes.iteritems():
            filt[vertex] = True

        g = gt.GraphView(syn_graph.use_graph_tool(), filt)

        lead_nodes = []
        for graph in self.subgraphs(g):
            lead = None
            for vertex in graph.vertices():
                if not lead:
                    lead = nodes[vertex]
                else:
                    lead_id = lead.synset.synset_id
                    new_id = nodes[vertex].synset.synset_id
                    if Q_synset[lead_id] < Q_synset[new_id]:
                        lead = nodes[vertex]
            lead_nodes.append(lead)

        return lead_nodes

    def subgraphs(self, g):
        if g.num_vertices() == 0:
            raise StopIteration
        prop = label_largest_component(g, False)
        filt = g.new_vertex_property('boolean')
        for v in g.vertices():
            if prop[v] > 0:
                filt[v] = True
        yield gt.GraphView(g, filt)

        filt = g.new_vertex_property('boolean')
        for v in g.vertices():
            if prop[v] <= 0:
                filt[v] = True
        gv = gt.GraphView(g, filt)

        for sgv in self.subgraphs(gv):
            yield sgv

    def _delta(self, h, n, s):
        n_limit = 1.5  # 1.5
        n_limit_2 = 2  # 2

        if ((n >= n_limit * h) and (s <= 2)) or ((n >= n_limit_2 * h) and s > 2):
            return True
        else:
            return False

    def run(self, syn_graph):
        for source, targets_supports in self._knowledge_source.items():
            log("\nAttach - {} - to {} lemmas".format(source, len(targets_supports)))
            Q = defaultdict(float)

            lemma_activations = []
            for target, support in targets_supports:
                nodes = self.graph.lemma_to_nodes_dict[target]
                la = LemmaActivations(
                    lemma=target,
                    nodes=nodes,
                    activation=support
                )
                lemma_activations.append(la)

            T = self._setup_initial_activation(lemma_activations)

            for start_node, activation_value in T.items():
                self._act_replication(start_node, activation_value, Q)
            
            log("Q TABLE")
            log(Q)
            lead_nodes = self.find_place_in_graph(Q, syn_graph)

            print("\n\n# Attachment areas:")
            for node in lead_nodes:
                print("{};{};{};{}".format(source, node, node.synset.synset_id, [lu.lemma for lu in node.synset.lu_set]))


class LemmaActivations(object):
    __slots__ = ['lemma', 'nodes', 'activation']

    def __init__(self, lemma, nodes, activation):
        self.lemma = lemma
        self.nodes = nodes
        self.activation = float(activation)
