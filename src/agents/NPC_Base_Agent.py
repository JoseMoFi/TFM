from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from spade_bdi.bdi import BDIAgent
from src.utils.keys import GEMINI_API
from src.utils.utils import *
# import agentspeak  # cuando definas acciones
# import spade

# Si usas LLM (opcional)
import google.generativeai as genai

# ------------------------------------------------------------------------------
# Config de rutas (dataclass)
# ------------------------------------------------------------------------------
@dataclass(frozen=True)
class NPCPaths:
    data_root: Path
    npc_name: str

    @property
    def profiles_dir(self) -> Path:      return self.data_root / "npc_profiles"
    @property
    def memory_dir(self) -> Path:        return self.data_root / "memory"
    @property
    def relationships_dir(self) -> Path: return self.data_root / "relationships"
    @property
    def primitives_base(self) -> Path:   return self.data_root / "primitives_base"
    @property
    def intentions_dir(self) -> Path:    return self.data_root / "npc_intentions"
    @property
    def world_histories_dir(self) -> Path: return self.data_root / "world_histories"

    # Archivos del NPC
    @property
    def profile(self) -> Path:           return self.profiles_dir / f"{self.npc_name}.json"      # OBLIGATORIO
    @property
    def dynamic_memory(self) -> Path:    return self.memory_dir / f"{self.npc_name}_dynamic.json"
    @property
    def relationships(self) -> Path:     return self.relationships_dir / f"{self.npc_name}.json"
    @property
    def intentions_asl(self) -> Path:    return self.intentions_dir / f"{self.npc_name}.asl"
    @property
    def intentions_json(self) -> Path:   return self.intentions_dir / f"{self.npc_name}.json"
    @property
    def common_history_json(self) -> Path: return self.world_histories_dir / "common_history.json" # OBLIGATORIO

    # Bases
    @property
    def base_asl(self) -> Path:          return self.primitives_base / "primitivas.asl" # OBLIGATORIO
    @property
    def base_json(self) -> Path:         return self.primitives_base / "primitivas.json" # OBLIGATORIO


# ------------------------------------------------------------------------------
# Inventario (igual que tenías, con pequeño saneo)
# ------------------------------------------------------------------------------
class Inventory:
    def __init__(self, bdi_interface=None):
        self.items: Dict[str, int] = {}
        self.bdi = bdi_interface

    def add(self, obj: str, count: int = 1) -> None:
        self.items[obj] = self.items.get(obj, 0) + count
        self._update_belief(obj)

    def subtract(self, obj: str, count: int = 1) -> None:
        if self.items.get(obj, 0) >= count:
            self.items[obj] -= count
            if self.items[obj] <= 0:
                del self.items[obj]
        self._update_belief(obj)

    def count(self, obj: str) -> int:
        return self.items.get(obj, 0)

    def _update_belief(self, obj: str) -> None:
        if not self.bdi:
            return
        cnt = self.count(obj)
        if cnt > 0:
            self.bdi.set_belief("has", [obj, cnt])
        else:
            self.bdi.remove_belief("has", [obj])


# ------------------------------------------------------------------------------
# Agente NPC: robusto a ficheros faltantes (salvo profile)
# ------------------------------------------------------------------------------
class NPCBaseAgent(BDIAgent):
    """
    - Requiere que exista data/npc_profiles/<npc>.json (perfil). Si no, levanta error.
    - Crea si faltan: memory/<npc>_*.json, relationships/<npc>.json, npc_intentions/<npc>.{asl,json}
      (copiando desde primitives_base si existen; si no, genera mínimos).
    - Expone strings formateados para inyectar en tu prompt.
    """

    def __init__(
        self,
        jid: str,
        npc_id: str,
        password: str,
        npc_name: str,
        data_root: str | Path = "data",
        # gemini_api_key: Optional[str] = None,  # si quieres inyectarlo aquí
    ):
        self.npc_name = npc_name
        self.npc_id = npc_id

        # Configuración de logger por NPC
        log_dir = NPC_LOG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{self.npc_name}.log"

        self.logger = logging.getLogger(f"npc.{npc_name}")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setLevel(logging.INFO)
            fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
            self.logger.addHandler(fh)

        self.logger.info(f"Inicializando NPC {npc_name} (ID: {npc_id})")

        self.paths = NPCPaths(Path(data_root), npc_name)

        # 1) Validar perfil obligatorio (no se auto‑genera)
        self._ensure_profile_exists()

        # 2) Bootstrap del resto
        self._bootstrap_optional_files()

        # 3) Cargar materiales de prompt (creencias/funciones/acciones)
        self._load_prompt_material()

        # 4) Construir historia formateada
        self._build_formatted_history()

        # 5) Estado auxiliar
        self.inventory = Inventory(self.bdi)

        # 6) Iniciar BDI con el .asl del NPC (ya garantizado)
        super().__init__(jid, password, str(self.paths.intentions_asl))

        # 7) Si usas LLM, inicializa aquí (descomenta si procede)
        if GEMINI_API:
            genai.configure(api_key=GEMINI_API)
            self.model = genai.GenerativeModel("models/gemini-2.5-flash")

    # ---------- Validaciones y bootstrap ----------
    def _ensure_profile_exists(self) -> None:
        """El perfil debe existir; si no, error con instrucción clara."""
        if not self.paths.profile.exists():
            msg = (
                f"Perfil obligatorio no encontrado: {self.paths.profile}\n"
                f"Créalo a partir de un ejemplo. Ejemplo mínimo:\n\n"
                f'{{\n'
                f'  "nombre": "{self.npc_name}",\n'
                f'  "edad": "", "ciudad": "", "profesion": "",\n'
                f'  "virtudes": [], "debilidades": [],\n'
                f'  "inventario": [], "personalidad": {{}}\n'
                f'}}\n'
            )
            raise FileNotFoundError(msg)
    
    def _ensure_history_exists(self) -> None:
        """El perfil debe existir; si no, error con instrucción clara."""
        if not self.paths.common_history_json.exists():
            msg = (
                f"Historia del mundo no encontrada: {self.paths.common_history_json}\n"
                r"Créalo a partir de una historia inventada con formato: { historia: ..., pueblos: {pueblo_n: historia pueblo_n}}"
            )
            raise FileNotFoundError(msg)

    def _bootstrap_optional_files(self) -> None:
        """Crea los demás archivos si faltan; copia de base cuando sea posible."""
        # Memorias y relaciones
        if not self.paths.dynamic_memory.exists():
            write_json(self.paths.dynamic_memory, {"emocion": "", "objetivo_actual": "", "historial_breve": []})
        if not self.paths.relationships.exists():
            write_json(self.paths.relationships, {})

        # Intenciones JSON
        if not self.paths.intentions_json.exists():
            if self.paths.base_json.exists():
                ensure_dir(self.paths.intentions_json.parent)
                shutil.copy2(self.paths.base_json, self.paths.intentions_json)
                self.logger.info("Copiado base JSON a %s", self.paths.intentions_json)
            else:
                write_json(self.paths.intentions_json, {"beliefs": {}, "functions": {}, "actions": {}})

        # Intenciones ASL
        if not self.paths.intentions_asl.exists():
            if self.paths.base_asl.exists():
                ensure_dir(self.paths.intentions_asl.parent)
                shutil.copy2(self.paths.base_asl, self.paths.intentions_asl)
                self.logger.info("Copiado base ASL a %s", self.paths.intentions_asl)
            else:
                ensure_dir(self.paths.intentions_asl.parent)
                self.paths.intentions_asl.write_text(
                    f"% Planes iniciales para {self.npc_name}\n",
                    encoding="utf-8"
                )

    # ---------- Prompt material ----------
    def _load_prompt_material(self) -> None:
        data = read_json(self.paths.intentions_json, self.logger, default={"beliefs": {}, "functions": {}, "actions": {}})

        self.str_beliefs = "\n".join(
            f"*{k}:\n\t- descripcion: {v}" for k, v in data.get("beliefs", {}).items()
        )
        self.str_functions = "\n".join(
            f"*{k}:\n\t- descripcion: {v}" for k, v in data.get("functions", {}).items()
        )
        self.str_intentions_actions = "\n".join([
            f"*{name}:\n\t- descripcion: {meta.get('description','')}\n\t- plan: " +
            "\n\t\t".join(meta.get("plans", []))
            for name, meta in data.get("actions", {}).items()
        ])

    # ---------- Historia formateada ----------
    def _build_formatted_history(self) -> None:
        profile = read_json(self.paths.profile, self.logger, default={})
        long_m = profile.get("history")
        dyn_m   = read_json(self.paths.dynamic_memory, self.logger, default={})
        rels    = read_json(self.paths.relationships, self.logger, default={})

        perfil_str = [
            "[📇 PERFIL DE PERSONAJE]",
            f"Nombre: {profile.get('nombre','')}",
            f"Edad: {profile.get('edad','')}",
            f"Ciudad: {profile.get('ciudad','')}",
            f"Profesión: {profile.get('profesion','')}",
            f"Virtudes: {', '.join(profile.get('virtudes', []))}",
            f"Debilidades: {', '.join(profile.get('debilidades', []))}",
            f"Inventario actual: {', '.join(profile.get('inventario', []))}",
            "Personalidad:"
        ]
        for k, v in profile.get("personalidad", {}).items():
            perfil_str.append(f"- {k.capitalize()}: {v}")

        eventos = long_m.get("eventos", {})
        eventos_str = "\n".join([f"- {k.replace('_',' ').capitalize()}: {v}" for k, v in eventos.items()])

        memoria_str = f"""[MEMORIA A LARGO PLAZO]
            Resumen:
            {long_m.get('resumen','')}

            Eventos:
            {eventos_str}

            Historia personal:
            {long_m.get('historia_personal','')}
        """

        rels_str = "\n".join([f"- {n}: relación = {v}" for n, v in rels.items()])
        relaciones_fmt = f"""[🤝 RELACIONES]
            {rels_str}
        """

        dyn_fmt = f"""[⚙️ ESTADO DINÁMICO]
            Emoción: {dyn_m.get('emocion','')}
            Objetivo: {dyn_m.get('objetivo_actual','')}
        """

        self._history = "\n\n".join([
            "\n".join(perfil_str).strip(),
            memoria_str.strip(),
            relaciones_fmt.strip(),
            dyn_fmt.strip()
        ])

    def get_history(self) -> str:
        return getattr(self, "_history", "")

    # ---------- Biblioteca de intenciones ----------
    def save_new_intention(self, intention_name: str, trigger: str, description: str, plan: str) -> None:
        """
        Guarda en JSON (biblioteca de planes) y recarga planes del BDI.
        Concatena .asl base + planes del JSON.
        """
        data = read_json(self.paths.intentions_json, self.logger, default={})
        data[intention_name] = {
            "trigger": trigger,
            "description": description,
            "plan": plan,
        }
        write_json(self.paths.intentions_json, data)

        # Recargar planes
        plans_from_json = "\n\n".join(
            v["plan"] for v in data.values() if isinstance(v, dict) and "plan" in v
        )
        base_asl_text = self.paths.intentions_asl.read_text(encoding="utf-8") if self.paths.intentions_asl.exists() else ""
        all_plans = (base_asl_text + "\n\n" + plans_from_json).strip()

        self.set_bdi_plans(all_plans)
        self.logger.info("[%s] Intention '%s' guardada y planes recargados.", self.npc_name, intention_name)
