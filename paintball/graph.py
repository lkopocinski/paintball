#!/usr/bin/python3.8
import logging
from collections import defaultdict
from typing import Iterator, List

import graph_tool as gt
from graph_tool import Graph, load_graph, Vertex, Edge
from graph_tool.generation import graph_union


class BaseNode:
    __slots__ = ['_graph', '_node']

    def __init__(self, graph: Graph, node: Vertex):
        """
        Args:
            graph (graph_tool.Graph): graph to which the node belongs
            node  (graph_tool.Vertex): underlying node
        """
        self._graph = graph
        self._node = node

    def use_graph_tool(self):
        """Returns underlying graph_tool.Vertex.

        It should be avoided at all costs.
        """
        return self._node

    def all_edges(self) -> Iterator[BaseEdge]:
        for edge in self._node.all_edges():
            yield BaseEdge(self._graph, edge)

    def all_neighbours(self) -> Iterator[BaseNode]:
        for neighbour in self._node.all_neighbours():
            yield BaseNode(self._graph, neighbour)

    def in_degree(self):
        return self._node.in_degree()

    def out_degree(self):
        return self._node.out_degree()

    def __getattr__(self, name: str):
        """Allows access to properties of graph."""
        return self._graph.vp[name][self._node]

    def __setattr__(self, name: str, value):
        """Allows access to properties of graph."""
        if name in self.__slots__:
            super(BaseNode, self).__setattr__(name, value)
        else:
            self._graph.vp[name][self._node] = value

    def __eq__(self, another):
        if isinstance(another, BaseNode):
            return self._node == another._node and self._graph == another._graph
        return self._node == another

    def __ne__(self, another):
        if isinstance(another, BaseNode):
            return self._node != another._node or self._graph != another._graph
        return self._node != another

    def __hash__(self):
        return hash(self._node)

    def __str__(self):
        return str(self._node)

    def __repr__(self):
        return repr(self._node)

    def __int__(self):
        return int(self._node)

    def copy(self):
        return BaseNode(self._graph, self._node)


class BaseEdge:
    __slots__ = ['_graph', '_edge']

    def __init__(self, graph: Graph, edge: Edge):
        """
        Args:
            graph (graph_tool.Graph): graph to which the edge belongs
            edge  (graph_tool.Edge): underlying edge
        """
        self._graph = graph
        self._edge = edge

    def use_graph_tool(self):
        """Returns underlying graph_tool.Edge.

        It should be avoided at all costs.
        """
        return self._edge

    def __getattr__(self, name):
        """Allows access to properties of graph."""
        return self._graph.ep[name][self._edge]

    def __setattr__(self, name, value):
        """Allows access to properties of graph."""
        if name in self.__slots__:
            super(BaseEdge, self).__setattr__(name, value)
        else:
            self._graph.ep[name][self._edge] = value

    def __eq__(self, another):
        return self._edge == another._edge and self._graph == another._graph

    def __ne__(self, another):
        return self._edge != another._edge or self._graph != another._graph

    def __hash__(self):
        return hash(self._edge)

    def __str__(self):
        return str(self._edge)

    def __repr__(self):
        return repr(self._edge)

    def copy(self):
        return BaseEdge(self._graph, self._edge)

    def source(self):
        return BaseNode(self._graph, self._edge.source())

    def target(self):
        return BaseNode(self._graph, self._edge.target())


class BaseGraph:
    """Class representing a graph.

    We do not use pure graph_tool.Graph because we want
    to be able to easily change this library. Neither we use inheritance
    as graph_tool has inconvenient licence.
    """

    def __init__(self):
        self._graph = None
        self._node_dict = {}
        self._syn_to_vertex_map = None
        self._lemma_to_nodes_dict = None
        self._lu_on_vertex_dict = None

    def use_graph_tool(self):
        """Returns underlying graph_tool.Graph.

        It should be avoided at all costs.
        """
        return self._graph

    def get_node_for_synset_id(self, syn_id):
        """
        Lazy function to makes the map of synset identifiers to nodes into
        the graph. The building of map is made only on the first function call.
        The first and the next calls of this function will return the built map.
        """
        if not self._syn_to_vertex_map:
            self._syn_to_vertex_map = {}
            for node in self.all_nodes():
                if node.synset:
                    synset_id = node.synset.synset_id
                    self._syn_to_vertex_map[synset_id] = node
        return self._syn_to_vertex_map.get(syn_id, None)

    def pickle(self, filename):
        self._graph.save(filename)

    def unpickle(self, filename):
        self._graph = load_graph(filename)

    def init_graph(self, drctd=False):
        self._graph = Graph(directed=drctd)

    def copy_graph_from(self, g):
        self._graph = g._g.copy()

    def set_directed(self, drctd):
        self._graph.set_directed(drctd)

    def is_directed(self):
        return self._graph.is_directed()

    def merge_graphs(self, g1: BaseGraph, g2: BaseGraph):
        self._graph = graph_union(g1._graph, g2._graph, internal_props=True)

    # Node operations:
    def all_nodes(self):
        for node in self._graph.vertices():
            yield BaseNode(self._graph, node)

    def create_node_attribute(self, name, kind, value=None):
        if not self.has_node_attribute(name):
            node_attr = self._graph.new_vertex_property(kind, value)
            self._graph.vertex_properties[name] = node_attr

    def create_node_attributes(self, node_attributes: List):
        for attr in node_attributes:
            if not self.has_node_attribute(attr[0]):
                node_attr = self._graph.new_vertex_property(attr[1])
                self._graph.vertex_properties[attr[0]] = node_attr

    def has_node_attribute(self, name):
        """ Checks if a node attribute already exists """
        return name in self._graph.vertex_properties

    def delete_node_attribute(self, name):
        """ Delete node attribute """
        del self._graph.vertex_properties[name]

    def add_node(self, name, node_attributes_list=None):
        if node_attributes_list is None:
            node_attributes_list = []

        if name not in self._node_dict:
            new_node = self._graph.add_vertex()
            self._node_dict[name] = BaseNode(self._graph, new_node)
            for attr in node_attributes_list:
                self._graph.vertex_properties[attr[0]][new_node] = attr[1]
        return self._node_dict[name]

    def get_node(self, name):
        return self._node_dict[name]

    def remove_node(self, name):
        self._graph.remove_vertex(self._node_dict[name]._node)
        del self._node_dict[name]

    def nodes_filter(self, nodes_to_filter_set, inverted=False,
                     replace=False, soft=False):
        """
        Filters out nodes from set

        Args:
          nodes_to_filter_set (Iterable): Nodes which fill be filtered out.
          inverted (bool): If True, nodes NOT in set will be filtered out.
            Defaults to False.
          replace (bool): Replace current filter instead of combining the two.
            Defaults to False.
          soft (bool): Hide nodes without removing them so they can be restored
            with reset_nodes_filter. Defaults to False.
        """
        predicate = lambda node: node not in nodes_to_filter_set
        self.nodes_filter_conditional(predicate, inverted, replace, soft)

    def nodes_filter_conditional(self, predicate, inverted=False,
                                 replace=False, soft=False):
        """
        Filters node based on a predicate

        Args:
          predicate (Callable): Predicate returning False for nodes that should be
            filtered out.
          inverted (bool): Invert condition. Defaults to False.
          replace (bool): Replace current filter instead of combining the two.
            Defaults to False.
          soft (bool): Hide nodes without removing them so they can be restored
            with reset_nodes_filter. Defaults to False.
        """

        (old_filter, old_inverted) = self._graph.get_vertex_filter()
        new_filter = self._graph.new_vertex_property("bool")

        for node in self.all_nodes():
            kept = predicate(node) != inverted
            if not replace and old_filter:
                old_kept = bool(old_filter[node._node]) != old_inverted
                kept = kept and old_kept
            new_filter[node._node] = kept

        self._graph.set_vertex_filter(new_filter, False)
        if not soft:
            self.apply_nodes_filter()

    def apply_nodes_filter(self):
        """Removes nodes that are currently filtered out."""
        self._graph.purge_vertices()

    def reset_nodes_filter(self):
        """Clears node filter."""
        self._graph.set_vertex_filter(None)

    # Edge operations:
    def num_edges(self):
        return self._graph.num_edges()

    def all_edges(self):
        for edge in self._graph.edges():
            yield BaseEdge(self._graph, edge)

    def get_edges_between(self, source, target):
        """
        Return all edges between source and target.
        Source and target can be either BaseNode or integer.
        """
        if isinstance(source, BaseNode):
            source = source._node
        if isinstance(target, BaseNode):
            target = target._node
        for e in self._graph.edge(source, target, all_edges=True):
            yield BaseEdge(self._graph, e)

    def get_edge(self, source, target, add_missing=False):
        """
        Return some edge between source and target. Source and target can be either
        BaseNode or integer.
        """
        if isinstance(source, BaseNode):
            source = source._node
        if isinstance(target, BaseNode):
            target = target._node
        e = self._graph.edge(source, target, add_missing)
        if e is not None:
            return BaseEdge(self._graph, e)
        else:
            return None

    def create_edge_attribute(self, name, kind, value=None):
        if not self.has_edge_attribute(name):
            edge_attr = self._graph.new_edge_property(kind, value)
            self._graph.edge_properties[name] = edge_attr

    def alias_edge_attribute(self, name, alias):
        self._graph.edge_properties[alias] = self._graph.edge_properties[name]

    def create_edge_attributes(self, edge_attributes_list):
        for attr in edge_attributes_list:
            if not self.has_edge_attribute(attr[0]):
                edge_attr = self._graph.new_edge_property(attr[1])
                self._graph.edge_properties[attr[0]] = edge_attr

    def has_edge_attribute(self, name):
        """ Checks if an edge attribute already existst """
        return name in self._graph.edge_properties

    def delete_edge_attribute(self, name):
        """ Delete edge attribute """
        del self._graph.edge_properties[name]

    def add_edge(self, parent, child, edge_attributes_list=None):
        if edge_attributes_list is None:
            edge_attributes_list = []

        new_edge = self._graph.add_edge(parent._node, child._node)
        for attr in edge_attributes_list:
            self._graph.edge_properties[attr[0]][new_edge] = attr[1]

        return BaseEdge(self._graph, new_edge)

    def edges_filter(self, edges_to_filter_set):
        edge_filter = self._graph.new_edge_property("bool")

        for e in self.all_edges():
            if e in edges_to_filter_set:
                edge_filter[e._edge] = False
            else:
                edge_filter[e._edge] = True

        self._graph.set_edge_filter(edge_filter)
        self._graph.purge_edges()

    def ungraph_tool(self, thingy, lemma_on_only_synset_node_dict):
        """
        Converts given data structure so that it no longer have any graph_tool dependencies.
        """
        logger = logging.getLogger(__name__)

        if type(thingy) == dict:
            return {
                self.ungraph_tool(k, lemma_on_only_synset_node_dict):
                    self.ungraph_tool(thingy[k], lemma_on_only_synset_node_dict)
                for k in thingy}

        nodes_to_translate = set()
        for vset in lemma_on_only_synset_node_dict.values():
            for v in vset:
                nodes_to_translate.add(v)

        if type(thingy) == gt.PropertyMap:
            dct = {}
            if thingy.key_type() == 'v':
                for node in nodes_to_translate:
                    dct[node] = thingy[node.use_graph_tool()]
            elif thingy.key_type() == 'e':
                for edge in self.all_edges():
                    dct[edge] = thingy[edge.use_graph_tool()]
            else:
                logger.error('Unknown property type %s', thingy.key_type())
                raise NotImplemented
            return dct

    def generate_lemma_to_nodes_dict_synsets(self):
        """
        This method generates a utility dictionary, which maps lemmas to
        corresponding node objects. It is expensive in means of time
        needed to generate the dictionary. It should therefore be executed
        at the beginning of the runtime and later its results should be reused
        as many times as needed without re-executing the function.
        """
        lemma_to_nodes_dict = defaultdict(set)
        for node in self.all_nodes():
            try:
                lu_set = node.synset.lu_set
            except KeyError:
                continue

            for lu in lu_set:
                lemma = lu.lemma.lower()
                lemma_to_nodes_dict[lemma].add(node)

        self._lemma_to_nodes_dict = lemma_to_nodes_dict

    def generate_lemma_to_nodes_dict_lexical_units(self):
        """
        This method generates a utility dictionary, which maps lemmas to
        corresponding node objects. It is expensive in means of time
        needed to generate the dictionary. It should therefore be executed
        at the beginning of the runtime and later its results should be reused
        as many times as needed without re-executing the function.
        """
        lemma_to_nodes_dict = defaultdict(set)

        for node in self.all_nodes():
            try:
                lemma = node.lu.lemma.lower()
                lemma_to_nodes_dict[lemma].add(node)
            except:
                continue

        self._lemma_to_nodes_dict = lemma_to_nodes_dict

    @property
    def lemma_to_nodes_dict(self):
        return self._lemma_to_nodes_dict

    def _make_lu_on_v_dict(self):
        """
        Makes dictionary lu on vertex
        """
        lu_on_vertex_dict = defaultdict(set)
        for node in self.all_nodes():
            try:
                nl = node.lu
            except Exception:
                continue

            if nl:
                lu_on_vertex_dict[node.lu.lu_id] = node

        self._lu_on_vertex_dict = lu_on_vertex_dict
