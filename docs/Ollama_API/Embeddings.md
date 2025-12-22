# Embeddings

Generate text embeddings for semantic search, retrieval, and RAG. Embeddings turn text into numeric vectors you can store in a vector database, search with cosine similarity, or use in RAG pipelines. The vector length depends on the model (typically 384–1024 dimensions).

## Recommended Models

- [embeddinggemma](https://ollama.com/library/embeddinggemma)
- [qwen3-embedding](https://ollama.com/library/qwen3-embedding)
- [all-minilm](https://ollama.com/library/all-minilm)

## Generate Embeddings

### Example (CLI):

```bash
ollama run embeddinggemma "Hello world"
```

You can also pipe text to generate embeddings:

```bash
echo "Hello world" | ollama run embeddinggemma
```

Output is a JSON array.

## Generate a Batch of Embeddings

Pass an array of strings to `input`.

### Example (cURL):

```bash
curl -X POST http://localhost:11434/api/embed \
  -H "Content-Type: application/json" \
  -d '{
    "model": "embeddinggemma",
    "input": [
      "First sentence",
      "Second sentence",
      "Third sentence"
    ]
  }'
```

## Tips

- Use cosine similarity for most semantic search use cases.
- Use the same embedding model for both indexing and querying.

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.ollama.com/llms.txt