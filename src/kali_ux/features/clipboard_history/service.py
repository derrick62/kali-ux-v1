"""Privacy-first clipboard history model. Monitoring is opt-in and backend-driven."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from hashlib import sha256
from time import time


@dataclass(frozen=True)
class Clip:
    digest: str
    text: str
    captured_at: float


class ClipboardHistory:
    def __init__(self, max_items: int = 50, max_item_bytes: int = 65536):
        self.max_items = max(1, min(max_items, 500))
        self.max_item_bytes = max(1, min(max_item_bytes, 1048576))
        self._items: deque[Clip] = deque()

    def add(self, text: str, *, sensitive: bool = False) -> bool:
        if (
            sensitive
            or not isinstance(text, str)
            or not text
            or len(text.encode("utf-8")) > self.max_item_bytes
        ):
            return False
        digest = sha256(text.encode()).hexdigest()
        if self._items and self._items[0].digest == digest:
            return False
        self._items = deque(x for x in self._items if x.digest != digest)
        self._items.appendleft(Clip(digest, text, time()))
        while len(self._items) > self.max_items:
            self._items.pop()
        return True

    def search(self, query: str = "") -> list[Clip]:
        return [x for x in self._items if query.casefold() in x.text.casefold()]

    def clear(self) -> None:
        self._items.clear()

    def snapshot(self) -> list[dict[str, object]]:
        return [{"text": x.text, "captured_at": x.captured_at} for x in self._items]
