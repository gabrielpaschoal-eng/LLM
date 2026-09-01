from typing import Any, List, Optional, Type

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel


def _reply_for(messages: List[BaseMessage]) -> str:
    text = "\n".join(str(message.content) for message in messages)
    if "Sugira uma cidade" in text:
        return '{"city": "Florianópolis", "reason": "praias e cultura açoriana"}'
    if "Sugira restaurantes" in text:
        return '{"city": "Florianópolis", "restaurants": "Ostradamus, Box 32"}'
    if "atividades e locais culturais" in text:
        return "Museu Victor Meirelles, Centro Histórico"
    if "Sra Praia" in text:
        return "Sra Praia: vá para Porto de Galinhas."
    if "Sr Montanha" in text:
        return "Sr Montanha: vá para a Serra do Rio do Rastro."
    if "Sr. Passeios" in text:
        return "Sr. Passeios: recomendo Salvador."
    if "Responda usando exclusivamente o conteúdo fornecido" in text:
        return "Resposta baseada no contexto fornecido."
    return "resposta padrão de teste"


class FakeChatModel(BaseChatModel):
    @property
    def _llm_type(self) -> str:
        return "fake-chat-model"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=_reply_for(messages)))])

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        return self._generate(messages, stop, run_manager, **kwargs)

    def with_structured_output(self, schema: Type[BaseModel], **kwargs: Any) -> RunnableLambda:
        def _route(input_value: Any) -> BaseModel:
            messages = input_value.to_messages() if hasattr(input_value, "to_messages") else []
            human_text = " ".join(
                str(message.content) for message in messages if isinstance(message, HumanMessage)
            ).lower()
            destination = "montanha" if "montanha" in human_text else "praia"
            return schema.model_validate({"destination": destination})

        return RunnableLambda(_route)


class _FakeDocument:
    def __init__(self, page_content: str) -> None:
        self.page_content = page_content


class FakeRetriever:
    async def ainvoke(self, question: str) -> List[_FakeDocument]:
        return [_FakeDocument("Trecho de teste do PDF de seguro.")]

    def invoke(self, question: str) -> List[_FakeDocument]:
        return [_FakeDocument("Trecho de teste do PDF de seguro.")]
