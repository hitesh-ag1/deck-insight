from typing import Any
from uuid import UUID, uuid4
from langchain_core.runnables import RunnableConfig
import fitz
from PIL import Image
import io
import base64
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.messages import (
    ChatMessage as LangchainChatMessage,
)
from langgraph.types import Command
from core.schema import ChatMessage, UserInput
from fastapi import HTTPException
from langgraph.pregel import Pregel

async def handle_complete(user_input: list) -> tuple[dict[str, Any], UUID]:
    run_id = uuid4()
    thread_id = str(uuid4())

    configurable = {"thread_id": thread_id}

    config = RunnableConfig(
        configurable=configurable,
        run_id=run_id,
    )

    initial_state = {
        "slides": user_input,
        "summary": None,
        "scorecard": None,
        "slide_content": None,
        "market_analysis": None,
        "sector": None,
        "market_size": None,
        "competitors": None,
        "github_url": None,
        "github_details": None,
        "is_tech_company": False,
        "error": None
    }

    kwargs = {
        "input": initial_state,
        "config": config,
    }

    return kwargs, run_id


async def handle_input_slides(user_input: list) -> tuple[dict[str, Any], UUID]:
    run_id = uuid4()
    thread_id = str(uuid4())

    configurable = {"thread_id": thread_id}

    config = RunnableConfig(
        configurable=configurable,
        run_id=run_id,
    )

    initial_state = {
        "slides": user_input,
        "current_index": 0,
        "scorecard": None
    }

    kwargs = {
        "input": initial_state,
        "config": config,
    }

    return kwargs, run_id

async def handle_qa_input(user_input: UserInput, agent: Pregel) -> tuple[dict[str, Any], UUID]:
    """
    Parse user input and handle any required interrupt resumption.
    Returns kwargs for agent invocation and the run_id.
    """
    run_id = uuid4()
    thread_id = user_input.thread_id or str(uuid4())

    configurable = {"thread_id": thread_id, "model": user_input.model}

    if user_input.agent_config:
        if overlap := configurable.keys() & user_input.agent_config.keys():
            raise HTTPException(
                status_code=422,
                detail=f"agent_config contains reserved keys: {overlap}",
            )
        configurable.update(user_input.agent_config)

    config = RunnableConfig(
        configurable=configurable,
        run_id=run_id,
    )

    # Check for interrupts that need to be resumed
    state = await agent.aget_state(config=config)
    interrupted_tasks = [
        task for task in state.tasks if hasattr(task, "interrupts") and task.interrupts
    ]

    input: Command | dict[str, Any]
    if interrupted_tasks:
        # assume user input is response to resume agent execution from interrupt
        input = Command(resume=user_input.message)
    else:
        input = {"messages": [HumanMessage(content=user_input.message)]}

    kwargs = {
        "input": input,
        "config": config,
    }

    return kwargs, run_id


async def handle_market_size(user_input: dict) -> tuple[dict[str, Any], UUID]:
    run_id = uuid4()
    thread_id = str(uuid4())

    configurable = {"thread_id": thread_id}

    config = RunnableConfig(
        configurable=configurable,
        run_id=run_id,
    )

    initial_state = {
        "input_overview": user_input,
    }

    kwargs = {
        "input": initial_state,
        "config": config,
    }

    return kwargs, run_id

async def handle_github_link(link: str) -> tuple[dict[str, Any], UUID]:
    run_id = uuid4()
    thread_id = str(uuid4())

    configurable = {"thread_id": thread_id}

    config = RunnableConfig(
        configurable=configurable,
        run_id=run_id,
    )

    initial_state = {
        "link": link,
    }

    kwargs = {
        "input": initial_state,
        "config": config,
    }

    return kwargs, run_id


def convert_pdf_to_images(pdf_bytes):
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        images.append(byte_arr)

    pdf_document.close()
    return images

def getbase64(image):
    return "data:image/jpeg;base64," + base64.b64encode(image.getvalue()).decode("utf-8")


def convert_message_content_to_string(content: str | list[str | dict]) -> str:
    if isinstance(content, str):
        return content
    text: list[str] = []
    for content_item in content:
        if isinstance(content_item, str):
            text.append(content_item)
            continue
        if content_item["type"] == "text":
            text.append(content_item["text"])
    return "".join(text)


def langchain_to_chat_message(message: BaseMessage) -> ChatMessage:
    """Create a ChatMessage from a LangChain message."""
    match message:
        case HumanMessage():
            human_message = ChatMessage(
                type="human",
                content=convert_message_content_to_string(message.content),
            )
            return human_message
        case AIMessage():
            ai_message = ChatMessage(
                type="ai",
                content=convert_message_content_to_string(message.content),
            )
            if message.tool_calls:
                ai_message.tool_calls = message.tool_calls
            if message.response_metadata:
                ai_message.response_metadata = message.response_metadata
            return ai_message
        case ToolMessage():
            tool_message = ChatMessage(
                type="tool",
                content=convert_message_content_to_string(message.content),
                tool_call_id=message.tool_call_id,
            )
            return tool_message
        case LangchainChatMessage():
            if message.role == "custom":
                custom_message = ChatMessage(
                    type="custom",
                    content="",
                    custom_data=message.content[0],
                )
                return custom_message
            else:
                raise ValueError(f"Unsupported chat message role: {message.role}")
        case _:
            raise ValueError(f"Unsupported message type: {message.__class__.__name__}")
