from __future__ import annotations
import arcade
from .config import SCREEN_W, SCREEN_H, GRASS_COLOR, CAMERA_SMOOTH, TILE, WORLD_W, WORLD_H
from .grid import GridRenderer
from .areas import BakeryArea
from .entities import GridWalker
from .adapters.npc_step_adapter import NpcStepAdapter
from .view_state import set_current_cell

class MainView(arcade.View):
    def __init__(self, step_adapter: NpcStepAdapter | None = None):
        super().__init__()
        arcade.set_background_color(GRASS_COLOR)
        self.camera = arcade.Camera(SCREEN_W, SCREEN_H)
        self.ui_camera = arcade.Camera(SCREEN_W, SCREEN_H)

        start_cell = (WORLD_W // 2, WORLD_H // 2)
        self.npc = GridWalker(int(TILE * 0.8), start_cell)
        set_current_cell(*start_cell)

        self.actors = arcade.SpriteList()
        self.actors.append(self.npc)

        self.grid = GridRenderer()
        self.bakery = BakeryArea()
        self.steps = step_adapter or NpcStepAdapter()

    def on_update(self, dt: float):
        # Consumir paso si el NPC está libre
        if not self.npc.is_moving() and self.steps.has_steps():
            step = self.steps.try_pop()
            if step:
                self.npc.step(*step)

        # Actualizar sprites
        self.actors.on_update(dt)
        set_current_cell(self.npc.cell_x, self.npc.cell_y)

        # Cámara centrada
        self.camera.move_to((self.npc.center_x - self.width/2, self.npc.center_y - self.height/2),
                            speed=CAMERA_SMOOTH)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.bakery.draw()
        self.grid.draw_visible(self.camera, self.window.width, self.window.height)
        self.actors.draw()
        self.ui_camera.use()
