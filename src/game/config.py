from __future__ import annotations

# Configuración general del mundo/render
TILE: int = 48
WORLD_W: int = 200   # celdas
WORLD_H: int = 200

SCREEN_W: int = 1000
SCREEN_H: int = 700

# Colores (R, G, B)
GRASS_COLOR = (80, 130, 80)
GRID_COLOR = (120, 170, 120)
BAKERY_FILL = (194, 167, 120)
BAKERY_OUTLINE = (120, 95, 60)
NPC_COLOR = (40, 120, 255)

# Zona Panadería (en celdas, ambos inclusive)
BAKERY_X1, BAKERY_Y1 = 50, 50
BAKERY_X2, BAKERY_Y2 = 60, 60

# Movimiento
STEP_TIME: float = 0.12  # s por paso de 1 celda
CAMERA_SMOOTH: float = 1.0  # 1.0 = instantáneo; <1.0 suavizado
