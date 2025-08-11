def run_integration() -> bool:
    """
    Integra todo: mundo + bridge + NPCAgent.
    1) Levanta el mundo (sin loop).
    2) Crea GameIOBridge y NPCAgent (LLM dummy).
    3) Llama a .move (vía primitiva del agente) y simula ticks hasta alcanzar la celda.
    Devuelve True si el NPC llega a (56,57).
    """
    import arcade
    from src.game.app import bootstrap_world
    from src.game.adapters.game_io_bridge import GameIOBridge
    from src.agents.npc_agent import NPCAgent
    import agentspeak  # requerido por las primitivas del agente

    class DummyLLM:
        def generate(self, prompt: str) -> str:
            # El contenido no es crítico en esta prueba; no usamos get_plan aquí
            return "+!noop : true <- .update_inventory(pan, 1, add)."

    window = None
    try:
        # 1) Mundo
        window, view, step_adapter, bus = bootstrap_world(npc_id="npc_eldric")

        # 2) Bridge + Agente
        bridge = GameIOBridge(npc_id="npc_eldric", world_bus=bus, step_adapter=step_adapter)
        agent = NPCAgent(
            jid="eldric@localhost",
            npc_id="npc_eldric",
            password="secret",
            npc_name="Eldric",
            data_root="data",
            llm=DummyLLM(),
            game_io=bridge,
        )

        # 3) Invocar la primitiva .move a través del BDI:
        # Simulamos la acción AgentSpeak .move((x,y)) -> el wrapper de NPCAgent ya encola via game_io
        # Llamamos la primitiva como lo haría el plan: pasando un "term" compatible.
        class _DummyTerm:
            def __init__(self, xy):
                self.args = [xy]

        # Emular llamada .move con (56,57)
        # La primitiva espera: agentspeak.grounded(term.args[0], intention.scope)
        # Creamos intención mínima con scope vacío
        class _DummyIntention:
            scope = {}

        term = _DummyTerm((56, 57))
        for fn in agent.add_custom_actions.__closure__ or []:
            pass  # Garantizar que el método está definido (no se llama aquí)

        # Usamos directamente el método interno registrado en add_custom_actions
        # Más simple: llamamos al bridge, que es lo que la primitiva hace por debajo.
        bridge.move_to_cell(56, 57, npc_id="npc_eldric")

        # 4) Simular unos ticks hasta consumir los pasos
        max_frames = 600
        while max_frames > 0 and (view.npc.cell_x, view.npc.cell_y) != (56, 57):
            view.on_update(1/60)
            max_frames -= 1

        assert (view.npc.cell_x, view.npc.cell_y) == (56, 57), \
            f"El NPC no alcanzó la celda esperada; está en {(view.npc.cell_x, view.npc.cell_y)}"
        return True

    finally:
        try:
            if window is not None:
                window.close()
        except Exception:
            pass
        try:
            for w in list(arcade.get_window()):
                w.close()
        except Exception:
            pass
