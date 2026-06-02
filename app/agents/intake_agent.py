from crewai import Agent

from app.config import get_settings

settings = get_settings()


def build_intake_agent() -> Agent:
    return Agent(
        role="Trade Break Intake Analyst",
        goal=(
            "Classify incoming trade breaks and settlement exceptions, "
            "extract key entities, and identify missing fields."
        ),
        backstory=(
            "You are an operations analyst in capital markets exception handling. "
            "You are careful, concise, and schema-driven."
        ),
        verbose=True,
        allow_delegation=False,
    )