from network import Flow, Network
from routing import IPRouting, CSPF, WeightedGreedy
import random
import copy
import time
import os
import csv


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

    for i, flow in enumerate(flows):

        # ===== IP =====
        path = ip_router.shortest_path(flow.src, flow.dst)
        log_line = f"FLOW {i} IP: "

        if path:
            log_line += " -> ".join(map(str, path))
        else:
            log_line += "NONE"

        if path and net_ip.reserve_bandwidth(path, flow.bandwidth):
            accepted_ip += 1
            log_line += " | ACCEPTED"
        else:
            log_line += " | REJECTED"

        if current_log_file:
            with open(current_log_file, "a") as f:
                f.write(log_line + "\n")

        # ===== CSPF =====
        path = cspf_router.compute_path(flow)
        log_line = f"FLOW {i} CSPF: "

        if path:
            log_line += " -> ".join(map(str, path))
        else:
            log_line += "NONE"

        if path and net_cspf.reserve_bandwidth(path, flow.bandwidth):
            accepted_cspf += 1
            log_line += " | ACCEPTED"
        else:
            log_line += " | REJECTED"

        if current_log_file:
            with open(current_log_file, "a") as f:
                f.write(log_line + "\n")

        # ===== WEIGHTED =====
        path = weighted_router.compute_path(flow)
        log_line = f"FLOW {i} WEIGHTED: "

        if path:
            log_line += " -> ".join(map(str, path))
        else:
            log_line += "NONE"

        if path and net_weighted.reserve_bandwidth(path, flow.bandwidth):
            accepted_weighted += 1
            log_line += " | ACCEPTED"
        else:
            log_line += " | REJECTED"

        if current_log_file:
            with open(current_log_file, "a") as f:
                f.write(log_line + "\n")

    # ===== WIZUALIZACJA =====
    if topo_prefix:
        net_ip.save_topology(f"{topo_prefix}_ip.png")
        net_cspf.save_topology(f"{topo_prefix}_cspf.png")
        net_weighted.save_topology(f"{topo_prefix}_weighted.png")

        import matplotlib.pyplot as plt
        import networkx as nx

        G = net_weighted.graph
        pos = nx.spring_layout(G, seed=42)

        edge_colors = [
            data["load"] / data["bandwidth"]
            for _, _, data in G.edges(data=True)
        ]

        fig, ax = plt.subplots(figsize=(8, 6))
        nx.draw(G, pos, with_labels=True, edge_color=edge_colors,
                edge_cmap=plt.cm.Reds, ax=ax)

        sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds)
        sm.set_array(edge_colors)
        fig.colorbar(sm, ax=ax)

        plt.savefig(f"{topo_prefix}_heatmap.png")
        plt.close()

    return {
        "ip_acceptance": accepted_ip / n_flows,
        "cspf_acceptance": accepted_cspf / n_flows,
        "weighted_acceptance": accepted_weighted / n_flows,
    }


def run_scaling_experiments():

    print("\n=== OPIS EKSPERYMENTU ===")
    print("IP        - najkrótsza ścieżka (ignoruje obciążenie)")
    print("CSPF      - uwzględnia ograniczenia (pasmo, delay)")
    print("Weighted  - uwzględnia obciążenie (load balancing)")
    print("Acceptance = procent zaakceptowanych przepływów\n")

    base_dir = f"run_{int(time.time())}"
    plots_dir = os.path.join(base_dir, "plots")
    logs_dir = os.path.join(base_dir, "logs")

    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    base_network = Network()
    base_network.generate_random(nodes=15)
    base_graph = base_network.get_graph()

    results = []

    for n_flows in [30, 60, 90]:

        log_file = os.path.join(logs_dir, f"log_{n_flows}.txt")

        with open(log_file, "w") as f:
            f.write(f"=== LOG DLA {n_flows} FLOWS ===\n")

        sum_ip, sum_cspf, sum_w = [], [], []

        for run_idx in range(10):

            with open(log_file, "a") as f:
                f.write(f"\n===== RUN {run_idx} =====\n")

            result = run_experiment(
                base_graph=base_graph,
                n_nodes=15,
                n_flows=n_flows,
                seed=run_idx,
                topo_prefix=os.path.join(plots_dir, f"topo_{n_flows}_{run_idx}"),
                current_log_file=log_file
            )

            print(f"[{n_flows} flows | run {run_idx}] "
                  f"IP={result['ip_acceptance']:.2f} (najkrótsza) | "
                  f"CSPF={result['cspf_acceptance']:.2f} (ograniczenia) | "
                  f"W={result['weighted_acceptance']:.2f} (obciążenie)")

            sum_ip.append(result["ip_acceptance"])
            sum_cspf.append(result["cspf_acceptance"])
            sum_w.append(result["weighted_acceptance"])

            results.append({
                "n_flows": n_flows,
                "run": run_idx,
                **result
            })

        print(f"\n=== PODSUMOWANIE dla {n_flows} flow ===")
        print(f"IP średnio: {sum(sum_ip)/len(sum_ip):.2f}")
        print(f"CSPF średnio: {sum(sum_cspf)/len(sum_cspf):.2f}")
        print(f"Weighted średnio: {sum(sum_w)/len(sum_w):.2f}\n")
        avg_w = sum(sum_w) / len(sum_w)

    if avg_w > 0.9:
        print("Wniosek: Sieć jest lekko obciążona – większość przepływów jest obsługiwana.")
    elif avg_w > 0.5:
        print("Wniosek: Sieć jest umiarkowanie obciążona – część przepływów jest odrzucana.")
    else:
        print("Wniosek: Sieć jest przeciążona – duża liczba odrzuconych przepływów.")

    print("-" * 50)

    csv_path = os.path.join(base_dir, "results.csv")

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    run_scaling_experiments()