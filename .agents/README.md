# Configuración de Agentes del Proyecto (`.agents/`)

Esta carpeta contiene las personalizaciones y subagentes exclusivos para este proyecto.

## Estructura de Directorios

- **`agents/`**: Define subagentes especializados en formato Markdown (`.md`).
  - Ejemplo: `agents/code-reviewer.md`
- **`skills/`** *(opcional)*: Guías paso a paso y flujos de trabajo específicos (`skills/<nombre>/SKILL.md`).
- **`rules/`** *(opcional)*: Reglas adicionales de contexto o módulos específicos.

## ¿Cómo añadir un nuevo subagente?
1. Crea un nuevo archivo en `.agents/agents/<nombre-agente>.md`.
2. Incluye el encabezado YAML (`name`, `description`, `tools`, `subagent: true`).
3. Define las instrucciones y el rol en formato Markdown en el cuerpo del archivo.
