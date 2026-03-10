from network import Flow, Network
from routing import IPRouting, CSPF, WeightedGreedy
import random
import statistics
import copy
import csv


def average_utilization(graph):
    utils = []
    for _, _, data in graph.edges(data=True):
        if data["bandwidth"] > 0:
            utils.append(data["load"] / data["bandwidth"])
    return sum(utils) / len(utils) if utils else 0

def generate_flows(n_flows, n_nodes, rng=None):
    rng  = rng or random
    flows = []
    for _ in range(n_flows):
        src = rng.randint(0, n_nodes - 1)
        dst = rng.randint(0, n_nodes - 1)

        while dst == src:
            dst = rng.randint(0, n_nodes - 1)

        bandwidth = rng.randint(5, 40)
        max_delay = rng.randint(5, 30)

        flows.append(Flow(src, dst, bandwidth, max_delay))

    return flows


def run_experiment(n_nodes=10, n_flows=30, seed=None, beta=3.0):
    rng = random.Random(seed) if seed is not None else random

    # Generacja jednej topologii bazowej
    base_network = Network()
    base_network.generate_random(nodes=n_nodes, rng=rng, ensure_connectivity=True)

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

    weighted_router = WeightedGreedy(graph_weighted, beta=beta)

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

    



def run_scaling_experiments(flow_levels=(30, 60, 90), n_runs=30, n_nodes=10, base_seed=12345, beta=3.0, summary_file="results_summary.csv", runs_csv_path="runs_details.csv"):
    aggregated_rows = []
    run_rows = []

    import statistics

    for n_flows in flow_levels:
        ip_acc, cspf_acc, w_acc = [], [], []
        ip_del, cspf_del, w_del = [], [], []
        ip_util, cspf_util, w_util = [], [], []

        for run_idx in range(n_runs):

            run_seed = base_seed + (n_flows * 1000) + run_idx
            result = run_experiment(n_nodes=10, n_flows=n_flows, seed=run_seed, beta=beta)

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
        run_rows.append(
                {
                    "n_flows": n_flows,
                    "run_idx": run_idx,
                    "seed": run_seed,
                    "ip_acceptance": result["ip_acceptance"],
                    "cspf_acceptance": result["cspf_acceptance"],
                    "weighted_acceptance": result["weighted_acceptance"],
                    "ip_avg_delay": result["ip_avg_delay"],
                    "cspf_avg_delay": result["cspf_avg_delay"],
                    "weighted_avg_delay": result["weighted_avg_delay"],
                    "ip_util": result["ip_util"],
                    "cspf_util": result["cspf_util"],
                    "weighted_util": result["weighted_util"],
                }
            )
        summary = {
            "n_flows": n_flows,
            "n_runs": n_runs,
            "ip_acceptance_mean": statistics.mean(ip_acc),
            "cspf_acceptance_mean": statistics.mean(cspf_acc),
            "weighted_acceptance_mean": statistics.mean(w_acc),
            "ip_delay_mean": statistics.mean(ip_del),
            "cspf_delay_mean": statistics.mean(cspf_del),
            "weighted_delay_mean": statistics.mean(w_del),
            "ip_util_mean": statistics.mean(ip_util),
            "cspf_util_mean": statistics.mean(cspf_util),
            "weighted_util_mean": statistics.mean(w_util),
        }
        aggregated_rows.append(summary)

        print("IP:")
        print("  acceptance:", summary["ip_acceptance_mean"])
        print("  delay:", summary["ip_delay_mean"])
        print("  utilization:", summary["ip_util_mean"])

        print("CSPF:")
        print("  acceptance:", summary["cspf_acceptance_mean"])
        print("  delay:", summary["cspf_delay_mean"])
        print("  utilization:", summary["cspf_util_mean"])

        print("Weighted:")
        print("  acceptance:", summary["weighted_acceptance_mean"])
        print("  delay:", summary["weighted_delay_mean"])
        print("  utilization:", summary["weighted_util_mean"])

    with open("results_summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(aggregated_rows[0].keys()))
        writer.writeheader()
        writer.writerows(aggregated_rows)
    
    with open(runs_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(run_rows[0].keys()))
        writer.writeheader()
        writer.writerows(run_rows)

if __name__ == "__main__":
    run_scaling_experiments(flow_levels=(30, 60, 90), n_runs=30,n_nodes=10, base_seed=12345, beta=3.0)