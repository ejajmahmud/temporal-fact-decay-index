"""Core exponential-decay temporal fact store for agent memory."""
import math
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class TemporalFact:
    entity: str
    attribute: str
    value: Any
    trust: float
    timestamp: float

    def confidence(self, now: float, half_life_seconds: float) -> float:
        age = max(0.0, now - self.timestamp)
        return self.trust * math.pow(0.5, age / half_life_seconds)


class TemporalFactIndex:
    """Tracks time-decaying agent facts and resolves contradictions by effective confidence."""

    def __init__(self, half_life_seconds: float = 3600.0, min_confidence: float = 0.05):
        if half_life_seconds <= 0:
            raise ValueError("half_life_seconds must be positive")
        self.half_life_seconds = half_life_seconds
        self.min_confidence = min_confidence
        self._facts: Dict[Tuple[str, str], List[TemporalFact]] = {}

    def record(
        self,
        entity: str,
        attribute: str,
        value: Any,
        trust: float = 1.0,
        timestamp: Optional[float] = None,
    ) -> TemporalFact:
        ts = time.time() if timestamp is None else timestamp
        fact = TemporalFact(entity=entity, attribute=attribute, value=value, trust=trust, timestamp=ts)
        self._facts.setdefault((entity, attribute), []).append(fact)
        return fact

    def query(self, entity: str, attribute: str, now: Optional[float] = None) -> Optional[Dict[str, Any]]:
        now_ts = time.time() if now is None else now
        candidates = self._facts.get((entity, attribute), [])
        best = None
        best_conf = -1.0
        for f in candidates:
            conf = f.confidence(now_ts, self.half_life_seconds)
            if conf >= self.min_confidence and conf > best_conf:
                best_conf = conf
                best = f
        if not best:
            return None
        return {
            "entity": entity,
            "attribute": attribute,
            "value": best.value,
            "confidence": round(best_conf, 4),
            "observed_at": best.timestamp,
        }

    def prune_stale(self, now: Optional[float] = None) -> int:
        now_ts = time.time() if now is None else now
        removed = 0
        for key in list(self._facts.keys()):
            kept = [f for f in self._facts[key] if f.confidence(now_ts, self.half_life_seconds) >= self.min_confidence]
            removed += len(self._facts[key]) - len(kept)
            if kept:
                self._facts[key] = kept
            else:
                del self._facts[key]
        return removed
