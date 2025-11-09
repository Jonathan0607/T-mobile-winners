"""
NVIDIA Nemotron API client with tool calling support.
Handles all interactions with the Nemotron model via NVIDIA API Catalog directly (no OpenAI client).
"""

import os
from typing import List, Dict, Optional, Callable
import json
import requests


class NemotronClient:
    """Client for interacting with NVIDIA Nemotron models via HTTP."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "nvidia/llama-3.3-nemotron-super-49b-v1.5", base_url: str = "https://integrate.api.nvidia.com/v1"):
        """
        Initialize the Nemotron client.
        
        Args:
            api_key: NVIDIA API key (or set NVIDIA_API_KEY env var)
            model: Model name from NVIDIA API Catalog
            base_url: NVIDIA Integrate API base URL
        """
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY must be provided or set as environment variable")
        
        self.model = model
        self.base_url = base_url.rstrip("/")
        
        # Prepare HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def _chat_completions(self, payload: Dict) -> Dict:
        """POST to NVIDIA Integrate chat completions endpoint and return JSON."""
        url = f"{self.base_url}/chat/completions"
        resp = self.session.post(url, data=json.dumps(payload), timeout=60)
        if not resp.ok:
            try:
                err = resp.json()
            except Exception:
                err = {"error": resp.text}
            raise RuntimeError(f"Nemotron API error {resp.status_code}: {err}")
        return resp.json()
    
    def call(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        top_p: float = 0.7,
        max_tokens: int = 2048,
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[str] = None
    ) -> str:
        """
        Make a standard chat completion call to Nemotron.
        
        Args:
            system_prompt: System message defining the agent's role
            user_prompt: User message with the task
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens to generate
            tools: Optional list of tool definitions for function calling
            tool_choice: "auto", "none", or specific tool name
        
        Returns:
            Generated text response
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        payload: Dict = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice or "auto"
        
        data = self._chat_completions(payload)
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        
        # Handle tool calls if present
        tool_calls = message.get("tool_calls")
        if tool_calls:
            # Normalize tool calls structure
            normalized = []
            for tc in tool_calls:
                func = tc.get("function", {})
                args = func.get("arguments", "{}")
                try:
                    parsed_args = json.loads(args) if isinstance(args, str) else args
                except Exception:
                    parsed_args = {}
                normalized.append({
                    "id": tc.get("id"),
                    "name": func.get("name"),
                    "arguments": parsed_args
                })
            return {"type": "tool_call", "tool_calls": normalized}
        
        return message.get("content", "")
    
    def call_with_tools(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: Dict[str, Callable],
        tool_schemas: List[Dict],
        max_iterations: int = 5
    ) -> str:
        """
        Call Nemotron with tool support, handling the tool calling loop.
        
        Args:
            system_prompt: System message
            user_prompt: User message
            tools: Dict mapping tool names to callable functions
            tool_schemas: List of tool schema definitions
            max_iterations: Maximum tool calling iterations
        
        Returns:
            Final text response after tool calls
        """
        messages: List[Dict] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        for _ in range(max_iterations):
            payload: Dict = {
                "model": self.model,
                "messages": messages,
                "tools": tool_schemas,
                "tool_choice": "auto",
                "temperature": 0.2,
                "top_p": 0.7,
                "max_tokens": 2048
            }
            data = self._chat_completions(payload)
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            
            # Append assistant message (may include tool calls) to history
            messages.append(message)
            
            tool_calls = message.get("tool_calls")
            if not tool_calls:
                # No tools requested, return final answer
                return message.get("content", "")
            
            # Execute tool calls and append results
            for tc in tool_calls:
                func = tc.get("function", {})
                function_name = func.get("name")
                args_raw = func.get("arguments", "{}")
                try:
                    function_args = json.loads(args_raw) if isinstance(args_raw, str) else (args_raw or {})
                except Exception:
                    function_args = {}
                
                if function_name not in tools:
                    tool_result = f"Error: Tool {function_name} not found"
                else:
                    try:
                        result = tools[function_name](**function_args)
                        tool_result = result if isinstance(result, str) else json.dumps(result)
                    except Exception as e:
                        tool_result = f"Error executing tool: {str(e)}"
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id"),
                    "content": tool_result
                })
        
        # If we've exhausted iterations, return the last assistant/content if any
        for m in reversed(messages):
            if m.get("role") == "assistant" and m.get("content"):
                return m["content"]
        return "Maximum iterations reached"
    
    def chat(self, messages: List[Dict]) -> str:
        """
        Chat interface compatible with OpenAI-style message format.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
                     Example: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        
        Returns:
            Generated text response from Nemotron
        """
        # Extract system and user prompts from messages
        system_prompt = ""
        user_prompt = ""
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "system":
                system_prompt = content
            elif role == "user":
                if user_prompt:
                    user_prompt += "\n\n" + content
                else:
                    user_prompt = content
        
        # Use call method if we have both system and user prompts
        if system_prompt and user_prompt:
            return self.call(system_prompt, user_prompt, temperature=0.2, max_tokens=2048)
        elif user_prompt:
            # If no system prompt, use empty system prompt
            return self.call("", user_prompt, temperature=0.2, max_tokens=2048)
        else:
            return "No user message found in chat messages"

