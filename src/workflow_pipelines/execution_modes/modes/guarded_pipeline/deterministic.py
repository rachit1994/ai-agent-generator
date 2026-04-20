"""Deterministic fallbacks when planner LLM returns empty text."""

from __future__ import annotations


def deterministic_planner_doc(task: str) -> str:
    return (
        "# Plan\n\n"
        "## Requirements\n"
        f"- Task: {task}\n\n"
        "## API contract\n"
        "- POST /users\n"
        "- POST /projects\n"
        "- POST /tasks\n"
        "- GET /tasks?project_id=\n\n"
        "## Data model\n"
        "- User: id, fields needed for creation\n"
        "- Project: id, user_id, fields needed for creation\n"
        "- Task: id, project_id, fields needed for creation\n\n"
        "## Edge cases\n"
        "- Missing project_id on task creation\n"
        "- GET /tasks with unknown project_id\n"
        "- Empty task list for a project\n\n"
        "## Security notes\n"
        "- Validate inputs with Pydantic\n"
        "- Avoid storing secrets in code\n\n"
        "## Performance notes\n"
        "- Use in-memory dicts keyed by id for O(1) lookups\n\n"
        "## Test plan\n"
        "- Create user, project, tasks; list tasks by project_id\n"
        "- Invalid project_id returns 400/404\n"
    )


def deterministic_executor_prompt(task: str, planning_doc: str) -> str:
    return (
        "You are the executor.\n"
        "Output ONLY the final Python code (no markdown fences, no prose).\n"
        "Constraints:\n"
        "- Single file FastAPI app\n"
        "- In-memory users/projects/tasks\n"
        "- Endpoints: POST /users, POST /projects, POST /tasks, GET /tasks?project_id=\n"
        "- Validate input with Pydantic\n"
        "- Handle edge cases with HTTPException\n"
        "- Include __main__ that runs uvicorn\n\n"
        "Planning doc:\n"
        f"{planning_doc}\n\n"
        "Task:\n"
        f"{task}\n"
    )
