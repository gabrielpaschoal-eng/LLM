from typing import Any, List, Optional, Type

import anyio
from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, ResultMessage, TextBlock, query
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel

from app.config import Settings


def _messages_to_prompt(messages: List[BaseMessage]) -> tuple[Optional[str], str]:
    system_parts = []
    turns = []
    for message in messages:
        if isinstance(message, SystemMessage):
            system_parts.append(str(message.content))
        elif isinstance(message, HumanMessage):
            turns.append(f"Usuário: {message.content}")
        elif isinstance(message, AIMessage):
            turns.append(f"Assistente: {message.content}")
        else:
            turns.append(str(message.content))
    system = "\n".join(system_parts) if system_parts else None
    return system, "\n\n".join(turns)


class ClaudeSDKChatModel(BaseChatModel):
    model: Optional[str] = None
    effort: Optional[str] = None

    @property
    def _llm_type(self) -> str:
        return "claude-agent-sdk"

    async def _ask(
        self, messages: List[BaseMessage], output_format: Optional[dict] = None
    ) -> Any:
        system, prompt = _messages_to_prompt(messages)
        options = ClaudeAgentOptions(
            model=self.model,
            effort=self.effort,
            system_prompt=system,
            allowed_tools=[],
            output_format=output_format,
        )
        text = ""
        structured = None
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text += block.text
            elif isinstance(message, ResultMessage):
                structured = message.structured_output
        if output_format is not None and structured is not None:
            return structured
        return text

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        text = anyio.run(self._ask, messages)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=text))])

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        text = await self._ask(messages)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=text))])

    def with_structured_output(self, schema: Type[BaseModel], **kwargs: Any) -> RunnableLambda:
        json_schema = schema.model_json_schema()

        def _run(input_value: Any) -> BaseModel:
            messages = input_value.to_messages() if hasattr(input_value, "to_messages") else [
                HumanMessage(content=str(input_value))
            ]
            result = anyio.run(
                self._ask,
                messages,
                {"type": "json_schema", "schema": json_schema},
            )
            return schema.model_validate(result)

        return RunnableLambda(_run)


def create_model(settings: Settings) -> ClaudeSDKChatModel:
    return ClaudeSDKChatModel(model=settings.model_name, effort=settings.effort)
