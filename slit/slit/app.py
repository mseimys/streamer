import time
from datetime import datetime
from dataclasses import dataclass

import extra_streamlit_components as stx
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

print("Executing app.py")

USER_INPUT = "user_input"
LAST_CHAT = "last_chat"


@dataclass
class Message:
    role: str
    text: str
    time: datetime


# @st.cache_resource
def get_cookie_manager():
    return stx.CookieManager()


cookie_manager = get_cookie_manager()


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
    timestamp = datetime.now()
    message = Message(role="user", text=text, time=timestamp)
    st.session_state["messages"].append(message)
    render_message(messages, message)
    response = async_task(status)
    st.session_state["messages"].append(response)
    cookie_manager.set(LAST_CHAT, timestamp.isoformat())


def initialize_state():
    print("initialize_state")
    if "messages" not in st.session_state:
        print("set messages to empty array")
        st.session_state["messages"] = []
    if "status" not in st.session_state:
        st.session_state["status"] = ""

    cookies = st.context.cookies
    print("Cookies:", cookies.to_dict())
    last_chat_cookie = cookie_manager.get(LAST_CHAT)
    if LAST_CHAT not in st.session_state:
        print("No last chat in state, will set it to", last_chat_cookie)
    st.session_state[LAST_CHAT] = last_chat_cookie


def render():
    initialize_state()

    print("app.py:render")
    st.title("Hello Streamlit!")
    if st.session_state[LAST_CHAT]:
        st.write("Last chat: ", st.session_state[LAST_CHAT])
    # st.write(st.context.cookies)
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
