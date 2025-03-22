from dataclasses import dataclass

from datetime import datetime
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
import time

print("Executing app.py")

USER_INPUT = "user_input"


@dataclass
class Message:
    role: str
    text: str
    time: datetime


def handle_click(container):
    print("app.py:handle_click")
    container.write("Button was clicked!")


def async_task(status: DeltaGenerator):
    with status.status("Running..."):
        time.sleep(2)
        st.write("Doing 1...")
        time.sleep(3)
        st.write("Doing 2...")
        time.sleep(2)

    status.empty()  # optional
    return Message(role="assistant", text="Async task response", time=datetime.now())


def render_message(messages: DeltaGenerator, message: Message):
    with messages.chat_message(message.role):
        st.markdown(f"**{message.time.strftime('%H:%M:%S')}** {message.text}")


def handle_submit(messages: DeltaGenerator, status: DeltaGenerator):
    print("app.py:handle_submit")
    text = st.session_state[USER_INPUT]
    message = Message(role="user", text=text, time=datetime.now())
    st.session_state["messages"].append(message)
    render_message(messages, message)
    response = async_task(status)
    st.session_state["messages"].append(response)


def initialize_state():
    print("initialize_state")
    if "messages" not in st.session_state:
        print("set messages to empty array")
        st.session_state["messages"] = []
    if "status" not in st.session_state:
        st.session_state["status"] = ""


def render():
    initialize_state()

    print("app.py:render")
    st.title("Hello Streamlit!")
    st.write("Message count: ", len(st.session_state["messages"]))
    messages = st.container()
    status = st.empty()

    st.chat_input(
        "Type a message",
        key=USER_INPUT,
        on_submit=lambda: handle_submit(messages, status),
    )

    for m in st.session_state["messages"]:
        render_message(messages, m)

    st.write("This is the bottom of the chat.")
    print("app.py:render: end")


render()
