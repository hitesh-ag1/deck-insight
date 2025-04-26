from langchain_elasticsearch import ElasticsearchStore
from core.settings import settings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langgraph.graph import MessagesState, StateGraph
from langgraph.graph import END
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.memory import MemorySaver

from agents.chatbot_qa.nodes import (
    query_or_respond,
    generate,
    tools,
)

embeddings = OpenAIEmbeddings(model=settings.EMBEDDINGS_MODEL)
vector_store = ElasticsearchStore(
            es_url=settings.ELASTIC_SEARCH_URL,
            index_name="pitch-deck-ai",
            embedding=embeddings,
            es_api_key=settings.ELASTIC_SEARCH_API,
        )
llm = ChatOpenAI(model=settings.TEXT_MODEL, temperature=0)

graph_builder = StateGraph(MessagesState)
graph_builder.add_node(query_or_respond)
graph_builder.add_node(tools)
graph_builder.add_node(generate)

graph_builder.set_entry_point("query_or_respond")
graph_builder.add_conditional_edges(
    "query_or_respond",
    tools_condition,
    {END: END, "tools": "tools"},
)
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", END)

qa_agent = graph_builder.compile(checkpointer=MemorySaver())
