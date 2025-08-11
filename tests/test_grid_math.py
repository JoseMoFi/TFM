from src.game.grid import cell_to_center_px
from src.game.config import TILE

def test_cell_to_center_px():
    cx, cy = 10, 7
    x, y = cell_to_center_px(cx, cy)
    assert x == cx * TILE + TILE / 2
    assert y == cy * TILE + TILE / 2