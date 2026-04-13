from network import Flow, Network
from routing import IPRouting, CSPF, WeightedGreedy
import matplotlib.pyplot as plt
import networkx as nx
import random
import copy
import time
import os
import json
import pandas as pd


# GENEROWANIE FLOW 

def generate_flows(n_flows, n_nodes, rng=None):
    rng = rng or random
    flows = []

    for _ in range(n_flows):
        src = rng.randint(0, n_nodes - 1)
        dst = rng.randint(0, n_nodes - 1)

        while dst == src:
            dst = rng.randint(0, n_nodes - 1)

        bandwidth = rng.randint(1, 10)
        max_delay = rng.randint(10, 40)

        flows.append(Flow(src, dst, bandwidth, max_delay))

    return flows


#  HEATMAP 

def save_heatmap(graph, filename, title):
    G = graph
    pos = nx.spring_layout(G, seed=42)

    edge_colors = [
        data["load"] / data["bandwidth"]
        for _, _, data in G.edges(data=True)
    ]

    fig, ax = plt.subplots(figsize=(8, 6))

    nx.draw(
        G,
        pos,
        with_labels=True,
        edge_color=edge_colors,
        edge_cmap=plt.cm.Reds,
        edge_vmin=0,
        edge_vmax=1,
        ax=ax
    )

    sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(vmin=0, vmax=1))
    sm.set_array(edge_colors)

    fig.colorbar(sm, ax=ax, label="Wykorzystanie łącza")
    plt.title(title)

    plt.savefig(filename)
    plt.close()


#  METRYKI 

def compute_network_metrics(graph):
    utilizations = []
    delays = []

    for _, _, data in graph.edges(data=True):
        bw = data.get("bandwidth", 1)
        load = data.get("load", 0)
        delay = data.get("delay", 1)

        utilizations.append(load / bw if bw > 0 else 0)
        delays.append(delay)

    return {
        "avg_util": sum(utilizations) / len(utilizations) if utilizations else 0,
        "max_util": max(utilizations) if utilizations else 0,
        "avg_delay_link": sum(delays) / len(delays) if delays else 0
    }


def compute_path_delay(graph, path):
    if not path or len(path) < 2:
        return 0

    delay = 0
    for i in range(len(path) - 1):
        edge_data = graph[path[i]][path[i + 1]]
        delay += edge_data.get("delay", 1)

    return delay


def save_run_metadata(base_dir, metadata):
    metadata_path = os.path.join(base_dir, "run_metadata.json")

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def init_rejection_stats():
    return {
        "bandwidth": 0,
        "delay": 0,
        "no_path": 0
    }


def rejection_metrics(prefix, stats, n_flows):
    return {
        f"{prefix}_reject_bandwidth": stats["bandwidth"],
        f"{prefix}_reject_delay": stats["delay"],
        f"{prefix}_reject_no_path": stats["no_path"],
        f"{prefix}_reject_bandwidth_ratio": stats["bandwidth"] / n_flows,
        f"{prefix}_reject_delay_ratio": stats["delay"] / n_flows,
        f"{prefix}_reject_no_path_ratio": stats["no_path"] / n_flows,
    }


def dominant_rejection_reason(means, prefix):
    reason_values = {
        "bandwidth": means[f"{prefix}_reject_bandwidth"],
        "delay": means[f"{prefix}_reject_delay"],
        "no_path": means[f"{prefix}_reject_no_path"],
    }

    dominant_reason = max(reason_values, key=reason_values.get)
    dominant_value = reason_values[dominant_reason]

    if dominant_value <= 0:
        return "none"

    return dominant_reason


#  WNIOSKI 

def print_summary_insights(df, n_flows):
    subset = df[df["n_flows"] == n_flows]
    means = subset.mean(numeric_only=True)

    print("\n" + "="*60)
    print(f"PODSUMOWANIE dla {n_flows} przepływów")
    print("="*60)

    print("\nAcceptance:")
    print(f"IP        : {means['ip_acceptance']:.3f}")
    print(f"CSPF      : {means['cspf_acceptance']:.3f}")
    print(f"Weighted  : {means['weighted_acceptance']:.3f}")

    print("\nBlocking:")
    print(f"IP        : {means['ip_blocking']:.3f}")
    print(f"CSPF      : {means['cspf_blocking']:.3f}")
    print(f"Weighted  : {means['weighted_blocking']:.3f}")

    print("\nPowody odrzucen:")
    print(
        f"IP        : bandwidth={means['ip_reject_bandwidth']:.1f}, "
        f"delay={means['ip_reject_delay']:.1f}, no_path={means['ip_reject_no_path']:.1f}"
    )
    print(
        f"CSPF      : bandwidth={means['cspf_reject_bandwidth']:.1f}, "
        f"delay={means['cspf_reject_delay']:.1f}, no_path={means['cspf_reject_no_path']:.1f}"
    )
    print(
        f"Weighted  : bandwidth={means['weighted_reject_bandwidth']:.1f}, "
        f"delay={means['weighted_reject_delay']:.1f}, no_path={means['weighted_reject_no_path']:.1f}"
    )

    print("\nDominujacy powod odrzucen:")
    print(f"IP        : {dominant_rejection_reason(means, 'ip')}")
    print(f"CSPF      : {dominant_rejection_reason(means, 'cspf')}")
    print(f"Weighted  : {dominant_rejection_reason(means, 'weighted')}")

    print("\nDelay:")
    print(f"IP        : {means['ip_avg_delay']:.2f}")
    print(f"CSPF      : {means['cspf_avg_delay']:.2f}")
    print(f"Weighted  : {means['weighted_avg_delay']:.2f}")

    print("\nMax Utilization:")
    print(f"IP        : {means['ip_max_util']:.2f}")
    print(f"CSPF      : {means['cspf_max_util']:.2f}")
    print(f"Weighted  : {means['weighted_max_util']:.2f}")

    print("\nWNIOSKI:")

    best = max(
        ["ip", "cspf", "weighted"],
        key=lambda x: means[f"{x}_acceptance"]
    )

    print(f"- Najlepszy algorytm: {best.upper()}")

    if means["weighted_acceptance"] > 0.85:
        print("- Sieć lekko obciążona")
    elif means["weighted_acceptance"] > 0.5:
        print("- Sieć umiarkowanie obciążona")
    else:
        print("- Sieć przeciążona")

    if means["weighted_max_util"] > 0.9:
        print("- Występują bottlenecki")
    elif means["weighted_max_util"] > 0.7:
        print("- Sieć blisko przeciążenia")
    else:
        print("- Stabilna praca sieci")

    if means["cspf_avg_delay"] < means["ip_avg_delay"]:
        print("- CSPF poprawia opóźnienia (QoS)")
    else:
        print("- Brak poprawy opóźnień względem IP")

    print("="*60 + "\n")


# EKSPERYMENT 

def run_experiment(base_graph, n_nodes=15, n_flows=30, seed=None, beta=3.0,
                   topo_prefix=None, current_log_file=None):

    rng = random.Random(seed) if seed is not None else random
    flows = generate_flows(n_flows, n_nodes, rng=rng)

    net_ip = Network()
    net_ip.graph = copy.deepcopy(base_graph)
    ip_router = IPRouting(net_ip.get_graph())

    net_cspf = Network()
    net_cspf.graph = copy.deepcopy(base_graph)
    cspf_router = CSPF(net_cspf.get_graph())

    net_weighted = Network()
    net_weighted.graph = copy.deepcopy(base_graph)
    weighted_router = WeightedGreedy(net_weighted.get_graph(), beta=beta)

    accepted_ip = 0
    accepted_cspf = 0
    accepted_weighted = 0
    ip_rejections = init_rejection_stats()
    cspf_rejections = init_rejection_stats()
    weighted_rejections = init_rejection_stats()

    path_lengths_ip, delays_ip = [], []
    path_lengths_cspf, delays_cspf = [], []
    path_lengths_w, delays_w = [], []

    for i, flow in enumerate(flows):

        #  IP 
        path = ip_router.shortest_path(flow.src, flow.dst)
        log_line = f"FLOW {i} IP: "
        log_line += " -> ".join(map(str, path)) if path else "NONE"

        if path and net_ip.reserve_bandwidth(path, flow.bandwidth):
            accepted_ip += 1
            path_lengths_ip.append(len(path))
            delays_ip.append(compute_path_delay(net_ip.graph, path))
            log_line += " | ACCEPTED"
        else:
            reason = "bandwidth" if path else "no_path"
            ip_rejections[reason] += 1
            log_line += f" | REJECTED ({reason})"

        if current_log_file:
            with open(current_log_file, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")

        #CSPF
        path, reason = cspf_router.compute_path_with_reason(flow)
        log_line = f"FLOW {i} CSPF: "
        log_line += " -> ".join(map(str, path)) if path else "NONE"

        if path and net_cspf.reserve_bandwidth(path, flow.bandwidth):
            accepted_cspf += 1
            path_lengths_cspf.append(len(path))
            delays_cspf.append(compute_path_delay(net_cspf.graph, path))
            log_line += " | ACCEPTED"
        else:
            if path and reason == "accepted":
                reason = "bandwidth"
            cspf_rejections[reason] += 1
            log_line += f" | REJECTED ({reason})"

        if current_log_file:
            with open(current_log_file, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")

        #WEIGHTED
        path, reason = weighted_router.compute_path_with_reason(flow)
        log_line = f"FLOW {i} WEIGHTED: "
        log_line += " -> ".join(map(str, path)) if path else "NONE"

        if path and net_weighted.reserve_bandwidth(path, flow.bandwidth):
            accepted_weighted += 1
            path_lengths_w.append(len(path))
            delays_w.append(compute_path_delay(net_weighted.graph, path))
            log_line += " | ACCEPTED"
        else:
            if path and reason == "accepted":
                reason = "bandwidth"
            weighted_rejections[reason] += 1
            log_line += f" | REJECTED ({reason})"

        if current_log_file:
            with open(current_log_file, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")

    ip_metrics = compute_network_metrics(net_ip.graph)
    cspf_metrics = compute_network_metrics(net_cspf.graph)
    w_metrics = compute_network_metrics(net_weighted.graph)

    if topo_prefix:
        net_ip.save_topology(f"{topo_prefix}_ip.png")
        net_cspf.save_topology(f"{topo_prefix}_cspf.png")
        net_weighted.save_topology(f"{topo_prefix}_weighted.png")

        save_heatmap(net_ip.graph, f"{topo_prefix}_ip_heatmap.png", "IP")
        save_heatmap(net_cspf.graph, f"{topo_prefix}_cspf_heatmap.png", "CSPF")
        save_heatmap(net_weighted.graph, f"{topo_prefix}_weighted_heatmap.png", "WEIGHTED")

    return {
        "ip_acceptance": accepted_ip / n_flows,
        "cspf_acceptance": accepted_cspf / n_flows,
        "weighted_acceptance": accepted_weighted / n_flows,

        "ip_blocking": 1 - (accepted_ip / n_flows),
        "cspf_blocking": 1 - (accepted_cspf / n_flows),
        "weighted_blocking": 1 - (accepted_weighted / n_flows),

        "ip_avg_delay": sum(delays_ip)/len(delays_ip) if delays_ip else 0,
        "cspf_avg_delay": sum(delays_cspf)/len(delays_cspf) if delays_cspf else 0,
        "weighted_avg_delay": sum(delays_w)/len(delays_w) if delays_w else 0,

        "ip_avg_util": ip_metrics["avg_util"],
        "cspf_avg_util": cspf_metrics["avg_util"],
        "weighted_avg_util": w_metrics["avg_util"],

        "ip_max_util": ip_metrics["max_util"],
        "cspf_max_util": cspf_metrics["max_util"],
        "weighted_max_util": w_metrics["max_util"],

        **rejection_metrics("ip", ip_rejections, n_flows),
        **rejection_metrics("cspf", cspf_rejections, n_flows),
        **rejection_metrics("weighted", weighted_rejections, n_flows)
    }



def run_scaling_experiments():

    base_dir = os.path.join("plots", f"run_{int(time.time())}")
    plots_dir = os.path.join(base_dir, "plots")
    logs_dir = os.path.join(base_dir, "logs")
    topology_seed = random.SystemRandom().randint(0, 10**9)
    topology_rng = random.Random(topology_seed)
    n_nodes = 15
    flow_levels = [30, 60, 90]
    runs_per_level = 10

    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    save_run_metadata(base_dir, {
        "topology_seed": topology_seed,
        "n_nodes": n_nodes,
        "flow_levels": flow_levels,
        "runs_per_level": runs_per_level,
        "topology_policy": (
            "One base topology is generated per program run and reused for all "
            "experiments in that run. A new topology is generated only after the "
            "program is started again."
        )
    })

    base_network = Network()
    base_network.generate_random(nodes=n_nodes, rng=topology_rng)
    base_graph = base_network.get_graph()

    print(f"\nTopology seed for this run: {topology_seed}")
    results = []

    for n_flows in flow_levels:

        log_file = os.path.join(logs_dir, f"log_{n_flows}.txt")

        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"=== LOG dla {n_flows} flows ===\n")
            f.write(f"TOPOLOGY_SEED={topology_seed}\n")

        for run_idx in range(runs_per_level):

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n===== RUN {run_idx} =====\n")

            topo_prefix = os.path.join(plots_dir, f"topo_{n_flows}_{run_idx}")

            result = run_experiment(
                base_graph=base_graph,
                n_nodes=n_nodes,
                n_flows=n_flows,
                seed=run_idx,
                topo_prefix=topo_prefix,
                current_log_file=log_file
            )

            results.append({
                "n_flows": n_flows,
                "run": run_idx,
                **result
            })

        print_summary_insights(pd.DataFrame(results), n_flows)

    df = pd.DataFrame(results)

    df.to_csv(os.path.join(base_dir, "results_details.csv"), index=False)
    df.groupby("n_flows").mean(numeric_only=True).to_csv(
        os.path.join(base_dir, "results_summary.csv")
    )


if __name__ == "__main__":
    run_scaling_experiments()
