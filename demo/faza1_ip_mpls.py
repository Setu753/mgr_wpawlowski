import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import sys

# --- 1. STAŁE I KONFIGURACJA SYMULACJI ---
BASE_STEPS_PER_MS = 10          # KROKI ANIMACJI: 10 klatek na 1ms
QUEUING_DELAY_MS = 4            # CZAS OCZEKIWANIA (Kara) w kolejce na przeciążonym węźle (B, C, D)
QUEUING_NODES = ['B', 'C', 'D'] # Węzły, w których występuje przeciążenie
TRAFFIC_UNIT_MBPS = 11          # KLUCZOWA DEFINICJA PAKIETU: Wymagana przepustowość (powyżej BW=10)

# Definicja Topologii
edges = [
    ('A', 'B', {'delay': 1, 'bw': 10}), ('B', 'C', {'delay': 1, 'bw': 10}),
    ('C', 'D', {'delay': 1, 'bw': 10}), ('D', 'F', {'delay': 1, 'bw': 10}), 
    ('A', 'G', {'delay': 3, 'bw': 100}), ('G', 'H', {'delay': 3, 'bw': 100}),
    ('H', 'E', {'delay': 3, 'bw': 100}), ('E', 'F', {'delay': 3, 'bw': 100}), 
]
G = nx.Graph()
G.add_edges_from([(u, v, d) for u, v, d in edges])

# Mapa Pozycji
pos = {
    'A': (0, 3), 'B': (2, 4), 'C': (4, 4), 'D': (6, 4), 'F': (8, 3),
    'G': (2, 2), 'H': (4, 2), 'E': (6, 2) 
}
START_NODE = 'A'
END_NODE = 'F'

# --- 2. LOGIKA ROUTINGU I KALKULACJI METRYK (CBR) ---
def calc_paths_and_metrics(G):
    # Logika kosztów (CPU) i warunek przeciążenia
    for u, v, data in G.edges(data=True):
        if data['bw'] < TRAFFIC_UNIT_MBPS: # Logika: BW (10) < Wymagane (11)
            data['cpu_cost'] = 10  
        else:
            data['cpu_cost'] = 2   

    # Routing IP (Bazowy Koszt)
    ip_path = nx.shortest_path(G, START_NODE, END_NODE, weight='delay')
    ip_base_delay = sum(G[u][v]['delay'] for u, v in zip(ip_path[:-1], ip_path[1:]))
    
    # KALKULACJA IP_REAL_DELAY (transport + kolejkowanie)
    ip_queuing_delay = len(QUEUING_NODES) * QUEUING_DELAY_MS 
    ip_real_delay = ip_base_delay + ip_queuing_delay          # 16ms
    ip_cpu_cost = sum(G[u][v]['cpu_cost'] for u, v in zip(ip_path[:-1], ip_path[1:]))

    # Routing MPLS-TE (CBR)
    paths = list(nx.all_simple_paths(G, START_NODE, END_NODE))
    # MPLS-TE szuka ścieżek, które mają wystarczającą BW dla jednostki ruchu (BW >= 11)
    mpls_candidates = [p for p in paths if all(G[u][v]['bw'] >= TRAFFIC_UNIT_MBPS for u, v in zip(p[:-1], p[1:]))]
    
    mpls_path = min(mpls_candidates, key=lambda p: sum(G[u][v]['delay'] for u, v in zip(p[:-1], p[1:])))
    mpls_real_delay = sum(G[u][v]['delay'] for u, v in zip(mpls_path[:-1], mpls_path[1:])) # 12ms
    mpls_base_delay = mpls_real_delay
    
    # Metryki
    metrics = {
        'IP': {'Jitter (ms)': 5.0, 'CPU Cost (jedn.)': ip_cpu_cost},
        'MPLS-TE': {'Jitter (ms)': 0.5, 'CPU Cost (jedn.)': sum(G[u][v]['cpu_cost'] for u, v in zip(mpls_path[:-1], mpls_path[1:]))}
    }

    # Przygotowanie mapy opóźnień (uwzględnia stop-and-wait)
    ip_delay_map = {}
    current_frame = 0; current_cumulative_delay = 0
    for i, (u, v) in enumerate(zip(ip_path[:-1], ip_path[1:])):
        link_delay = G[u][v]['delay']; steps_travel = int(link_delay * BASE_STEPS_PER_MS)
        
        # 1. RUCH PRZEZ ŁĄCZE
        for k in range(steps_travel): ip_delay_map[current_frame + k] = current_cumulative_delay + (link_delay * (k / steps_travel))
        current_frame += steps_travel; current_cumulative_delay += link_delay
        
        # 2. OCZEKIWANIE W KOLEJCE
        if v in QUEUING_NODES:
            steps_wait = int(QUEUING_DELAY_MS * BASE_STEPS_PER_MS)
            for k in range(steps_wait): ip_delay_map[current_frame + k] = current_cumulative_delay
            current_frame += steps_wait; current_cumulative_delay += QUEUING_DELAY_MS
        
    return ip_path, ip_base_delay, ip_real_delay, mpls_path, mpls_base_delay, mpls_real_delay, metrics, ip_delay_map

# Uruchomienie obliczeń
ip_path, ip_base_delay, ip_real_delay, mpls_path, mpls_base_delay, mpls_real_delay, metrics, ip_delay_map = calc_paths_and_metrics(G)

# --- 3. DANE WIZUALNE I INTERPOLACJA RUCHU ---

def interpolate_path(G, path, steps_per_ms, queuing_nodes=None, queuing_delay_ms=0):
    """Generuje punkty (X, Y) dla ruchu, włączając punkty 'postoju'."""
    points = []
    for u, v in zip(path[:-1], path[1:]):
        x1, y1 = pos[u]; x2, y2 = pos[v]; link_delay = G[u][v]['delay']
        steps_travel = int(link_delay * steps_per_ms) 
        xs = np.linspace(x1, x2, steps_travel); ys = np.linspace(y1, y2, steps_travel); points += list(zip(xs, ys))
        
        if queuing_nodes and v in queuing_nodes:
            wait_steps = int(queuing_delay_ms * steps_per_ms) 
            wait_points = [(pos[v][0], pos[v][1])] * wait_steps
            points += wait_points
            
    return points

ip_points = interpolate_path(G, ip_path, BASE_STEPS_PER_MS, QUEUING_NODES, QUEUING_DELAY_MS)
mpls_points = interpolate_path(G, mpls_path, BASE_STEPS_PER_MS)
total_frames = max(len(ip_points), len(mpls_points)) + 20


# --- 4. FUNKCJA RYSOWANIA I ANIMACJI ---
def run_phase1_simulation():
    # Krok 1: Tworzenie i konfiguracja wykresów
    fig = plt.figure(figsize=(10, 8))
    gs = fig.add_gridspec(2, 1, hspace=0.3)

    # Subplot 1: Topologia Sieci
    ax_net = fig.add_subplot(gs[0, 0])
    
    # Rysowanie węzłów z obwódkami przeciążenia
    all_nodes = list(G.nodes()); 
    nx.draw_networkx_nodes(G, pos, ax=ax_net, nodelist=all_nodes, node_size=1300, node_color='lightblue', linewidths=1, edgecolors='black')
    queuing_node_colors = ['lightblue'] * len(QUEUING_NODES) 
    nx.draw_networkx_nodes(G, pos, ax=ax_net, nodelist=QUEUING_NODES,
                           node_size=1300, node_color=queuing_node_colors, 
                           linewidths=3, edgecolors='red') 
    
    # Rysowanie etykiet i krawędzi
    nx.draw_networkx_labels(G, pos, font_size=11, ax=ax_net)
    edge_labels = {(u, v): f"d={G[u][v]['delay']}ms, bw={G[u][v]['bw']}Mb/s" for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax_net)
    
    # Tytuł Wizualizacyjny: Uwzględnienie definicji pakietu
    ax_net.set_title(f"Rysunek 1: Routing (Pakiet Wymaga {TRAFFIC_UNIT_MBPS}Mb/s) vs MPLS-TE", fontsize=14)
    ax_net.axis('off')
    
    # Inicjalizacja śladów (trails) i pakietów
    trail_ip, = ax_net.plot([], [], 'r--', linewidth=3, alpha=0.7)
    trail_mpls, = ax_net.plot([], [], 'g--', linewidth=2, alpha=0.6)

    packet_ip, = ax_net.plot([], [], 'ro', markersize=12, label='Pakiet IP')
    packet_mpls, = ax_net.plot([], [], 'go', markersize=12, label='Pakiet MPLS-TE')
    ax_net.legend(loc='upper left', bbox_to_anchor=(0.85, 0.95), frameon=True, fontsize=9, edgecolor='black', title="Ruchomy Pakiet:")

    # Subplot 2: Dynamiczny Wykres Opóźnień
    ax_delay = fig.add_subplot(gs[1, 0])
    ax_delay.set_title(
        'Rysunek 2: Porównanie Opóźnienia (Realnie Narastającego) i Kosztów QoS\n'
        f"IP: SŁABA JAKOŚĆ (Jitter: ±{metrics['IP']['Jitter (ms)']}ms, CPU: {metrics['IP']['CPU Cost (jedn.)']} jedn.) | "
        f"MPLS-TE: GWARANTOWANA JAKOŚĆ (Jitter: ±{metrics['MPLS-TE']['Jitter (ms)']}ms, CPU: {metrics['MPLS-TE']['CPU Cost (jedn.)']} jedn.)", fontsize=10
    )
    ax_delay.set_xlabel('Czas [symulowany krok]')
    ax_delay.set_ylabel('Opóźnienie [ms]')
    ax_delay.grid(True, linestyle='--', alpha=0.6)

    max_real_delay = max(ip_real_delay, mpls_real_delay)
    ax_delay.set_ylim(0, max_real_delay * 1.5)
    ax_delay.set_xlim(0, total_frames)

    # Inicjalizacja linii wykresu opóźnień
    line_ip_real_delay, = ax_delay.plot([], [], 'r-', label=f'IP - Narastające (max: {ip_real_delay}ms)')
    line_mpls_real_delay, = ax_delay.plot([], [], 'g-', label=f'MPLS-TE - Stałe: {mpls_real_delay}ms')
    line_ip_base_delay = ax_delay.axhline(ip_base_delay, color='r', linestyle=':', alpha=0.5, label=f'IP - Bazowe: {ip_base_delay}ms')
    line_mpls_base_delay = ax_delay.axhline(mpls_base_delay, color='g', linestyle=':', alpha=0.5, label=f'MPLS-TE - Bazowe: {mpls_base_delay}ms')

    ax_delay.legend(loc='upper center', frameon=True, fontsize=9, edgecolor='black', ncol=4)

    # Historie danych do aktualizacji wykresów
    ip_x_hist, ip_y_hist = [], []; mpls_x_hist, mpls_y_hist = [], []
    time_points_hist, ip_real_hist, mpls_real_hist = [], [], []

    def update(frame):
        # --- Ruch Pakietu IP ---
        if frame < len(ip_points):
            current_x, current_y = ip_points[frame]
            packet_ip.set_data([current_x], [current_y]); ip_x_hist.append(current_x); ip_y_hist.append(current_y)
            current_ip_delay = ip_delay_map.get(frame, ip_real_delay)
        else:
            packet_ip.set_data([pos[END_NODE][0]], [pos[END_NODE][1]]); current_ip_delay = ip_real_delay

        # --- Ruch Pakietu MPLS ---
        if frame < len(mpls_points):
            current_x, current_y = mpls_points[frame]
            packet_mpls.set_data([current_x], [current_y]); mpls_x_hist.append(current_x); mpls_y_hist.append(current_y)
            current_mpls_delay = mpls_real_delay
        else:
            packet_mpls.set_data([pos[END_NODE][0]], [pos[END_NODE][1]]); current_mpls_delay = mpls_real_delay

        # --- Rysowanie Śladów (Trails) ---
        trail_ip.set_data(ip_x_hist, ip_y_hist); trail_mpls.set_data(mpls_x_hist, mpls_y_hist)

        # --- Aktualizacja Wykresu Opóźnień ---
        time_points_hist.append(frame); ip_real_hist.append(current_ip_delay); mpls_real_hist.append(current_mpls_delay)
        line_ip_real_delay.set_data(time_points_hist, ip_real_hist); line_mpls_real_delay.set_data(time_points_hist, mpls_real_hist)

        ax_delay.set_xlim(0, frame + 10); ax_delay.set_ylim(0, max_real_delay * 1.5)

        return packet_ip, packet_mpls, line_ip_real_delay, line_mpls_real_delay, trail_ip, trail_mpls

    ani = animation.FuncAnimation(
        fig, update, frames=total_frames, interval=70, blit=False, repeat=False)
    plt.show()

if __name__ == "__main__":
    run_phase1_simulation()