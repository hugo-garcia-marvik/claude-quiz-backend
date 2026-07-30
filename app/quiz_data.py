"""
Practice questions for Claude Certified Architect – Foundations (CCA-F).

Unofficial study material covering the five exam domains:
1. Agentic Architecture & Orchestration (27%)
2. Tool Design & MCP Integration (18%)
3. Claude Code Configuration & Workflows (20%)
4. Prompt Engineering & Structured Output (20%)
5. Context Management & Reliability (15%)
"""

QUESTIONS = [
    {
        "id": 1,
        "domain": "Agentic Architecture & Orchestration",
        "question": (
            "Estás diseñando un sistema multi-agente donde un orquestador descompone "
            "una tarea de investigación en subtareas y las asigna a subagentes. "
            "¿Cuál es el patrón más adecuado para coordinar el trabajo y consolidar resultados?"
        ),
        "options": [
            "Un único prompt monolítico que resuelve todo en un solo turno",
            "Hub-and-spoke: el orquestador despacha subtareas, recibe resultados y los sintetiza",
            "Cada subagente escribe directamente en la respuesta final del usuario sin coordinación",
            "Ejecutar todos los subagentes en un bucle infinito hasta agotar el contexto",
        ],
        "correct_index": 1,
        "explanation": (
            "El patrón hub-and-spoke es el estándar para multi-agente: un orquestador "
            "central descompone, asigna, recolecta y sintetiza. Evita el monolitismo "
            "y la falta de control de un modelo sin orquestación."
        ),
    },
    {
        "id": 2,
        "domain": "Agentic Architecture & Orchestration",
        "question": (
            "Un agente de soporte al cliente entra en un bucle de herramientas. "
            "¿Cuándo debería terminar el bucle de forma confiable?"
        ),
        "options": [
            "Solo cuando se agote el presupuesto de tokens",
            "Cuando la tarea esté resuelta, se alcance un máximo de iteraciones, o se requiera escalamiento humano",
            "Nunca: el bucle debe continuar hasta que el usuario cierre la sesión",
            "Únicamente tras invocar exactamente tres herramientas",
        ],
        "correct_index": 1,
        "explanation": (
            "Los bucles agentic deben tener criterios de terminación claros: "
            "éxito de la tarea, límite de iteraciones y rutas de escalamiento "
            "para degradación elegante."
        ),
    },
    {
        "id": 3,
        "domain": "Tool Design & MCP Integration",
        "question": (
            "Al diseñar herramientas (tools) para Claude vía MCP, ¿qué práctica "
            "mejora más la fiabilidad de las invocaciones?"
        ),
        "options": [
            "Omitir descripciones para ahorrar tokens",
            "Esquemas claros, descripciones precisas y errores estructurados (errorCategory, isRetryable, mensaje legible)",
            "Devolver siempre HTTP 200 con el error embebido en texto libre",
            "Exponer una sola herramienta genérica execute_anything",
        ],
        "correct_index": 1,
        "explanation": (
            "Tool design sólido implica contratos claros (schemas + descriptions) "
            "y respuestas de error estructuradas para que el modelo sepa si reintentar "
            "o escalar."
        ),
    },
    {
        "id": 4,
        "domain": "Tool Design & MCP Integration",
        "question": (
            "¿Cuál es una ventaja clave de usar Model Context Protocol (MCP) "
            "para integrar herramientas con Claude?"
        ),
        "options": [
            "Reemplaza por completo la necesidad de prompt engineering",
            "Estandariza cómo se exponen tools/context a clientes de IA, facilitando reutilización entre apps",
            "Elimina la autenticación y los límites de rate",
            "Obliga a que todas las tools se ejecuten solo en el navegador del usuario",
        ],
        "correct_index": 1,
        "explanation": (
            "MCP define un protocolo estándar cliente-servidor para tools y contexto, "
            "lo que permite reutilizar servidores MCP entre distintos hosts y agentes."
        ),
    },
    {
        "id": 5,
        "domain": "Claude Code Configuration & Workflows",
        "question": (
            "En Claude Code, ¿cómo se aplica la jerarquía de configuración de CLAUDE.md?"
        ),
        "options": [
            "Solo existe un CLAUDE.md global del usuario; el proyecto no puede sobreescribirlo",
            "Usuario → proyecto → directorio: las reglas más cercanas al path de trabajo tienen prioridad local",
            "Solo el archivo en la raíz del monorepo se lee; el resto se ignora",
            "CLAUDE.md solo se usa en CI/CD, no en la sesión interactiva",
        ],
        "correct_index": 1,
        "explanation": (
            "Claude Code soporta jerarquía de instrucciones (user-level, project-level, "
            "directory-level) y reglas con path-scoping para especializar comportamiento."
        ),
    },
    {
        "id": 6,
        "domain": "Claude Code Configuration & Workflows",
        "question": (
            "Un job de CI invoca `claude` sin flags y se cuelga esperando input. "
            "¿Cuál es la corrección correcta para modo no interactivo?"
        ),
        "options": [
            "Añadir solo CLAUDE_HEADLESS=true sin cambiar el comando",
            "Usar el flag -p (print) y pasar el prompt como argumento para salida no interactiva",
            "Redirigir stdin a /dev/null y esperar que complete solo",
            "Añadir el flag --batch (no estándar) y reintentar",
        ],
        "correct_index": 1,
        "explanation": (
            "Sin -p, Claude Code inicia sesión interactiva y espera stdin. "
            "Con -p (print) se ejecuta en modo no interactivo y devuelve el resultado."
        ),
    },
    {
        "id": 7,
        "domain": "Prompt Engineering & Structured Output",
        "question": (
            "Necesitas que Claude devuelva datos parseables de forma consistente "
            "para un pipeline de extracción. ¿Qué enfoque es más robusto?"
        ),
        "options": [
            "Pedir 'JSON si puedes' sin esquema ni validación",
            "Definir un esquema (tool/structured output), validar la respuesta y reintentar o corregir ante fallos",
            "Pedir markdown libre y parsear con regex ad-hoc",
            "Confiar en que el modelo siempre cumple el formato del primer ejemplo",
        ],
        "correct_index": 1,
        "explanation": (
            "Structured output + validación + estrategia de reintento/corrección "
            "es el patrón de producción para extracciones fiables."
        ),
    },
    {
        "id": 8,
        "domain": "Prompt Engineering & Structured Output",
        "question": (
            "Al diseñar un prompt de sistema para un agente de producción, "
            "¿qué elemento es más crítico incluir además de la tarea?"
        ),
        "options": [
            "Solo ejemplos de tono amable",
            "Límites de alcance, criterios de éxito, formato de salida y qué hacer ante incertidumbre",
            "Una lista de 50 sinónimos de la tarea",
            "Instrucciones para ignorar cualquier tool disponible",
        ],
        "correct_index": 1,
        "explanation": (
            "Los prompts de producción deben acotar el rol, definir éxito/fallo, "
            "formato de salida y políticas ante ambigüedad o falta de datos."
        ),
    },
    {
        "id": 9,
        "domain": "Context Management & Reliability",
        "question": (
            "Una conversación larga con un agente se acerca al límite de contexto. "
            "¿Cuál es la mejor estrategia de fiabilidad?"
        ),
        "options": [
            "Ignorar el límite y confiar en que el modelo recuerde todo",
            "Resumir/compactar estado relevante, priorizar hechos críticos y descartar ruido",
            "Borrar siempre el system prompt para liberar tokens",
            "Duplicar el historial completo en cada mensaje para 'reforzar memoria'",
        ],
        "correct_index": 1,
        "explanation": (
            "La gestión de contexto en producción usa compactación, priorización "
            "de estado y retención de hechos críticos, no duplicación del historial."
        ),
    },
    {
        "id": 10,
        "domain": "Context Management & Reliability",
        "question": (
            "Un agente de soporte no puede resolver un caso tras varios intentos de tools. "
            "¿Qué patrón de fiabilidad aplica?"
        ),
        "options": [
            "Repetir la misma tool indefinidamente",
            "Degradación elegante: informar límites, ofrecer alternativas y escalar a humano cuando corresponda",
            "Inventar una solución para no dejar al usuario sin respuesta",
            "Cerrar la sesión sin mensaje",
        ],
        "correct_index": 1,
        "explanation": (
            "Graceful degradation y escalamiento humano son patrones clave de "
            "fiabilidad: no inventar, comunicar límites y transferir cuando el "
            "agente no puede resolver."
        ),
    },
]


from typing import Any, Dict, List, Optional


def get_questions_public() -> List[Dict[str, Any]]:
    """Return questions without correct answers (for the client)."""
    return [
        {
            "id": q["id"],
            "domain": q["domain"],
            "question": q["question"],
            "options": q["options"],
        }
        for q in QUESTIONS
    ]


def get_question_by_id(question_id: int) -> Optional[Dict[str, Any]]:
    for q in QUESTIONS:
        if q["id"] == question_id:
            return q
    return None
