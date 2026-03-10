import networkx as nx
import random


class Network:
    def __init__(self):
        self.graph = nx.Graph()

    def generate_random(self, nodes=8, link_probability=0.4,rng=None, ensure_connectivity=True):
        rng =rng or random
        self.graph.clear()
        
        for i in range(nodes):
            self.graph.add_node(i)

        for i in range(nodes):
            for j in range(i + 1, nodes):
                if rng.random() < link_probability:
                    self.graph.add_edge(
                        i,
                        j,
                        bandwidth=rng.randint(50, 100),
                        delay=rng.uniform(1, 10),
                        load=0
                    )
        # Gwarantujemy spójność topologii bazowej, aby wyniki nie były zaniżane
        # przez przypadkowe rozspójnienie grafu.
        if ensure_connectivity and nodes > 1:
            components = list(nx.connected_components(self.graph))
            if len(components) > 1:
                for a, b in zip(components, components[1:]):
                    u = next(iter(a))
                    v = next(iter(b))
                    self.graph.add_edge(
                        u,
                        v,
                        bandwidth=rng.randint(50, 100),
                        delay=rng.uniform(1, 10),
                        load=0
                    )


    def get_graph(self):
        return self.graph
    
    def reserve_bandwidth(self, path, bandwidth):
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]

            link = self.graph[u][v]

            if link["bandwidth"] - link["load"] < bandwidth:
                return False

    # Rezerwujemy przepustowość
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]
            self.graph[u][v]["load"] += bandwidth

        return True

class Flow:
    def __init__(self, src, dst, bandwidth, max_delay, priority=1):
        self.src = src
        self.dst = dst
        self.bandwidth = bandwidth
        self.max_delay = max_delay
        self.priority = priority