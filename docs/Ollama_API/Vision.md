# Vision

Vision models accept images alongside text so the model can describe, classify, and answer questions about what it sees.

## Quick Start

```bash
ollama run gemma3 ./image.png whats in this image?
```

## Usage with Ollama’s API

Provide an `images` array. SDKs accept file paths, URLs, or raw bytes while the REST API expects base64-encoded image data.

### Example (Python):

```python
from ollama import chat

path = input('Please enter the path to the image: ')

response = chat(
  model='gemma3',
  messages=[
    {
      'role': 'user',
      'content': 'What is in this image? Be concise.',
      'images': [path],
    }
  ],
)

print(response.message.content)
```

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.ollama.com/llms.txt