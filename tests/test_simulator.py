import unittest

from network import Network, Flow
from routing import CSPF, WeightedGreedy


class TestBandwidthReservation(unittest.TestCase):
    def test_reserve_bandwidth_updates_all_edges_on_multihop_path(self):
        net = Network()
        g = net.get_graph()
        g.add_edge(0, 1, bandwidth=100, delay=1, load=0)
        g.add_edge(1, 2, bandwidth=100, delay=1, load=0)

        ok = net.reserve_bandwidth([0, 1, 2], bandwidth=30)

        self.assertTrue(ok)
        self.assertEqual(g[0][1]["load"], 30)
        self.assertEqual(g[1][2]["load"], 30)

    def test_reserve_bandwidth_fails_if_any_edge_has_not_enough_capacity(self):
        net = Network()
        g = net.get_graph()
        g.add_edge(0, 1, bandwidth=100, delay=1, load=0)
        g.add_edge(1, 2, bandwidth=20, delay=1, load=0)

        ok = net.reserve_bandwidth([0, 1, 2], bandwidth=30)

        self.assertFalse(ok)
        self.assertEqual(g[0][1]["load"], 0)
        self.assertEqual(g[1][2]["load"], 0)


class TestConstraints(unittest.TestCase):
    def test_cspf_rejects_path_when_delay_constraint_is_violated(self):
        net = Network()
        g = net.get_graph()
        g.add_edge(0, 1, bandwidth=100, delay=6, load=0)
        g.add_edge(1, 2, bandwidth=100, delay=6, load=0)

        cspf = CSPF(g)
        flow = Flow(src=0, dst=2, bandwidth=10, max_delay=10)

        self.assertIsNone(cspf.compute_path(flow))

    def test_weighted_greedy_rejects_path_when_delay_constraint_is_violated(self):
        net = Network()
        g = net.get_graph()
        g.add_edge(0, 1, bandwidth=100, delay=6, load=0)
        g.add_edge(1, 2, bandwidth=100, delay=6, load=0)

        weighted = WeightedGreedy(g, beta=3.0)
        flow = Flow(src=0, dst=2, bandwidth=10, max_delay=10)

        self.assertIsNone(weighted.compute_path(flow))


if __name__ == "__main__":
    unittest.main()