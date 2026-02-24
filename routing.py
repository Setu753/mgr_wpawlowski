import networkx as nx


class IPRouting:
    def __init__(self, graph):
        self.graph = graph

    def shortest_path(self, src, dst):
        try:
            return nx.dijkstra_path(self.graph, src, dst, weight="delay")
        except nx.NetworkXNoPath:
            return None