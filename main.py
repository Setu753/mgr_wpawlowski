from network import Flow, Network
from routing import IPRouting


# 1. Tworzymy sieć
net = Network()
net.generate_random(nodes=10)

graph = net.get_graph()

# 2. Routing IP
router = IPRouting(graph)
flow = Flow(src=0, dst=5, bandwidth=20, max_delay=5)
path = router.shortest_path(flow.src, flow.dst)

print("Ścieżka IP:", path)

if path:
    # 3. Rezerwacja przepustowości
    if net.reserve_bandwidth(path, flow.bandwidth):
        print("Przepustowość zarezerwowana dla flow.")
    else:
        print("Nie można zarezerwować przepustowości dla flow.")