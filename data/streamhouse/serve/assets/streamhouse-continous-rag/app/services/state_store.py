from __future__ import annotations

import threading
from collections import deque
from typing import Any

from app.models import FactoryException, FactoryState, KnowledgeDocument


class StateStore:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.factory_state: FactoryState | None = None
        self.exceptions: deque[FactoryException] = deque(maxlen=50)
        self.events: deque[dict[str, Any]] = deque(maxlen=150)
        self.documents: dict[str, KnowledgeDocument] = {}

    def set_factory_state(self, state: FactoryState) -> None:
        with self._lock:
            self.factory_state = state
            self.events.appendleft({"type": "factory_state", "data": state.model_dump()})

    def add_exception(self, exc: FactoryException) -> None:
        with self._lock:
            self.exceptions.appendleft(exc)
            self.events.appendleft({"type": "factory_exception", "data": exc.model_dump()})

    def add_document(self, doc: KnowledgeDocument) -> None:
        with self._lock:
            self.documents[doc.document_id] = doc
            self.events.appendleft(
                {
                    "type": "knowledge_update",
                    "data": {
                        "document_id": doc.document_id,
                        "title": doc.title,
                        "source": doc.source,
                        "updated_at": doc.updated_at,
                    },
                }
            )

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "factory_state": self.factory_state.model_dump() if self.factory_state else None,
                "exceptions": [item.model_dump() for item in list(self.exceptions)[:10]],
                "documents": [item.model_dump() for item in self.documents.values()],
                "events": list(self.events)[:30],
            }
