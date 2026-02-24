import networkx as nx
import random


class Network:
    def __init__(self):
        self.graph = nx.Graph()

    def generate_random(self, nodes=8, link_probability=0.4):
        for i in range(nodes):
            self.graph.add_node(i)

        for i in range(nodes):
            for j in range(i + 1, nodes):
                if random.random() < link_probability:
                    self.graph.add_edge(
                        i,
                        j,
                        bandwidth=random.randint(50, 100),
                        delay=random.uniform(1, 10),
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