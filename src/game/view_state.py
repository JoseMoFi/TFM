from __future__ import annotations
from typing import Tuple

# Estado mínimo global (local al proceso) para compartir la celda actual del NPC con el bridge.
# Si prefieres evitar globals, puedo inyectarlo por callbacks.
_current_cell: Tuple[int, int] = (0, 0)

def set_current_cell(cx: int, cy: int) -> None:
    global _current_cell
    _current_cell = (cx, cy)

def get_current_cell() -> Tuple[int, int]:
    return _current_cell
