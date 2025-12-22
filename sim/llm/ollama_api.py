"""
ollama_api.py

Implements a Python class for all major Ollama API endpoints.
See: https://docs.ollama.com/api/introduction and https://github.com/ollama/ollama/blob/main/docs/api.md

Endpoints covered:
- /api/generate (POST)
- /api/chat (POST)
- /api/create (POST)
- /api/show (POST)
- /api/tags (GET)
- /api/copy (POST)
- /api/delete (DELETE)
- /api/pull (POST)
- /api/push (POST)
- /api/embed (POST)
- /api/ps (GET)
- /api/version (GET)

All endpoints are implemented as methods on OllamaAPI.
"""

from ast import ClassDef
from binascii import Incomplete
from calendar import c
from collections import namedtuple
from configparser import NoSectionError
from dataclasses import Field
from email import iterators, message
from itertools import accumulate
import json
from logging import PlaceHolder
from mmap import mmap
from numbers import Number
from operator import le
from pyexpat.errors import messages
import re
from tkinter import N
from types import new_class
from urllib.parse import parse_qsl
from numpy import number
from pydantic.fields import FieldInfo
import requests
from typing import Any, ClassVar, Dict, Generator, Iterable, Iterator, List, Mapping, Optional, Union
from ollama_schemas import (
    ChatMessage, ChatResponseMessage, GenerateRequest, GenerateResponse, ChatRequest, ChatResponse, EmbedRequest, EmbedResponse, ModelOptions, RoleEnum,
    ShowRequest, ShowResponse, ListResponse, PsResponse, CreateRequest, StatusResponse,
    PullRequest, PushRequest, DeleteRequest, CopyRequest, VersionResponse, ErrorResponse
)


import time

from sim.utils.schema_validation import ValidationError



class OllamaAPI:
    def __init__(self, base_url: str = "http://localhost:11434/api"):
        self.base_url = base_url.rstrip("/")

    def _request_with_retry(self, method, url, stream=False, **kwargs):
        retries = 3
        backoff = 1
        for attempt in range(retries):
            try:
                if method == "post":
                    return requests.post(url, stream=stream, **kwargs)
                elif method == "get":
                    return requests.get(url, stream=stream, **kwargs)
                elif method == "delete":
                    return requests.delete(url, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
            except Exception as e:
                if isinstance(e, requests.RequestException):
                    if attempt < retries - 1:
                        time.sleep(backoff)
                        backoff *= 2
                    else:
                        raise e
                else:
                    raise e
                
        raise requests.exceptions.ConnectionError()
    
    
    def generate(self, req: Union[GenerateRequest, Dict[str, Any]]) -> Union[GenerateResponse, ErrorResponse, Iterator[GenerateResponse]]:
        """POST /api/generate: Generate a completion.

        This endpoint allows you to generate text completions based on a given prompt.
        For more information, see the "Structured Outputs" documentation in the Ollama API.
        Relevant Documentation: docs/Ollama_API/Structured_Outputs.md
        """
        data = req if isinstance(req, dict) else req.model_dump(by_alias=True)
        streaming = data.get("stream", False)
        try:
            resp = self._request_with_retry("post", f"{self.base_url}/generate", json=data, stream=streaming)
            contentType=resp.headers.get("Content-Type", "")
            if streaming:
                assert re.match(r"application\/x-ndjson(;.*)?", contentType)
                return map(GenerateResponse.model_validate_json, resp.iter_lines(decode_unicode=True))
            else:
                assert re.match(r"application\/json(;.*)?", contentType)
                return GenerateResponse(**resp.json())
        except Exception as e:
            return ErrorResponse(error=str(e))



    def chat(self, req: Union[ChatRequest, Dict[str, Any]]) -> Union[ChatResponse, ErrorResponse, Iterator[ChatResponse]]:
        """POST /api/chat: Generate a chat completion.

        This endpoint supports multi-turn conversations and can include streaming responses.
        For more details, refer to the "Streaming" and "Thinking" sections in the Ollama API documentation.
        Relevant Documentation: docs/Ollama_API/Streaming.md, docs/Ollama_API/Thinking.md
        """
        data = req if isinstance(req, dict) else req.model_dump(by_alias=True)
        streaming = data.get("stream", False)
        try:
            resp = self._request_with_retry("post", f"{self.base_url}/chat", json=data, stream=streaming)
            contentType=resp.headers.get("Content-Type", "")
            if streaming:
                #application/x-ndjson
                assert re.match(r"application\/x-ndjson(;.*)?", contentType)
                return map(ChatResponse.model_validate_json, resp.iter_lines(decode_unicode=True))
            else:
                #application/json
                assert re.match(r"application\/json(;.*)?", contentType)
                return ChatResponse(**resp.json())
        
        except Exception as e:
            return ErrorResponse(error=str(e))

    def create(self, req: Union[CreateRequest, Dict[str, Any]]) -> Union[StatusResponse, ErrorResponse]:
        """POST /api/create: Create a model.

        This endpoint is used to create a new model in the Ollama system.
        Refer to the "Tool Calling" section for examples of creating and using tools.
        Relevant Documentation: docs/Ollama_API/Tool_Calling.md
        """
        data = req if isinstance(req, dict) else req.model_dump(by_alias=True)
        resp = self._request_with_retry("post", f"{self.base_url}/create", json=data)
        try:
            return StatusResponse(**resp.json())
        except Exception:
            return ErrorResponse(**resp.json())

    def show(self, req: Union[ShowRequest, Dict[str, Any]]) -> Union[ShowResponse, ErrorResponse]:
        """POST /api/show: Show model information.

        This endpoint retrieves metadata and details about a specific model.
        Relevant Documentation: docs/Ollama_API/Tool_Calling.md
        """
        data = req if isinstance(req, dict) else req.model_dump(by_alias=True)
        resp = self._request_with_retry("post", f"{self.base_url}/show", json=data)
        try:
            return ShowResponse(**resp.json())
        except Exception:
            return ErrorResponse(**resp.json())

    def tags(self) -> Union[ListResponse, ErrorResponse]:
        """GET /api/tags: List local models.

        This endpoint lists all locally available models in the Ollama system.
        """
        resp = self._request_with_retry("get", f"{self.base_url}/tags")
        try:
            return ListResponse(**resp.json())
        except Exception:
            return ErrorResponse(**resp.json())

    def copy(self, req: Union[CopyRequest, Dict[str, Any]]) -> Union[StatusResponse, ErrorResponse]:
        """POST /api/copy: Copy a model.

        This endpoint duplicates an existing model, creating a new instance.
        """
        data = req if isinstance(req, dict) else req.model_dump(by_alias=True)
        resp = self._request_with_retry("post", f"{self.base_url}/copy", json=data)
        try:
            return StatusResponse(**resp.json())
        except Exception:
            return ErrorResponse(**resp.json())

    def delete(self, req: Union[DeleteRequest, Dict[str, Any]]) -> Union[StatusResponse, ErrorResponse]:
        """DELETE /api/delete: Delete a model.

        This endpoint removes a model from the Ollama system.
        """
        data = req if isinstance(req, dict) else req.model_dump(by_alias=True)
        resp = self._request_with_retry("delete", f"{self.base_url}/delete", json=data)
        try:
            return StatusResponse(**resp.json())
        except Exception:
            return ErrorResponse(**resp.json())

    def pull(self, req: Union[PullRequest, Dict[str, Any]]) -> Union[StatusResponse, ErrorResponse]:
        """POST /api/pull: Pull a model.

        This endpoint downloads a model from a remote repository.
        """
        data = req if isinstance(req, dict) else req.model_dump(by_alias=True)
        resp = self._request_with_retry("post", f"{self.base_url}/pull", json=data)
        try:
            return StatusResponse(**resp.json())
        except Exception:
            return ErrorResponse(**resp.json())

    def push(self, req: Union[PushRequest, Dict[str, Any]]) -> Union[StatusResponse, ErrorResponse]:
        """POST /api/push: Push a model.

        This endpoint uploads a model to a remote repository.
        """
        data = req if isinstance(req, dict) else req.model_dump(by_alias=True)
        resp = self._request_with_retry("post", f"{self.base_url}/push", json=data)
        try:
            return StatusResponse(**resp.json())
        except Exception:
            return ErrorResponse(**resp.json())

    def embed(self, req: Union[EmbedRequest, Dict[str, Any]]) -> Union[EmbedResponse, ErrorResponse]:
        """POST /api/embed: Generate embeddings.

        This endpoint generates text embeddings for semantic search, retrieval, and RAG pipelines.
        For more details, refer to the "Embeddings" section in the Ollama API documentation.
        Relevant Documentation: docs/Ollama_API/Embeddings.md
        """
        data = req if isinstance(req, dict) else req.model_dump(by_alias=True)
        resp = self._request_with_retry("post", f"{self.base_url}/embed", json=data)
        try:
            return EmbedResponse(**resp.json())
        except Exception:
            return ErrorResponse(**resp.json())

    def ps(self) -> Union[PsResponse, ErrorResponse]:
        """GET /api/ps: List running models.

        This endpoint lists all currently running models in the Ollama system.
        """
        resp = self._request_with_retry("get", f"{self.base_url}/ps")
        try:
            return PsResponse(**resp.json())
        except Exception:
            return ErrorResponse(**resp.json())

    def version(self) -> Union[VersionResponse, ErrorResponse]:
        """GET /api/version: Get Ollama version.

        This endpoint retrieves the current version of the Ollama system.
        """
        resp = self._request_with_retry("get", f"{self.base_url}/version")
        try:
            return VersionResponse(**resp.json())
        except Exception:
            return ErrorResponse(**resp.json())

if __name__ == "__main__":
    MODEL_1 = "llama3.1:8b-instruct-q8_0"
    MODEL_2 = "qwen3:1.7b"
    MODEL_3 = "qwen3:8b"
    MODEL_Default = MODEL_3
    # Example usage of the chat function with a test prompt
    from ollama_schemas import ChatRequest

    api = OllamaAPI()
    from typing import Callable, Union

    from pydantic import BaseModel,Field
    from typing import Type
    class NumberSequence(BaseModel):
        x_prev: list[int]=Field(description="The previous numbers in the sequence.")
        x_next: Optional[int] = Field(default=None, description="The next number in the sequence.")
    NumberSequence_schema = json.dumps(NumberSequence.model_json_schema())
    
    system_prompt = ("You are a helpful assistant that performs simple arithmetic operations. \n"
                     "Respond ONLY with a JSON object that strictly adheres to the provided schema. \n"
                     "Here is the schema in JSON format:\n" + NumberSequence_schema + "\n")
    
    

    options=ModelOptions(temperature=0.8, num_ctx=8192, num_predict=128)
    initialOrLastOutput = {"x_prev": [0], "x_next": None}
    _create_messages_list = lambda input,prompt: [ChatMessage(role=RoleEnum.SYSTEM, content=system_prompt),
                                                                                  ChatMessage(role=RoleEnum.USER, content="Input:\n"+json.dumps(input)+"\n"+prompt)]
    
    
    def _get_response(request: ChatRequest|GenerateRequest)  -> ChatResponse | ErrorResponse | GenerateResponse | Iterator:
        text, thinking = None, None
        from pydantic import pydantic,Field,BaseModel
        
        response: Optional[ChatResponse|GenerateResponse|ErrorResponse|Iterator] = None 
        match request:
            case ChatRequest():
                response = api.chat(request)
            case GenerateRequest():
                response = api.generate(request)

        if response is None:
            raise ValueError("No response received from Ollama API.")
        return response
    

    class _responseCallbackDict(Dict[type[ChatResponse|GenerateResponse], Optional[Callable[[ChatResponse|GenerateResponse],None]]]):
        def __init__(self,*args, **kwargs): 
            super().__init__(*args, **kwargs)
        def __getitem__(self, key: ChatResponse | GenerateResponse) -> Callable[[ChatResponse | GenerateResponse], None] | None:
                return isinstance(key, ChatResponse) and self.get(ChatResponse) or isinstance(key, GenerateResponse) and self.get(GenerateResponse) or None
        pass

    def _handle_response(response: Union[ChatResponse, GenerateResponse, ErrorResponse, Iterator],
                         callback_dict: _responseCallbackDict=_responseCallbackDict()) -> None:
        
        match response:
            #response is a single ChatResponse
            case chat_response if isinstance(response, ChatResponse):
                if ChatResponseHandler:
                    ChatResponseHandler(chat_response)

            #response is a single GenerateResponse
            case GenerateResponse() as gen_response:
                if GenerateResponseHandler:
                    GenerateResponseHandler(gen_response)

            #response is an iterator
            case response as iterator if isinstance(response, Iterator):
                resp: Any
                for resp in iterator:
                   _handle_response(resp, ChatResponseHandler, GenerateResponseHandler)

            #response is an error
            case response if isinstance(response, ErrorResponse):
                print("ErrorResponse:", response.error)

                resp_type = type(response)
                callback_dict[response]
                callback_func= callback_dict.get(response, None)
                
            case _ if callback_dict and callback_dict.get(type(response), None) is not None:
                resp_type = type(response)
                callback_dict[response]
                callback_func= callback_dict.get(response, None)
        
            raise ValueError("Unexpected response type.")
    
    def _is_assistant_response(response: ChatResponse|GenerateResponse) -> bool:
            match response:
                case ChatResponse(messages=list(ChatResponseMessage(role=RoleEnum.ASSISTANT) as msg) as msgs) if len(msgs) > 0 and msgs[-1] is msg:
                    return True
                case GenerateResponse(role=role):
                    return True
            return False

    def _create_request(input: dict[str,Any], prompt: str, use_chat: bool) -> ChatRequest|GenerateRequest:
        if use_chat:
            return ChatRequest(model=MODEL_Default, messages=_create_messages_list(input, prompt), stream=True, think=True, options=options, format=NumberSequence.model_json_schema())
        else:
            generate_user_prompt = ("Input:\n"+json.dumps(input)+"\n"+prompt)
            return GenerateRequest(model=MODEL_Default, prompt=generate_user_prompt, system=system_prompt, stream=True, think=True, options=options, format=NumberSequence.model_json_schema())
    
    

    for i in range(50):
        user_prompt = ("next_number = previous_number + 1\n"
                            "Calculate the value of next_number\n"
                            "Respond ONLY with JSON that adheres to the following schema:\n"
                            + NumberSequence_schema + "\n")
        
        request = _create_request(initialOrLastOutput, user_prompt, use_chat=True)
        response =  _get_response(request)
        text, thinking = _get_response_text(response), _get_response_thinking(response)
                
        text_buffer: list[str] = []

        
        def _chat_response_handler(response: ChatResponse, textBuffer: list[str]):
            global accumulated_text
            match response.message:
                case ChatResponseMessage(role=RoleEnum.ASSISTANT, content=content, thinking=thinking):
                    if content and len(content) > 0:
                        text_buffer.append(content)
                    if thinking and len(thinking) > 0:
                        print(thinking, end="", flush=True)
                case _:
                    #Ignore other message types for now
                    pass

        def _generate_response_handler(gen_response: GenerateResponse):
            global accumulated_text
            resp, thinking = gen_response.response, gen_response.thinking
            
            if resp and len(resp) > 0:
                accumulated_text += resp
            if thinking and len(thinking) > 0:
                print(thinking, end="", flush=True)


        _handle_response(response, ChatResponseHandler=_chat_response_handler, GenerateResponseHandler=_generate_response_handler)
        print("\nFinal Content:\n", accumulated_text)
        try:
            ns: NumberSequence = NumberSequence.model_validate_json(accumulated_text)
            
            print(f"Parsed Output - x_prev: {ns.x_prev}, x_next: {ns.x_next}")
            initialOrLastOutput = ns.model_dump()

        except Exception as e:
            match e:
                case ValidationError():
                    print("Validation error:", e)
                case json.JSONDecodeError():
                    print("JSON decoding error:", e)
                case _:
                    print("Error parsing JSON output:", e)
            break
    


    
