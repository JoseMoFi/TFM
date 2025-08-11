def run_world_smoke() -> bool:
    """
    Smoke test: crear mundo, dibujar un frame y cerrar.
    Devuelve True si no hay excepciones.
    """
    import arcade
    from src.game.app import bootstrap_world

    window = None
    try:
        window, view, step_adapter, bus = bootstrap_world(npc_id="npc_eldric")
        # Forzamos un par de updates/draws sin event loop
        for _ in range(3):
            view.on_update(1/60)
            view.on_draw()
        return True
    finally:
        # Cerrar ventana limpia
        try:
            if window is not None:
                window.close()
        except Exception:
            pass
        # En algunas plataformas, asegurar que no queden ventanas colgando
        try:
            for w in list(arcade.get_window()):
                w.close()
        except Exception:
            pass
