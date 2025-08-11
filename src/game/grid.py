from __future__ import annotations
import arcade
from .config import TILE, WORLD_W, WORLD_H, GRID_COLOR

class GridRenderer:
    """Dibuja la rejilla solo en el viewport visible (barato en mapas grandes)."""

    def draw_visible(self, camera: arcade.Camera, screen_w: int, screen_h: int) -> None:
        vx, vy = camera.position
        vw, vh = screen_w, screen_h

        left = max(0, (vx // TILE) * TILE - TILE)
        right = min(WORLD_W * TILE, ((vx + vw) // TILE + 2) * TILE)
        bottom = max(0, (vy // TILE) * TILE - TILE)
        top = min(WORLD_H * TILE, ((vy + vh) // TILE + 2) * TILE)

        x = left
        while x <= right:
            arcade.draw_line(x, bottom, x, top, GRID_COLOR, 1)
            x += TILE

        y = bottom
        while y <= top:
            arcade.draw_line(left, y, right, y, GRID_COLOR, 1)
            y += TILE

def cell_to_center_px(cx: int, cy: int) -> tuple[float, float]:
    return cx * TILE + TILE / 2, cy * TILE + TILE / 2

def clamp_world_px(x: float, y: float) -> tuple[float, float]:
    x = min(max(x, 0), WORLD_W * TILE)
    y = min(max(y, 0), WORLD_H * TILE)
    return x, y
