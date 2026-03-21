from network import Flow, Network
from routing import IPRouting, CSPF, WeightedGreedy
import random
import statistics
import copy
import csv
import time


def generate_flows(n_flows, n_nodes, rng=None):
    rng = rng or random
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

    base_network = Network()
    base_network.generate_random(nodes=n_nodes, rng=rng, ensure_connectivity=True)
    base_graph = base_network.get_graph()

    flows = generate_flows(n_flows, n_nodes, rng=rng)

    # ================= IP =================
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
            total_delay_ip += net_ip.path_delay(path)

    # ================= CSPF =================
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
            total_delay_cspf += net_cspf.path_delay(path)

    # ================= WEIGHTED =================
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
            total_delay_weighted += net_weighted.path_delay(path)

    # ===== METRYKI =====
    ip_util = net_ip.utilization()
    cspf_util = net_cspf.utilization()
    weighted_util = net_weighted.utilization()

    return {
        "ip_acceptance": accepted_ip / n_flows,
        "cspf_acceptance": accepted_cspf / n_flows,
        "weighted_acceptance": accepted_weighted / n_flows,

        "ip_avg_delay": total_delay_ip / accepted_ip if accepted_ip else 0,
        "cspf_avg_delay": total_delay_cspf / accepted_cspf if accepted_cspf else 0,
        "weighted_avg_delay": total_delay_weighted / accepted_weighted if accepted_weighted else 0,

        "ip_avg_util": ip_util["avg"],
        "ip_max_util": ip_util["max"],

        "cspf_avg_util": cspf_util["avg"],
        "cspf_max_util": cspf_util["max"],

        "weighted_avg_util": weighted_util["avg"],
        "weighted_max_util": weighted_util["max"],

        "ip_rejected": n_flows - accepted_ip,
        "cspf_rejected": n_flows - accepted_cspf,
        "weighted_rejected": n_flows - accepted_weighted,
    }


def run_scaling_experiments(
    flow_levels=(30, 60, 90),
    n_runs=30,
    n_nodes=10,
    base_seed=int(time.time()),
    beta=3.0,
    summary_file="results_summary.csv",
    runs_csv_path="runs_details.csv",
):
    aggregated_rows = []
    run_rows = []

    for n_flows in flow_levels:
        ip_acc, cspf_acc, w_acc = [], [], []
        ip_del, cspf_del, w_del = [], [], []
        ip_util, cspf_util, w_util = [], [], []

        ip_max_util, cspf_max_util, w_max_util = [], [], []

        for run_idx in range(n_runs):
            run_seed = base_seed + (n_flows * 1000) + run_idx

            result = run_experiment(
                n_nodes=n_nodes,
                n_flows=n_flows,
                seed=run_seed,
                beta=beta,
            )

            ip_acc.append(result["ip_acceptance"])
            cspf_acc.append(result["cspf_acceptance"])
            w_acc.append(result["weighted_acceptance"])

            ip_del.append(result["ip_avg_delay"])
            cspf_del.append(result["cspf_avg_delay"])
            w_del.append(result["weighted_avg_delay"])

            ip_util.append(result["ip_avg_util"])
            cspf_util.append(result["cspf_avg_util"])
            w_util.append(result["weighted_avg_util"])

            ip_max_util.append(result["ip_max_util"])
            cspf_max_util.append(result["cspf_max_util"])
            w_max_util.append(result["weighted_max_util"])

            # 🔥 FIX — zapis każdego runa
            run_rows.append({
                "n_flows": n_flows,
                "run_idx": run_idx,
                "seed": run_seed,
                **result
            })

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

            "ip_max_util_mean": statistics.mean(ip_max_util),
            "cspf_max_util_mean": statistics.mean(cspf_max_util),
            "weighted_max_util_mean": statistics.mean(w_max_util),
        }

        aggregated_rows.append(summary)

        print(f"\n=== {n_flows} flow ===")
        print("IP:", summary["ip_acceptance_mean"])
        print("CSPF:", summary["cspf_acceptance_mean"])
        print("Weighted:", summary["weighted_acceptance_mean"])

    # ===== CSV =====
    with open(summary_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(aggregated_rows[0].keys()))
        writer.writeheader()
        writer.writerows(aggregated_rows)

    with open(runs_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(run_rows[0].keys()))
        writer.writeheader()
        writer.writerows(run_rows)


if __name__ == "__main__":
    run_scaling_experiments(
        flow_levels=(30, 60, 90),
        n_runs=30,
        n_nodes=10,
        base_seed=int(time.time()),
        beta=3.0
    )