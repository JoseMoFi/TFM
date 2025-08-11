from __future__ import annotations
import arcade
from .config import BAKERY_X1, BAKERY_Y1, BAKERY_X2, BAKERY_Y2, TILE, BAKERY_FILL, BAKERY_OUTLINE

class BakeryArea:
    """Zona rectangular que representa la panadería."""
    def __init__(self, label: str = "PANADERÍA") -> None:
        self.label = label

        self.x = BAKERY_X1 * TILE
        self.y = BAKERY_Y1 * TILE
        self.w = (BAKERY_X2 - BAKERY_X1 + 1) * TILE
        self.h = (BAKERY_Y2 - BAKERY_Y1 + 1) * TILE

    def rect_cells(self) -> list[int]:
        return [BAKERY_X1, BAKERY_Y1, BAKERY_X2, BAKERY_Y2]
    
    def draw(self) -> None:
        cx, cy = self.x + self.w / 2, self.y + self.h / 2
        arcade.draw_rectangle_filled(cx, cy, self.w, self.h, BAKERY_FILL)
        arcade.draw_rectangle_outline(cx, cy, self.w, self.h, BAKERY_OUTLINE, border_width=3)
        arcade.draw_text(self.label, self.x + 12, self.y + self.h - 28, BAKERY_OUTLINE, 16, bold=True)
