"""In-process bridge event bus — the contract §3 surface, headless transport.

Emitters speak the eight contract `__tarsEvent` types plus the P-CORE-6-decreed
`reminder` clock fire (flat-scalar payload); at P3 merge pywebview replaces
the transport (a subscriber that evaluates window.__tarsEvent) without any
emitter changing. Subscriber failures never take core down.
"""

# reminder: the P-CORE-6 clock fire — decreed by the phase prompt (payload: flat scalars,
# <= existing event shapes); every other emit stays one of the original 8.
EVENT_TYPES = frozenset({"state", "chunk", "done", "action", "transcript", "gauge", "error", "close",
                         "reminder"})


class Bus:
    """Fan-out emitter with per-subscriber fault isolation."""

    def __init__(self):
        self._subscribers = []

    def subscribe(self, handler) -> None:
        self._subscribers.append(handler)

    def emit(self, event_type: str, detail: dict) -> None:
        if event_type not in EVENT_TYPES:
            raise ValueError(f"unknown bridge event type: {event_type}")
        for handler in list(self._subscribers):
            try:
                handler(event_type, detail)
            except Exception:
                pass  # transport fault must never crash core (bridge-contract §3)
