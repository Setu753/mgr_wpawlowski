import networkx as nx


class IPRouting:
    def __init__(self, graph):
        self.graph = graph

    def shortest_path(self, src, dst):
        try:
            return nx.dijkstra_path(self.graph, src, dst, weight="delay")
        except nx.NetworkXNoPath:
            return None


class CSPF:
    def __init__(self, graph):
        self.graph = graph

    def compute_path(self, flow):
        path, _ = self.compute_path_with_reason(flow)
        return path

    def compute_path_with_reason(self, flow):
        filtered_graph = self.graph.copy()

        for u, v, data in list(filtered_graph.edges(data=True)):
            if data["bandwidth"] - data["load"] < flow.bandwidth:
                filtered_graph.remove_edge(u, v)

        try:
            path = nx.dijkstra_path(
                filtered_graph,
                flow.src,
                flow.dst,
                weight="delay"
            )

            total_delay = sum(
                self.graph[u][v]["delay"]
                for u, v in zip(path[:-1], path[1:])
            )

            if total_delay > flow.max_delay:
                return None, "delay"

            return path, "accepted"

        except nx.NetworkXNoPath:
            return None, "bandwidth"


class WeightedGreedy:
    def __init__(self, graph, beta=3.0):
        self.graph = graph
        self.beta = beta

    def compute_path(self, flow):
        path, _ = self.compute_path_with_reason(flow)
        return path

    def compute_path_with_reason(self, flow):
        filtered_graph = self.graph.copy()

        for u, v, data in list(filtered_graph.edges(data=True)):
            if data["bandwidth"] - data["load"] < flow.bandwidth:
                filtered_graph.remove_edge(u, v)

        for _, _, data in filtered_graph.edges(data=True):
            delay = data["delay"]
            bandwidth = data["bandwidth"]
            load = data["load"]
            utilization = load / bandwidth if bandwidth > 0 else 0

            data["weight"] = delay * (1 + self.beta * utilization)

        try:
            path = nx.dijkstra_path(
                filtered_graph,
                flow.src,
                flow.dst,
                weight="weight"
            )

            total_delay = sum(
                self.graph[u][v]["delay"]
                for u, v in zip(path[:-1], path[1:])
            )

            if total_delay > flow.max_delay:
                return None, "delay"

            return path, "accepted"

        except nx.NetworkXNoPath:
            return None, "bandwidth"
