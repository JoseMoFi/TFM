def run_agent_plan() -> bool:
    """
    Crea un NPCAgent con un LLM de prueba y llama a get_plan().
    Devuelve True si genera texto (no vacío) y no hay errores.
    """
    from src.agents.npc_agent import NPCAgent

    class DummyLLM:
        def generate(self, prompt: str) -> str:
            # Plan AgentSpeak de ejemplo (válido a nivel sintáctico para biblioteca)
            return (
                "+!ir_a_panaderia : true <-\n"
                "    .move((55,55));\n"
                "    .update_inventory(harina, 1, add).\n"
            )

    # No pasamos game_io aquí; solo probamos la generación de plan
    agent = NPCAgent(
        jid="eldric@localhost",
        npc_id="npc_eldric",
        password="secret",
        npc_name="Eldric",
        data_root="data",
        llm=DummyLLM(),
        game_io=None,
    )
    env_desc = "NPC en (54,54). Panadería en recta [50,50,60,60]."
    plan_text = agent.get_plan(env_desc)
    assert isinstance(plan_text, str)
    assert len(plan_text.strip()) > 0, "El LLM dummy debería devolver un plan no vacío"
    return True
