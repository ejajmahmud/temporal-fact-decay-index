"""CLI for Temporal Fact Decay Index."""
import argparse
import json
from .core import TemporalFactIndex


def main():
    parser = argparse.ArgumentParser(description="Temporal Fact Decay Index CLI")
    parser.add_argument("--half-life", type=float, default=3600.0, help="Confidence half-life in seconds")
    args = parser.parse_args()

    idx = TemporalFactIndex(half_life_seconds=args.half_life)
    idx.record("db-primary", "role", "readonly", trust=0.9, timestamp=1000.0)
    idx.record("db-primary", "role", "readwrite", trust=0.95, timestamp=5000.0)
    print(json.dumps(idx.query("db-primary", "role", now=5000.0), indent=2))


if __name__ == "__main__":
    main()
