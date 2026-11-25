"""Tests for Temporal Fact Decay Index."""
import unittest
from temporal_fact_decay_index.core import TemporalFactIndex


class TestTemporalFactIndex(unittest.TestCase):
    def test_half_life_decay_and_recency_winner(self):
        idx = TemporalFactIndex(half_life_seconds=100.0, min_confidence=0.1)
        idx.record("node1", "state", "down", trust=1.0, timestamp=0.0)
        idx.record("node1", "state", "up", trust=0.8, timestamp=200.0)
        res = idx.query("node1", "state", now=200.0)
        self.assertEqual(res["value"], "up")
        self.assertAlmostEqual(res["confidence"], 0.8, places=3)

    def test_prunes_below_minimum_confidence(self):
        idx = TemporalFactIndex(half_life_seconds=10.0, min_confidence=0.2)
        idx.record("svc", "v", "old", trust=1.0, timestamp=0.0)
        self.assertIsNone(idx.query("svc", "v", now=100.0))
        self.assertEqual(idx.prune_stale(now=100.0), 1)
