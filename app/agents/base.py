# app/agents/base.py
from __future__ import annotations

import json
from typing import Generic, Optional, Type, TypeVar

from crewai import Agent, LLM
from openai import OpenAI
from pydantic import BaseModel

from app.config import settings

T = TypeVar("T", bound=BaseModel)


def _cfg(name: str, default):
    return getattr(settings, name, getattr(settings, name.upper(), default))


class StructuredOutputRunner(Generic[T]):
    def __init__(self, model_name: Optional[str] = None):
        self.client = OpenAI(api_key=_cfg("openai_api_key", None))
        self.model_name = model_name or _cfg("openai_model", "gpt-4o-mini")

    def run(
        self,
        system_prompt: str,
        user_payload: dict,
        output_model: Type[T],
    ) -> T:
        response = self.client.responses.parse(
            model=self.model_name,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, default=str)},
            ],
            text_format=output_model,
        )
        return response.output_parsed


def build_crewai_agent(
    *,
    role: str,
    goal: str,
    backstory: str,
    tools: Optional[list] = None,
) -> Agent:
    llm = LLM(
        model=_cfg("crewai_model", _cfg("openai_model", "gpt-4o-mini")),
        temperature=0,
    )

    return Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        tools=tools or [],
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=5,
    )