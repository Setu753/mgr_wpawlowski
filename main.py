from network import Flow, Network
from routing import IPRouting, CSPF, WeightedGreedy
import random
import statistics
import copy


def average_utilization(graph):
    utils = []
    for _, _, data in graph.edges(data=True):
        if data["bandwidth"] > 0:
            utils.append(data["load"] / data["bandwidth"])
    return sum(utils) / len(utils) if utils else 0

def generate_flows(n_flows, n_nodes):
    flows = []
    for _ in range(n_flows):
        src = random.randint(0, n_nodes - 1)
        dst = random.randint(0, n_nodes - 1)

        while dst == src:
            dst = random.randint(0, n_nodes - 1)

        bandwidth = random.randint(5, 40)
        max_delay = random.randint(5, 30)

        flows.append(Flow(src, dst, bandwidth, max_delay))

    return flows


def run_experiment(n_nodes=10, n_flows=30):

    # Generacja jednej topologi bazowej
    base_network = Network()
    base_network.generate_random(nodes=n_nodes)

    base_graph = base_network.get_graph()

    # Generacja jednego zestawu flow
    flows = generate_flows(n_flows, n_nodes)

    
    # IP
    
    net_ip = Network()
    net_ip.graph = copy.deepcopy(base_graph)
    graph_ip = net_ip.get_graph()

    ip_router = IPRouting(graph_ip)

    accepted_ip = 0
    total_delay_ip = 0

    for flow in flows:
        path = ip_router.shortest_path(flow.src, flow.dst)

        if path and net_ip.reserve_bandwidth(path, flow.bandwidth):
            accepted_ip += 1
            delay = sum(graph_ip[u][v]["delay"] for u, v in zip(path[:-1], path[1:]))
            total_delay_ip += delay

    
    # CSPF
    
    net_cspf = Network()
    net_cspf.graph = copy.deepcopy(base_graph)
    graph_cspf = net_cspf.get_graph()

    cspf_router = CSPF(graph_cspf)

    accepted_cspf = 0
    total_delay_cspf = 0

    for flow in flows:
        path = cspf_router.compute_path(flow)

        if path and net_cspf.reserve_bandwidth(path, flow.bandwidth):
            accepted_cspf += 1
            delay = sum(graph_cspf[u][v]["delay"] for u, v in zip(path[:-1], path[1:]))
            total_delay_cspf += delay

    
    # WG
    
    net_weighted = Network()
    net_weighted.graph = copy.deepcopy(base_graph)
    graph_weighted = net_weighted.get_graph()

    weighted_router = WeightedGreedy(graph_weighted)

    accepted_weighted = 0
    total_delay_weighted = 0

    for flow in flows:
        path = weighted_router.compute_path(flow)

        if path and net_weighted.reserve_bandwidth(path, flow.bandwidth):
            accepted_weighted += 1
            delay = sum(graph_weighted[u][v]["delay"] for u, v in zip(path[:-1], path[1:]))
            total_delay_weighted += delay

    return {
        "ip_acceptance": accepted_ip / n_flows,
        "cspf_acceptance": accepted_cspf / n_flows,
        "weighted_acceptance": accepted_weighted / n_flows,

        "ip_avg_delay": total_delay_ip / accepted_ip if accepted_ip > 0 else 0,
        "cspf_avg_delay": total_delay_cspf / accepted_cspf if accepted_cspf > 0 else 0,
        "weighted_avg_delay": total_delay_weighted / accepted_weighted if accepted_weighted > 0 else 0,

        "ip_util": average_utilization(graph_ip),
        "cspf_util": average_utilization(graph_cspf),
        "weighted_util": average_utilization(graph_weighted),
    }

    



def run_scaling_experiments(flow_levels=(30, 60, 90), n_runs=30):

    import statistics

    for n_flows in flow_levels:
        ip_acc, cspf_acc, w_acc = [], [], []
        ip_del, cspf_del, w_del = [], [], []
        ip_util, cspf_util, w_util = [], [], []

        for _ in range(n_runs):
            result = run_experiment(n_nodes=10, n_flows=n_flows)

            ip_acc.append(result["ip_acceptance"])
            cspf_acc.append(result["cspf_acceptance"])
            w_acc.append(result["weighted_acceptance"])

            ip_del.append(result["ip_avg_delay"])
            cspf_del.append(result["cspf_avg_delay"])
            w_del.append(result["weighted_avg_delay"])

            ip_util.append(result["ip_util"])
            cspf_util.append(result["cspf_util"])
            w_util.append(result["weighted_util"])

        print(f"\n=== OBCIĄŻENIE: {n_flows} flow (średnia z {n_runs}) ===")

        print("IP:")
        print("  acceptance:", statistics.mean(ip_acc))
        print("  delay:", statistics.mean(ip_del))
        print("  utilization:", statistics.mean(ip_util))

        print("CSPF:")
        print("  acceptance:", statistics.mean(cspf_acc))
        print("  delay:", statistics.mean(cspf_del))
        print("  utilization:", statistics.mean(cspf_util))

        print("Weighted:")
        print("  acceptance:", statistics.mean(w_acc))
        print("  delay:", statistics.mean(w_del))
        print("  utilization:", statistics.mean(w_util))

if __name__ == "__main__":
    run_scaling_experiments(flow_levels=(30, 60, 90), n_runs=30)