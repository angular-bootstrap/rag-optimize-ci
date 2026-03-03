import tempfile
import unittest

from ragopt.adapters import get_adapter
from ragopt.config import load_config
from ragopt.engine import recommend, run_evaluation
from ragopt.metrics import citation_hit_rate, groundedness, overlap_f1, overall_score
from ragopt.reporting import build_run_markdown


class MetricsTests(unittest.TestCase):
    def test_overlap_f1_basic(self):
        self.assertEqual(overlap_f1("retrieval augmented generation", "retrieval augmented generation"), 1.0)

    def test_groundedness_partial(self):
        g = groundedness("cats like milk", ["cats like fish"])
        self.assertTrue(0 < g < 1)

    def test_citation(self):
        self.assertEqual(citation_hit_rate("answer [1] [2]", ["a", "b"]), 1.0)

    def test_penalty(self):
        s_fast = overall_score(0.8, 0.8, 1.0, 100, 0.001, 1000, 0.01, 0.45, 0.25, 0.15, 0.10, 0.05)
        s_slow = overall_score(0.8, 0.8, 1.0, 900, 0.009, 1000, 0.01, 0.45, 0.25, 0.15, 0.10, 0.05)
        self.assertGreater(s_fast, s_slow)


class ConfigAndEngineTests(unittest.TestCase):
    def test_load_config(self):
        cfg = load_config("examples/ragopt.yaml")
        self.assertEqual(len(cfg.candidates), 2)
        self.assertAlmostEqual(cfg.policy.weights.quality, 0.45)

    def test_end_to_end(self):
        cfg = load_config("examples/ragopt.yaml")
        with tempfile.TemporaryDirectory() as td:
            result = run_evaluation(cfg, artifacts_dir=td)
            self.assertEqual(len(result.candidates), 2)
            rec = recommend(result)
            self.assertIn(rec.winner, {"baseline-lite", "candidate-detailed"})
            md = build_run_markdown(result, rec)
            self.assertIn("| Candidate | Quality |", md)


class AdapterTests(unittest.TestCase):
    def test_provider_lookup(self):
        self.assertEqual(type(get_adapter("mock")).__name__, "MockAdapter")
        self.assertEqual(type(get_adapter("openai")).__name__, "OpenAIAdapter")
        self.assertEqual(type(get_adapter("ollama")).__name__, "OllamaAdapter")
        self.assertEqual(type(get_adapter("local-http")).__name__, "LocalHTTPAdapter")

    def test_unknown_provider(self):
        with self.assertRaises(ValueError):
            get_adapter("nope")


if __name__ == "__main__":
    unittest.main()
