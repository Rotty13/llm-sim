# Streaming

Streaming allows you to render text as it is produced by the model.

Streaming is enabled by default through the REST API, but disabled by default in the SDKs.

To enable streaming in the SDKs, set the `stream` parameter to `True`.

## Key streaming concepts

1. Chatting: Stream partial assistant messages. Each chunk includes the `content` so you can render messages as they arrive.
2. Thinking: Thinking-capable models emit a `thinking` field alongside regular content in each chunk. Detect this field in streaming chunks to show or hide reasoning traces before the final answer arrives.
3. Tool calling: Watch for streamed `tool_calls` in each chunk, execute the requested tool, and append tool outputs back into the conversation.

## Handling streamed chunks

It is necessary to accumulate the partial fields in order to maintain the history of the conversation. This is particularly important for tool calling where the thinking, tool call from the model, and the executed tool result must be passed back to the model in the next request.

### Example (Python):

```python
from ollama import chat

stream = chat(
  model='qwen3',
  messages=[{'role': 'user', 'content': 'What is 17 × 23?'}],
  stream=True,
)

in_thinking = False
content = ''
thinking = ''
for chunk in stream:
  if chunk.message.thinking:
    if not in_thinking:
      in_thinking = True
      print('Thinking:\n', end='', flush=True)
    print(chunk.message.thinking, end='', flush=True)
    # accumulate the partial thinking 
    thinking += chunk.message.thinking
  elif chunk.message.content:
    if in_thinking:
      in_thinking = False
      print('\n\nAnswer:\n', end='', flush=True)
    print(chunk.message.content, end='', flush=True)
    # accumulate the partial content
    content += chunk.message.content

  # append the accumulated fields to the messages for the next request
  new_messages = [{ 'role': 'assistant', 'thinking': thinking, 'content': content }]
```

### Example (JavaScript):

```javascript
import ollama from 'ollama';

async function main() {
  const stream = await ollama.chat({
    model: 'qwen3',
    messages: [{ role: 'user', content: 'What is 17 × 23?' }],
    stream: true,
  });

  let inThinking = false;
  let content = '';
  let thinking = '';

  for await (const chunk of stream) {
    if (chunk.message.thinking) {
      if (!inThinking) {
        inThinking = true;
        process.stdout.write('Thinking:\n');
      }
      process.stdout.write(chunk.message.thinking);
      // accumulate the partial thinking
      thinking += chunk.message.thinking;
    } else if (chunk.message.content) {
      if (inThinking) {
        inThinking = false;
        process.stdout.write('\n\nAnswer:\n');
      }
      process.stdout.write(chunk.message.content);
      // accumulate the partial content
      content += chunk.message.content;
    }
  }

  // append the accumulated fields to the messages for the next request
  new_messages = [{ role: 'assistant', thinking: thinking, content: content }];
}

main().catch(console.error);
```

---

## Streaming Response Format

Certain API endpoints stream responses by default, such as `/api/generate`. These responses are provided in the newline-delimited JSON format (i.e., the `application/x-ndjson` content type). For example:

```json
{"model":"gemma3","created_at":"2025-10-26T17:15:24.097767Z","response":"That","done":false}
{"model":"gemma3","created_at":"2025-10-26T17:15:24.109172Z","response":"'","done":false}
{"model":"gemma3","created_at":"2025-10-26T17:15:24.121485Z","response":"s","done":false}
{"model":"gemma3","created_at":"2025-10-26T17:15:24.132802Z","response":" a","done":false}
{"model":"gemma3","created_at":"2025-10-26T17:15:24.143931Z","response":" fantastic","done":false}
{"model":"gemma3","created_at":"2025-10-26T17:15:24.155176Z","response":" question","done":false}
{"model":"gemma3","created_at":"2025-10-26T17:15:24.166576Z","response":"!","done":true, "done_reason": "stop"}
```

### Disabling Streaming

Streaming can be disabled by providing `{"stream": false}` in the request body for any endpoint that supports streaming. This will cause responses to be returned in the `application/json` format instead:

```json
{"model":"gemma3","created_at":"2025-10-26T17:15:24.166576Z","response":"That's a fantastic question!","done":true}
```

### When to Use Streaming vs Non-Streaming

**Streaming (default):**
  - Real-time response generation
  - Lower perceived latency
  - Better for long generations

**Non-streaming:**
  - Simpler to process
  - Better for short responses or structured outputs
  - Easier to handle in some applications