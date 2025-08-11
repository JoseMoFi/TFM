# src/agents/npc_agent.py
from __future__ import annotations

import logging
from typing import Any, Tuple, Optional

import agentspeak  # SPADE-BDI/AgentSpeak

from .npc_base_agent import NPCBaseAgent


class NPCAgent(NPCBaseAgent):
    """
    Agente completo: registra primitivas BDI e integra el LLM para generar planes.
    - Primitivas: .move, .catch, .drop, .search, .update_inventory, funciones .accessible, .object_at
    - LLM opcional: self.llm (inyectable) con interfaz .generate(prompt)->str
    - El destino de movimiento espera coordenadas (x,y) (tuplas/listas o "x,y")
    """

    def __init__(
        self,
        jid: str,
        npc_id: str,
        password: str,
        npc_name: str,
        data_root: str | None = "data",
        llm: Any | None = None,
        game_io: Any | None = None,  # opcional: puente hacia el mundo (colas)
    ):
        self.llm = llm
        self.game_io = game_io  # si lo usas, debe exponer move_to_cell(x,y, npc_id=...) y say(...)
        super().__init__(jid, npc_id, password, npc_name, data_root)

        # Alias de logger de la base
        self.logger: logging.Logger = self.logger
        self.logger.info("NPCAgent inicializado (LLM=%s, game_io=%s)", bool(llm), bool(game_io))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_site_to_xy(site: Any) -> Optional[Tuple[int, int]]:
        """Acepta (x,y), [x,y], 'x,y' o {'x':x,'y':y}. Devuelve (x,y) ints o None."""
        try:
            if isinstance(site, (tuple, list)) and len(site) == 2:
                x, y = site
                return int(x), int(y)
            if isinstance(site, str) and "," in site:
                sx, sy = site.split(",", 1)
                return int(sx.strip()), int(sy.strip())
            if isinstance(site, dict) and "x" in site and "y" in site:
                return int(site["x"]), int(site["y"])
        except Exception:
            return None
        return None

    # ------------------------------------------------------------------
    # Registro de primitivas y funciones para el BDI
    # (SPADE-BDI llamará a este hook)
    # ------------------------------------------------------------------
    def add_custom_actions(self, actions):
        # ============= FUNCIONES =============
        @actions.add_function(".accessible", (object,))
        def _accessible(location):
            """
            Devuelve True si la ubicación es accesible.
            Aquí puedes consultar el mundo real o un mapa local.
            Por ahora devolvemos True para no bloquear planes.
            """
            return True

        @actions.add_function(".object_at", ())
        def _object_at():
            """
            Devuelve lista de pares (objeto, location) visibles.
            Sustituye por tu percepción real cuando la conectes.
            """
            # Ejemplo mínimo sin entorno: vacío
            return []

        # ============= ACCIONES =============
        @actions.add(".search", 1)
        def _search(agent, term, intention):
            """
            Busca la ubicación de un objeto y actualiza la creencia object_at(Object, Location).
            Aquí pon tu lógica real; de momento ejemplifica asentando una creencia stub.
            """
            obj = agentspeak.grounded(term.args[0], intention.scope)
            # Stub: asumimos que está “cerca” en (10,5)
            self.bdi.set_belief("object_at", [obj, (10, 5)])
            self.logger.info("SEARCH → object_at(%s, %s)", obj, (10, 5))
            yield

        @actions.add(".move", 1)
        def _move(agent, term, intention):
            """
            Mueve al NPC a Site, donde Site = (x,y) | 'x,y' | {'x':..,'y':..}
            Si hay game_io, encolamos la acción hacia el mundo físico.
            """
            site = agentspeak.grounded(term.args[0], intention.scope)
            xy = NPCAgent._normalize_site_to_xy(site)
            if xy is None:
                self.logger.error("MOVE inválido: Site=%r", site)
                return
            x, y = xy
            if self.game_io is not None and hasattr(self.game_io, "move_to_cell"):
                # Enviar al mundo (no bloqueante)
                try:
                    self.game_io.move_to_cell(x, y, npc_id=self.npc_id)
                    self.logger.info("MOVE → encolado a (%d,%d)", x, y)
                except Exception as e:
                    self.logger.error("MOVE fallo al encolar (%d,%d): %s", x, y, e)
            else:
                # Si no hay game_io, al menos loggeamos.
                self.logger.info("MOVE (sin game_io) -> (%d,%d)", x, y)
            yield

        @actions.add(".catch", 1)
        def _catch(agent, term, intention):
            obj = agentspeak.grounded(term.args[0], intention.scope)
            # Aquí podrías validar proximidad y actualizar inventario:
            try:
                self.inventory.add(str(obj), 1)
                self.logger.info("CATCH → %s (nuevo conteo=%d)", obj, self.inventory.count(str(obj)))
            except Exception as e:
                self.logger.error("CATCH error: %s", e)
            yield

        @actions.add(".drop", 2)
        def _drop(agent, term, intention):
            obj = agentspeak.grounded(term.args[0], intention.scope)
            site = agentspeak.grounded(term.args[1], intention.scope)
            xy = NPCAgent._normalize_site_to_xy(site)
            if xy is None:
                self.logger.error("DROP inválido: obj=%r site=%r", obj, site)
                return
            try:
                # Lógica mínima: quitar de inventario; en mundo real, crear objeto en celda xy
                self.inventory.subtract(str(obj), 1)
                self.logger.info("DROP → %s en %s (conteo=%d)", obj, xy, self.inventory.count(str(obj)))
            except Exception as e:
                self.logger.error("DROP error: %s", e)
            yield

        @actions.add(".update_inventory", 3)
        def _update_inventory(agent, term, intention):
            obj = str(agentspeak.grounded(term.args[0], intention.scope))
            count = int(agentspeak.grounded(term.args[1], intention.scope))
            op = str(agentspeak.grounded(term.args[2], intention.scope))
            try:
                if op == "add":
                    self.inventory.add(obj, count)
                elif op == "subtract":
                    self.inventory.subtract(obj, count)
                else:
                    self.logger.error("UPDATE_INVENTORY op desconocida: %s", op)
                self.logger.info("UPDATE_INVENTORY → %s %s (%d) => %d", op, obj, count, self.inventory.count(obj))
            except Exception as e:
                self.logger.error("UPDATE_INVENTORY error: %s", e)
            yield

    # ------------------------------------------------------------------
    # LLM: generación de plan en AgentSpeak (opcional)
    # ------------------------------------------------------------------
    def get_plan(self, env_description: str) -> str:
        """
        Construye el prompt y llama al LLM (si está disponible).
        Devuelve texto AgentSpeak listo para alimentar al BDI.
        """
        if not self.llm:
            self.logger.warning("get_plan llamado sin LLM configurado.")
            return ""

        prompt_splitter = "# _ _ _ #"
        prompt = f"""
            Eres un **NPC llamado {self.npc_name}** dentro de un **RPG medieval**. 
            Tu personalidad e historia sirven como contexto para tu tono y prioridades (más o menos hostil, obediente, generoso, etc.).

            Tu comportamiento está gobernado por:
            - Un sistema **BDI** donde defines **intenciones** (+!intencion) que se disparan por **creencias** positivas.
            - Un conjunto de **acciones primitivas** que ejecutan efectos en el entorno.
            - **Funciones** auxiliares solo usables dentro del cuerpo del plan (nunca en el trigger).
            - Un **sistema externo (LLM/orquestador)** que prepara las creencias para activar la intención correcta.

            ======================
            CONTEXTO DEL PERSONAJE
            ======================
            {self.get_history()}

            ======================
            ACCIONES DISPONIBLES
            ======================
            (Usa únicamente estas acciones/intenciones; no inventes nuevas)
            {self.str_intentions_actions}

            ======================
            FUNCIONES DISPONIBLES
            ======================
            (Usables solo en el cuerpo del plan; nunca en el trigger)
            {self.str_functions}

            ======================
            CREENCIAS DISPONIBLES
            ======================
            (Usa exclusivamente estas; no inventes predicados nuevos)
            {self.str_beliefs}

            ======================
            ESTADO ACTUAL DEL NPC
            ======================
            {env_description}

            ===============================
            REGLAS ESTRICTAS PARA EL PLAN
            ===============================
            1) Define **UNA sola intención** (+!nombre_intencion) con **un trigger de creencias positivas** (sin 'not').
            2) El cuerpo del plan debe usar SOLO:
            - Acciones primitivas listadas (p.ej., .move, .catch, .drop, .search, .update_inventory).
            - Otras intenciones ya existentes si las hubiera (subplanes).
            - Funciones listadas (solo dentro del cuerpo).
            3) **Coordenadas en grid**: considera que **Site = (X,Y)** (tupla o equivalente). No uses nombres de zonas salvo que vengan como creencia.
            4) El plan debe ser **ejecutable y sintácticamente válido** en AgentSpeak/SPADE.
            5) **No** repitas la misma intención con múltiples condiciones. **Una única versión** por intención.
            6) **No** declares funciones nuevas ni creencias no listadas. **No** comentes el código ni expliques nada.
            7) Estás usando el motor BDI SPADE_bdi para generar los planes.

            ======================
            EJEMPLO DE SALIDA ESPERADA
            ======================
            +!atender_cliente(Object, Site) : has(Object, Count) & accessible(Site) <-
                !move_to(Site);
                !drop_object(Object).

            ======================
            OBJETIVO
            ======================
            Genera un bloque AgentSpeak **válido y reutilizable** con:
            - **Una sola** intención (+!nombre_intencion).
            - Un plan que responda al estado de creencias proporcionado, usando acciones/intenciones existentes.

            ======================
            FORMATO DE RESPUESTA
            ======================
            (Sin explicaciones, sin comentarios)

            [AGENTSPEAK]

            {prompt_splitter}

            [intencion_1 : descripción funcional general]
        """.strip()

        try:
            # Interfaz esperada: self.llm.generate(prompt) -> str
            plan_text: str = self.llm.generate(prompt)
            plan_text = (plan_text or "").strip()
            self.logger.info("Plan LLM generado (%d chars)", len(plan_text))
            return plan_text
        except Exception as e:
            self.logger.error("Error generando plan con LLM: %s", e)
            return ""
