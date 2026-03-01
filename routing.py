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
        # 1. Kopia grafu
        filtered_graph = self.graph.copy()

        # 2. Usuwanie łącza bez wystarczającego pasma
        for u, v, data in list(filtered_graph.edges(data=True)):
            if data["bandwidth"] - data["load"] < flow.bandwidth:
                filtered_graph.remove_edge(u, v)

        try:
            # 3. Liczenie ścieżki po przefiltrowanym grafie
            path = nx.dijkstra_path(filtered_graph, flow.src, flow.dst, weight="delay")

            # 4. Sprawdzanie constraint delay
            total_delay = sum(
                self.graph[u][v]["delay"]
                for u, v in zip(path[:-1], path[1:])
            )

            if total_delay > flow.max_delay:
                return None

            return path

        except nx.NetworkXNoPath:
            return None

class WeightedGreedy:
    def __init__(self, graph, beta=3.0):
        self.graph = graph
        self.beta = beta

    def compute_path(self, flow):

        filtered_graph = self.graph.copy()

        # filtr przepustowości
        for u, v, data in list(filtered_graph.edges(data=True)):
            if data["bandwidth"] - data["load"] < flow.bandwidth:
                filtered_graph.remove_edge(u, v)

        # dynamiczna waga: delay * (1 + beta * utilization)
        for u, v, data in filtered_graph.edges(data=True):

            delay = data["delay"]
            bandwidth = data["bandwidth"]
            load = data["load"]

            utilization = load / bandwidth

            weight = delay * (1 + self.beta * utilization)

            data["weight"] = weight

        try:
            path = nx.dijkstra_path(
                filtered_graph,
                flow.src,
                flow.dst,
                weight="weight"
            )

            # constraint delay
            total_delay = sum(
                self.graph[u][v]["delay"]
                for u, v in zip(path[:-1], path[1:])
            )

            if total_delay > flow.max_delay:
                return None

            return path

        except nx.NetworkXNoPath:
            return None
       