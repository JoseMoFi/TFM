# TFM - Simulación con NPCs controlados por BDI + LLM

Este proyecto implementa un entorno de simulación en 2D con **Arcade** donde NPCs son controlados por un sistema **BDI** (Belief-Desire-Intention) coordinado con un **LLM** para generación de planes.

## 📦 Estructura del proyecto

src/
game/ # Mundo físico (mapa, grid, pathfinding, render)
agents/ # Lógica BDI de los NPCs
utils/ # Utilidades y constantes
main.py # Punto de entrada del juego
data/
npc_profiles/ # Perfiles estáticos de NPCs
npc_intentions/ # Intenciones y planes específicos
primitives_base/ # Planes y creencias base
assets/ # Sprites, sonidos, mapas
stable_versions/ # Versiones estables archivadas
tests/ # Pruebas

## Instalación

1. Clona el repositorio:
git clone git@github.com:TU_USUARIO/TU_REPO.git
cd TU_REPO
