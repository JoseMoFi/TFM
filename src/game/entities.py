from __future__ import annotations
import arcade
from .config import TILE, NPC_COLOR, STEP_TIME
from .grid import cell_to_center_px

class GridWalker(arcade.SpriteSolidColor):
    """Sprite cuadrado que se mueve por rejilla (4 direcciones, 1 celda/paso)."""

    def __init__(self, size: int, start_cell: tuple[int, int]) -> None:
        super().__init__(size, size, NPC_COLOR)
        self.cell_x, self.cell_y = start_cell
        self.center_x, self.center_y = cell_to_center_px(self.cell_x, self.cell_y)
        self._target_px = (self.center_x, self.center_y)
        self._moving: bool = False
        self._t: float = 0.0

    # ---- API de alto nivel: mover 1 celda ----
    def step(self, dx: int, dy: int) -> None:
        if (abs(dx) + abs(dy)) != 1:
            return
        self.cell_x += dx
        self.cell_y += dy
        self._target_px = cell_to_center_px(self.cell_x, self.cell_y)
        self._moving = True
        self._t = 0.0

    def is_moving(self) -> bool:
        return self._moving

    # ---- Update ----
    def on_update(self, delta_time: float = 1/60) -> None:
        if not self._moving:
            return
        self._t += delta_time
        alpha = min(self._t / STEP_TIME, 1.0)
        # LERP hacia el objetivo
        self.center_x += (self._target_px[0] - self.center_x) * alpha
        self.center_y += (self._target_px[1] - self.center_y) * alpha
        if self._t >= STEP_TIME - 1e-6:
            self.center_x, self.center_y = self._target_px
            self._moving = False
