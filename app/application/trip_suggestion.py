from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import Runnable, RunnablePassthrough

from app.domain.travel import Destination, Restaurants
from app.infrastructure.ai.claude_chat_model import ClaudeSDKChatModel

_destination_parser = JsonOutputParser(pydantic_object=Destination)
_restaurants_parser = JsonOutputParser(pydantic_object=Restaurants)

_city_prompt = PromptTemplate(
    template="""
    Sugira uma cidade dado o meu interesse por {interest}.
    {output_format}
    """,
    input_variables=["interest"],
    partial_variables={"output_format": _destination_parser.get_format_instructions()},
)

_restaurants_prompt = PromptTemplate(
    template="""
    Sugira restaurantes pouplares entre locais em {city}
    {output_format}
    """,
    partial_variables={"output_format": _restaurants_parser.get_format_instructions()},
)

_cultural_prompt = PromptTemplate(
    template="Sugira atividades e locais culturais em {city}"
)


def create_trip_suggestion_chain(model: ClaudeSDKChatModel) -> Runnable:
    city_chain = _city_prompt | model | _destination_parser
    restaurants_chain = (
        (lambda x: {"city": x["destination"]["city"]}) | _restaurants_prompt | model | _restaurants_parser
    )
    cultural_chain = (
        (lambda x: {"city": x["destination"]["city"]}) | _cultural_prompt | model | StrOutputParser()
    )
    return (
        RunnablePassthrough.assign(destination=city_chain)
        | RunnablePassthrough.assign(restaurants=restaurants_chain)
        | RunnablePassthrough.assign(cultural_activities=cultural_chain)
    )
