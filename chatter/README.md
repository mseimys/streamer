# OpenAI Chatter Bot

Copy paste of implementation from https://b-reid.medium.com/from-setup-to-streaming-using-fastapi-with-openais-assistant-api-6cf7b024e45e

Start dev server:

```
uv run poe dev
```

Create new thread:

```
curl -X POST http://localhost:5000/api/assistant/threads -H "Content-Type: application/json"

{"data":{"id":"thread_uk6X6xzya882SUaRi0l9eOmqZ","created_at":1745614861,"metadata":{},"object":"thread","tool_resources":{"code_interpreter":null,"file_search":null}}}
```

Initiate a Chat Session Using SSE:

```
curl -N -X POST \
-H "Accept: text/event-stream" -H "Content-Type: application/json" \
-d '{"text": "Hello! Please introduce yourself", "thread_id": "thread_uk6X6xzya882SUaRi0l9eOmqZ" }' \
http://localhost:5000/api/assistant/chat
```
