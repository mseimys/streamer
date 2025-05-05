import json
import asyncio
from typing import AsyncIterator, Literal, Union, cast

from openai.types.beta.threads.runs import ToolCall, ToolCallDelta
from openai import AsyncOpenAI, AsyncAssistantEventHandler
from typing_extensions import override


class EventHandler(AsyncAssistantEventHandler):
    """Async event handler that provides an async iterator."""

    client: AsyncOpenAI
    queue: asyncio.Queue[str]
    done: asyncio.Event

    def __init__(self, client: AsyncOpenAI):
        super().__init__()
        self.client = client
        self.queue = asyncio.Queue()
        self.done = asyncio.Event()

    @override
    async def on_text_created(self, text) -> None:
        print("\nassistant > ", end="", flush=True)
        self.done.clear()

    @override
    async def on_text_delta(self, delta, snapshot) -> None:
        print(delta.value, end="", flush=True)
        if delta.value is not None and delta.value != "":
            self.queue.put_nowait(delta.value)

    @override
    async def on_tool_call_created(self, tool_call: ToolCall) -> None:
        """Callback that is fired when a tool call is created"""
        print(tool_call.__dict__)
        print(f"\non_tool_call_created > {tool_call.type}\n", flush=True)

    @override
    async def on_tool_call_delta(self, delta: ToolCallDelta, snapshot: ToolCall) -> None:
        """Callback that is fired when a tool call delta is encountered"""
        print(delta.__dict__)
        print("\non_tool_call_delta", flush=True)

    @override
    async def on_tool_call_done(self, tool_call: ToolCall) -> None:
        """Callback that is fired when a tool call request is ready to be executed"""
        print(tool_call.__dict__)
        function_name = tool_call.function.name  # analyze_json_string
        args = json.loads(tool_call.function.arguments)
        print(f"\nshould now call > {function_name} with {args}\n", flush=True)

        tools_output = [
            {
                "tool_call_id": tool_call.id,
                "output": f"abrakadabra({args})",
            }
        ]

        await self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tools_output,
        )
        ### DOES NOT RESUME..

    @override
    async def on_exception(self, exception: Exception):
        """Fired whenever an exception happens during streaming"""
        print(f"on_exception: {str(exception)}", flush=True)

    @override
    async def on_end(self) -> None:
        """Fires when stream ends or when exception is thrown"""
        print("\non_end!", flush=True)
        print("CURRENT RUN:", self.current_run.__dict__)

        self.done.set()

    async def aiter(self) -> AsyncIterator[str]:
        while not self.queue.empty() or not self.done.is_set():
            done, other = await asyncio.wait(
                [
                    asyncio.ensure_future(self.queue.get()),
                    asyncio.ensure_future(self.done.wait()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            if other:
                other.pop().cancel()

            token_or_done = cast(Union[str, Literal[True]], done.pop().result())

            if token_or_done is True:
                break

            yield token_or_done
