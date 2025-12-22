"""
Classes:
- ModelOptions: Options for model generation and inference, including sampling parameters, penalties, hardware settings, and context management.
- GenerateRequest: Request schema for text generation, supporting prompts, images, formatting, streaming, and advanced options.
- Logprob: Represents a token's log probability and related metadata.
- GenerateResponse: Response schema for text generation, including generated text, timing, and log probabilities.
- ToolCall: Represents a function/tool call in chat interactions.
- RoleEnum: Enum for chat message roles (system, assistant, user, tool).
- ChatMessage: Represents a message in a chat, including role, content, images, and tool calls.
- ToolDefinition: Definition of a tool/function available in chat.
- ChatRequest: Request schema for chat interactions, supporting tools, formatting, streaming, and options.
- ChatResponseMessage: Represents a single chat response message, including role, content, and tool calls.
- ChatResponse: Response schema for chat, including message, timing, and log probabilities.
- StreamChunk: Represents a chunk of streamed chat or generation output.
- StreamResponse: Response schema for streamed outputs, containing multiple chunks.
- EmbedRequest: Request schema for embedding generation, supporting batching and options.
- EmbedResponse: Response schema for embeddings, including timing and evaluation counts.
- ShowRequest: Request schema for retrieving model details.
- ShowResponse: Response schema for model details, including parameters, license, and capabilities.
- ModelSummary: Summary of a model for listing/tagging purposes.
- ListResponse: Response schema for listing available models.
- PsModel: Represents a running model instance and its metadata.
- PsResponse: Response schema for listing running models.
- CreateRequest: Request schema for creating a new model, supporting templates, licenses, and chat history.
- StatusResponse: Response schema for status updates, including progress.
- PullRequest: Request schema for pulling a model from a remote source.
- PushRequest: Request schema for pushing a model to a remote destination.
- DeleteRequest: Request schema for deleting a model.
- CopyRequest: Request schema for copying a model.
- VersionResponse: Response schema for API or model version information.
- ErrorResponse: Standard error response schema.
ollama_schemas.py

Pydantic models for all major Ollama API request and response schemas.
Covers: generate, chat, embed, show, tags, ps, create, pull, push, delete, copy, version, and error responses.
"""
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ModelOptions(BaseModel):
    """
    Options for model generation and inference.

    Attributes:
        seed (Optional[int]): Random seed for reproducibility.
        temperature (Optional[float]): Sampling temperature for randomness.
        top_k (Optional[int]): Number of top tokens to consider during sampling.
        top_p (Optional[float]): Cumulative probability threshold for nucleus sampling.
        min_p (Optional[float]): Minimum probability threshold for token selection.
        tfs_z (Optional[float]): Tail-free sampling parameter.
        typical_p (Optional[float]): Typical probability threshold for token selection.
        repeat_last_n (Optional[int]): Number of recent tokens to consider for repetition penalty.
        repeat_penalty (Optional[float]): Penalty for repeating tokens.
        presence_penalty (Optional[float]): Penalty for token presence in the context.
        frequency_penalty (Optional[float]): Penalty for token frequency in the context.
        mirostat (Optional[int]): Mirostat sampling mode.
        mirostat_tau (Optional[float]): Target entropy for Mirostat sampling.
        mirostat_eta (Optional[float]): Learning rate for Mirostat sampling.
        penalize_newline (Optional[bool]): Whether to penalize newline tokens.
        stop (Optional[Union[str, List[str]]]): Stop sequences for generation.
        numa (Optional[bool]): Whether to enable NUMA optimizations.
        num_ctx (Optional[int]): Number of context tokens.
        num_predict (Optional[int]): Number of tokens to predict.
        num_keep (Optional[int]): Number of tokens to keep in memory.
        num_batch (Optional[int]): Batch size for token generation.
        num_gpu (Optional[int]): Number of GPUs to use.
        main_gpu (Optional[int]): ID of the main GPU to use.
        low_vram (Optional[bool]): Whether to enable low VRAM mode.
        vocab_only (Optional[bool]): Whether to load only the vocabulary.
        use_mmap (Optional[bool]): Whether to use memory-mapped files.
        use_mlock (Optional[bool]): Whether to use memory locking.
        num_thread (Optional[int]): Number of threads to use.
    """
    seed: Optional[int] = Field(
        default=0, examples=[42], description="Random seed for reproducibility."
    )
    temperature: Optional[float] = Field(
        default=0.8, examples=[0.8], description="Sampling temperature for randomness."
    )
    top_k: Optional[int] = Field(
        default=20, examples=[20], description="Number of top tokens to consider during sampling."
    )
    top_p: Optional[float] = Field(
        default=0.9, examples=[0.9], description="Cumulative probability threshold for nucleus sampling."
    )
    min_p: Optional[float] = Field(
        default=0.0, examples=[0.0], description="Minimum probability threshold for token selection."
    )
    tfs_z: Optional[float] = Field(
        default=0.5, examples=[0.5], description="Tail-free sampling parameter."
    )
    typical_p: Optional[float] = Field(
        default=0.7, examples=[0.7], description="Typical probability threshold for token selection."
    )
    repeat_last_n: Optional[int] = Field(
        default=33, examples=[33], description="Number of recent tokens to consider for repetition penalty."
    )
    repeat_penalty: Optional[float] = Field(
        default=1.2, examples=[1.2], description="Penalty for repeating tokens."
    )
    presence_penalty: Optional[float] = Field(
        default=1.5, examples=[1.5], description="Penalty for token presence in the context."
    )
    frequency_penalty: Optional[float] = Field(
        default=1.0, examples=[1.0], description="Penalty for token frequency in the context."
    )
    mirostat: Optional[int] = Field(
        default=1, examples=[1], description="Mirostat sampling mode."
    )
    mirostat_tau: Optional[float] = Field(
        default=0.8, examples=[0.8], description="Target entropy for Mirostat sampling."
    )
    mirostat_eta: Optional[float] = Field(
        default=0.6, examples=[0.6], description="Learning rate for Mirostat sampling."
    )
    penalize_newline: Optional[bool] = Field(
        default=True, examples=[True], description="Whether to penalize newline tokens."
    )
    stop: Optional[Union[str, List[str]]] = Field(
        default=None, examples=["\n", "user:"], description="Stop sequences for generation."
    )
    numa: Optional[bool] = Field(
        default=False, examples=[False], description="Whether to enable NUMA optimizations."
    )
    num_ctx: Optional[int] = Field(
        default=1024, examples=[1024], description="Number of context tokens."
    )
    num_predict: Optional[int] = Field(
        default=100, examples=[100], description="Number of tokens to predict."
    )
    num_keep: Optional[int] = Field(
        default=5, examples=[5], description="Number of tokens to keep in memory."
    )
    num_batch: Optional[int] = Field(
        default=2, examples=[2], description="Batch size for token generation."
    )
    num_gpu: Optional[int] = Field(
        default=1, examples=[1], description="Number of GPUs to use."
    )
    main_gpu: Optional[int] = Field(
        default=0, examples=[0], description="ID of the main GPU to use."
    )
    low_vram: Optional[bool] = Field(
        default=False, examples=[False], description="Whether to enable low VRAM mode."
    )
    vocab_only: Optional[bool] = Field(
        default=False, examples=[False], description="Whether to load only the vocabulary."
    )
    use_mmap: Optional[bool] = Field(
        default=True, examples=[True], description="Whether to use memory-mapped files."
    )
    use_mlock: Optional[bool] = Field(
        default=False, examples=[False], description="Whether to use memory locking."
    )
    num_thread: Optional[int] = Field(
        default=8, examples=["8"], description="Number of threads to use."
    )

    class Config:
        extra = "forbid"

# --- Generate ---
class GenerateRequest(BaseModel):
    """
    Request schema for generating text using a language model.

    Attributes:
        model (str): The name or identifier of the model to use.
        prompt (Optional[str]): The input prompt to generate text from.
        suffix (Optional[str]): Optional text to append after the generated output.
        images (Optional[List[str]]): List of image data (as base64 strings or URLs) to provide as context.
        format (Optional[Union[str, Dict[str, Any]]]): Output format specification, either as a string or a dictionary.
        system (Optional[str]): System-level instructions or context for the model.
        stream (Optional[bool]): Whether to stream the output as it is generated. Defaults to True.
        think (Optional[Union[bool, str]]): Whether to enable "thinking" mode, or a string specifying the mode.
        raw (Optional[bool]): If True, returns raw model output without post-processing.
        keep_alive (Optional[Union[str, int]]): How long to keep the session alive, as a string or integer (e.g., seconds).
        options (Optional[ModelOptions]): Additional model-specific options.
        logprobs (Optional[bool]): Whether to include log probabilities for generated tokens.
        top_logprobs (Optional[int]): Number of top log probabilities to include for each token.
    """
    model: str
    prompt: Optional[str] = None
    suffix: Optional[str] = None
    images: Optional[List[str]] = None
    format: Optional[Union[str, Dict[str, Any]]] = None
    system: Optional[str] = None
    stream: Optional[bool] = True
    think: Optional[Union[bool, str]] = None
    raw: Optional[bool] = None
    keep_alive: Optional[Union[str, int]] = None
    options: Optional[ModelOptions] = None
    logprobs: Optional[bool] = None
    top_logprobs: Optional[int] = None

class Logprob(BaseModel):
    """
    Represents a token's log probability and related metadata.

    Attributes:
        token (str): The token text.
        logprob (float): The log probability of the token.
        bytes (Optional[List[int]]): Byte representation of the token.
        top_logprobs (Optional[List[Dict[str, Union[str, float, List[int]]]]]): Top log probabilities for the token.
    """
    token: str
    logprob: float
    bytes: Optional[List[int]] = None
    top_logprobs: Optional[List[Dict[str, Union[str, float, List[int]]]]] = None

class GenerateResponse(BaseModel):
    """
    Represents the response generated by a language model.

    Attributes:
        model (str): The name or identifier of the model used to generate the response.
        created_at (str): The timestamp indicating when the response was created.
        response (str): The generated response text.
        thinking (Optional[str]): Optional field containing intermediate thoughts or reasoning, if available.
        done (bool): Indicates whether the response generation is complete.
        done_reason (Optional[str]): The reason why the generation stopped (e.g., "stop", "unload").
        total_duration (Optional[int]): Total duration (in milliseconds) taken to generate the response.
        load_duration (Optional[int]): Duration (in milliseconds) taken to load the model.
        prompt_eval_count (Optional[int]): Number of tokens evaluated in the prompt.
        prompt_eval_duration (Optional[int]): Duration (in milliseconds) taken to evaluate the prompt.
        eval_count (Optional[int]): Number of tokens evaluated during generation.
        eval_duration (Optional[int]): Duration (in milliseconds) taken for token evaluation during generation.
        logprobs (Optional[List[Logprob]]): Optional list of log probability objects for generated tokens.
    """
    model: str
    created_at: str
    response: str
    thinking: Optional[str] = None
    done: bool
    done_reason: Optional[str] = None  # Added to handle reasons like "stop" or "unload"
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None
    logprobs: Optional[List[Logprob]] = None

# --- Chat ---
class ToolCall(BaseModel):
    """
    Represents a function or tool call in chat interactions.

    Attributes:
        function (Dict[str, Any]): The function or tool being called, represented as a dictionary.
    """
    function: Dict[str, Any]

# --- Role Enum ---
class RoleEnum(str, Enum):
    """
    Enum for chat message roles.

    Attributes:
        SYSTEM (str): Represents the system role.
        ASSISTANT (str): Represents the assistant role.
        USER (str): Represents the user role.
        TOOL (str): Represents the tool role.
    """
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"
    TOOL = "tool"

class ChatMessage(BaseModel):
    """
    Represents a message in a chat interaction.

    Attributes:
        role (RoleEnum): The role of the message sender (e.g., system, assistant, user, tool).
        content (str): The content of the message.
        images (Optional[List[str]]): Optional list of images associated with the message.
        tool_calls (Optional[List[ToolCall]]): Optional list of tool calls associated with the message.
        tool_name (Optional[str]): Optional name of the tool being used.
    """
    role: RoleEnum
    content: str
    images: Optional[List[str]] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_name: Optional[str] = None  # Added to handle tool call results

class ToolDefinition(BaseModel):
    """
    Definition of a tool or function available in chat interactions.

    Attributes:
        type (str): The type of the tool or function.
        function (Dict[str, Any]): The function definition, represented as a dictionary.
    """
    type: str
    function: Dict[str, Any]

class ChatRequest(BaseModel):
    """
    Request schema for chat interactions.

    Attributes:
        model (str): The name or identifier of the model to use.
        messages (List[ChatMessage]): List of messages in the chat interaction.
        tools (Optional[List[ToolDefinition]]): Optional list of tools available for the chat.
        format (Optional[Union[str, Dict[str, Any]]]): Output format specification, either as a string or a dictionary.
        options (Optional[ModelOptions]): Additional model-specific options.
        stream (Optional[bool]): Whether to stream the output as it is generated. Defaults to True.
        think (Optional[Union[bool, str]]): Whether to enable "thinking" mode, or a string specifying the mode.
        keep_alive (Optional[Union[str, int]]): How long to keep the session alive, as a string or integer (e.g., seconds).
        logprobs (Optional[bool]): Whether to include log probabilities for generated tokens.
        top_logprobs (Optional[int]): Number of top log probabilities to include for each token.
    """
    model: str
    messages: List[ChatMessage]
    tools: Optional[List[ToolDefinition]] = None
    format: Optional[Union[str, Dict[str, Any]]] = None
    options: Optional[ModelOptions] = None
    stream: Optional[bool] = True
    think: Optional[Union[bool, str]] = None
    keep_alive: Optional[Union[str, int]] = None
    logprobs: Optional[bool] = None
    top_logprobs: Optional[int] = None
    class Config:
        extra = "forbid"

class ChatResponseMessage(BaseModel):
    """
    Represents a single chat response message.

    Attributes:
        role (RoleEnum): The role of the message sender (e.g., system, assistant, user, tool).
        content (Optional[str]): The content of the message.
        thinking (Optional[str]): Optional field containing intermediate thoughts or reasoning, if available.
        tool_calls (Optional[List[ToolCall]]): Optional list of tool calls associated with the message.
        images (Optional[List[str]]): Optional list of images associated with the message.
    """
    role: RoleEnum
    content: Optional[str] = None  # Added to align with the streaming example
    thinking: Optional[str] = None  # Ensure this field is present
    tool_calls: Optional[List[ToolCall]] = None
    images: Optional[List[str]] = None

class ChatResponse(BaseModel):
    """
    Response schema for chat interactions.

    Attributes:
        model (str): The name or identifier of the model used to generate the response.
        created_at (str): The timestamp indicating when the response was created.
        message (ChatResponseMessage): The chat response message.
        done (bool): Indicates whether the chat interaction is complete.
        done_reason (Optional[str]): The reason why the chat interaction stopped (e.g., "stop", "unload").
        total_duration (Optional[int]): Total duration (in milliseconds) taken to generate the response.
        load_duration (Optional[int]): Duration (in milliseconds) taken to load the model.
        prompt_eval_count (Optional[int]): Number of tokens evaluated in the prompt.
        prompt_eval_duration (Optional[int]): Duration (in milliseconds) taken to evaluate the prompt.
        eval_count (Optional[int]): Number of tokens evaluated during generation.
        eval_duration (Optional[int]): Duration (in milliseconds) taken for token evaluation during generation.
        logprobs (Optional[List[Logprob]]): Optional list of log probability objects for generated tokens.
    """
    model: str
    created_at: str
    message: ChatResponseMessage
    done: bool
    done_reason: Optional[str] = None  # Added to handle reasons like "stop" or "unload"
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None
    logprobs: Optional[List[Logprob]] = None

class StreamChunk(BaseModel):
    """
    Represents a chunk of streamed chat or generation output.

    Attributes:
        thinking (Optional[str]): Represents partial reasoning traces.
        content (Optional[str]): Represents partial content.
        tool_calls (Optional[List[ToolCall]]): Represents tool calls in the chunk.
    """
    thinking: Optional[str] = None  # Represents partial reasoning traces
    content: Optional[str] = None  # Represents partial content
    tool_calls: Optional[List[ToolCall]] = None  # Represents tool calls in the chunk

class StreamResponse(BaseModel):
    """
    Response schema for streamed outputs.

    Attributes:
        chunks (List[StreamChunk]): List of streamed chunks.
    """
    chunks: List[StreamChunk]  # List of streamed chunks

# --- Embed ---
class EmbedRequest(BaseModel):
    """
    Request schema for embedding generation.

    Attributes:
        model (str): The name or identifier of the model to use.
        input (Union[str, List[str]]): The input text or list of texts to generate embeddings for.
        truncate (Optional[bool]): Whether to truncate the input text. Defaults to True.
        dimensions (Optional[int]): The number of dimensions for the embeddings.
        keep_alive (Optional[str]): How long to keep the session alive, as a string.
        options (Optional[ModelOptions]): Additional model-specific options.
    """
    model: str
    input: Union[str, List[str]]
    truncate: Optional[bool] = True
    dimensions: Optional[int] = None
    keep_alive: Optional[str] = None
    options: Optional[ModelOptions] = None

class EmbedResponse(BaseModel):
    """
    Response schema for embeddings.

    Attributes:
        model (str): The name or identifier of the model used to generate the embeddings.
        embeddings (List[List[float]]): List of embeddings generated for the input texts.
        total_duration (Optional[int]): Total duration (in milliseconds) taken to generate the embeddings.
        load_duration (Optional[int]): Duration (in milliseconds) taken to load the model.
        prompt_eval_count (Optional[int]): Number of tokens evaluated in the prompt.
    """
    model: str
    embeddings: List[List[float]]
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None

# --- Show ---
class ShowRequest(BaseModel):
    """
    Request schema for retrieving model details.

    Attributes:
        model (str): The name or identifier of the model to retrieve details for.
        verbose (Optional[bool]): Whether to include verbose details. Defaults to None.
    """
    model: str
    verbose: Optional[bool] = None

class ShowResponse(BaseModel):
    """
    Response schema for model details.

    Attributes:
        parameters (Optional[str]): Model parameters.
        license (Optional[str]): Model license information.
        modified_at (Optional[str]): Timestamp indicating when the model was last modified.
        details (Optional[Dict[str, Any]]): Additional details about the model.
        template (Optional[str]): Model template information.
        capabilities (Optional[List[str]]): List of model capabilities.
        model_info (Optional[Dict[str, Any]]): Additional model information.
    """
    parameters: Optional[str] = None
    license: Optional[str] = None
    modified_at: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    template: Optional[str] = None
    capabilities: Optional[List[str]] = None
    model_info: Optional[Dict[str, Any]] = None

# --- Tags (List Models) ---
class ModelSummary(BaseModel):
    """
    Summary of a model for listing or tagging purposes.

    Attributes:
        name (str): The name of the model.
        modified_at (Optional[str]): Timestamp indicating when the model was last modified.
        size (Optional[int]): The size of the model.
        digest (Optional[str]): The digest of the model.
        details (Optional[Dict[str, Any]]): Additional details about the model.
    """
    name: str
    modified_at: Optional[str] = None
    size: Optional[int] = None
    digest: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class ListResponse(BaseModel):
    """
    Response schema for listing available models.

    Attributes:
        models (List[ModelSummary]): List of model summaries.
    """
    models: List[ModelSummary]

# --- PS (List Running Models) ---
class PsModel(BaseModel):
    """
    Represents a running model instance and its metadata.

    Attributes:
        model (str): The name or identifier of the running model.
        size (Optional[int]): The size of the model.
        digest (Optional[str]): The digest of the model.
        details (Optional[Dict[str, Any]]): Additional details about the model.
        expires_at (Optional[str]): Timestamp indicating when the model instance expires.
        size_vram (Optional[int]): The size of the model in VRAM.
        context_length (Optional[int]): The context length of the model.
    """
    model: str
    size: Optional[int] = None
    digest: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    expires_at: Optional[str] = None
    size_vram: Optional[int] = None
    context_length: Optional[int] = None

class PsResponse(BaseModel):
    """
    Response schema for listing running models.

    Attributes:
        models (List[PsModel]): List of running model instances.
    """
    models: List[PsModel]

# --- Create ---
class CreateRequest(BaseModel):
    """
    Request schema for creating a new model.

    Attributes:
        model (str): The name or identifier of the model to create.
        from_ (Optional[str]): The source model to create from.
        template (Optional[str]): The template to use for creating the model.
        license (Optional[Union[str, List[str]]]): The license information for the model.
        system (Optional[str]): System-level instructions or context for the model.
        parameters (Optional[Dict[str, Any]]): Additional parameters for creating the model.
        messages (Optional[List[ChatMessage]]): List of messages to include in the model creation process.
        quantize (Optional[str]): Quantization settings for the model.
        stream (Optional[bool]): Whether to stream the output as it is generated. Defaults to True.
    """
    model: str
    from_: Optional[str] = Field(None, alias="from")
    template: Optional[str] = None
    license: Optional[Union[str, List[str]]] = None
    system: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    messages: Optional[List[ChatMessage]] = None
    quantize: Optional[str] = None
    stream: Optional[bool] = True

class StatusResponse(BaseModel):
    """
    Response schema for status updates.

    Attributes:
        status (str): The status of the operation.
        digest (Optional[str]): The digest of the operation.
        total (Optional[int]): The total number of items in the operation.
        completed (Optional[int]): The number of completed items in the operation.
    """
    status: str
    digest: Optional[str] = None
    total: Optional[int] = None
    completed: Optional[int] = None

# --- Pull/Push ---
class PullRequest(BaseModel):
    """
    Request schema for pulling a model from a remote source.

    Attributes:
        model (str): The name or identifier of the model to pull.
        insecure (Optional[bool]): Whether to allow insecure connections. Defaults to None.
        stream (Optional[bool]): Whether to stream the output as it is generated. Defaults to True.
    """
    model: str
    insecure: Optional[bool] = None
    stream: Optional[bool] = True

class PushRequest(BaseModel):
    """
    Request schema for pushing a model to a remote destination.

    Attributes:
        model (str): The name or identifier of the model to push.
        insecure (Optional[bool]): Whether to allow insecure connections. Defaults to None.
        stream (Optional[bool]): Whether to stream the output as it is generated. Defaults to True.
    """
    model: str
    insecure: Optional[bool] = None
    stream: Optional[bool] = True

# --- Delete ---
class DeleteRequest(BaseModel):
    """
    Request schema for deleting a model.

    Attributes:
        model (str): The name or identifier of the model to delete.
    """
    model: str

# --- Copy ---
class CopyRequest(BaseModel):
    """
    Request schema for copying a model.

    Attributes:
        source (str): The source model to copy from.
        destination (str): The destination model to copy to.
    """
    source: str
    destination: str

# --- Version ---
class VersionResponse(BaseModel):
    """
    Response schema for API or model version information.

    Attributes:
        version (str): The version of the API or model.
    """
    version: str

# --- Error ---
class ErrorResponse(BaseModel):
    """
    Standard error response schema.

    Attributes:
        error (str): The error message.
    """
    error: str


