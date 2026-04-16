# Updated anl_asksage_client.py
# Changes applied based on comparison with the new client.py

from __future__ import annotations

import json
import logging
from typing import Any, Dict, IO, List, Optional, Union

import requests
from requests import Response, Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse


class ANLAskSageClientError(Exception):
    """
    Base exception for ANLAskSageClient errors.
    """


class RequestError(ANLAskSageClientError):
    """
    Raised when an HTTP request fails.
    """


class TokenError(ANLAskSageClientError):
    """
    Raised when acquiring an access token fails.
    """


class ANLAskSageClient:
    """
    A secure, resilient Python client for interacting with the Ask Sage APIs.

    - Enforces HTTPS-only for all requests and base URLs; HTTP is rejected
    - Uses a persistent requests.Session with retries and backoff for robustness
    - Honors the provided HTTP method (GET/POST), though current API uses POST
    - Adds timeouts to all network calls (configurable)
    - Safer logging (no sensitive payloads), structured error handling
    - Input validation and safer file handling (context-managed, optional file-like support)
    - Stronger typing, improved docstrings, readability, and maintainability
    - Optional custom CA bundle for TLS verification
    - Omits None values from form payloads to match API expectations
    - Disables automatic redirects to prevent HTTPS → HTTP downgrades
    """

    def __init__(
        self,
        email: str,
        api_key: str,
        user_base_url: str = "https://api.asksage.anl.gov/user",
        server_base_url: str = "https://api.asksage.anl.gov/server",
        path_to_CA_Bundle: Optional[str] = None,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        user_agent: str = "ANLAskSageClient/2.1",
    ) -> None:
        """
        Initialize the client with service base URLs and obtain a short-lived token.

        Parameters:
        - email: User email for token retrieval
        - api_key: API key for token retrieval
        - user_base_url: Base URL for user-scoped endpoints (must be HTTPS)
        - server_base_url: Base URL for server-scoped endpoints (must be HTTPS)
        - path_to_CA_Bundle: Optional path to a custom CA bundle (TLS verification)
        - timeout_seconds: Default per-request timeout in seconds
        - max_retries: HTTP retry count for transient errors
        - backoff_factor: Exponential backoff factor for retries
        - user_agent: Custom User-Agent header value
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        # Validate and normalize base URLs (HTTPS only)
        self.user_base_url = self._validate_https_base_url(user_base_url)
        self.server_base_url = self._validate_https_base_url(server_base_url)

        # TLS verification (True or path to CA bundle)
        self.verify: Union[bool, str] = path_to_CA_Bundle if path_to_CA_Bundle else True
        self.timeout = timeout_seconds

        # Create a single persistent session with retries
        self.session: Session = requests.Session()
        retry = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "POST"]),
            raise_on_status=False,
            respect_retry_after_header=True,
            # We rely on explicit redirect handling (disabled in request call)
            # to avoid scheme downgrades; do not auto-follow at adapter level.
            redirect=0,
        )
        adapter = HTTPAdapter(max_retries=retry)
        # Mount HTTPS adapter only; do not mount HTTP to avoid accidental usage
        self.session.mount("https://", adapter)

        # Set default headers (token added below after retrieval)
        self.default_headers: Dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": user_agent,
        }

        # Obtain token and store authorization header
        token = self.get_token(email, api_key)
        self.headers = {**self.default_headers, "x-access-tokens": token}

    # --------------- Internal helpers ---------------
    @staticmethod
    def _validate_https_base_url(url: str) -> str:
        """
        Ensure the base URL is HTTPS and return a normalized value without trailing slash.
        """
        if not isinstance(url, str):
            raise ValueError("Base URL must be a string")
        parsed = urlparse(url.strip())
        if parsed.scheme.lower() != "https":
            raise ValueError(f"Insecure base URL not allowed (must be HTTPS): {url}")
        if not parsed.netloc:
            raise ValueError(f"Invalid base URL missing host: {url}")
        return url.rstrip("/")

    @staticmethod
    def _ensure_https_url(url: str) -> None:
        """Raise an error if the URL is not HTTPS."""
        parsed = urlparse(url)
        if parsed.scheme.lower() != "https":
            raise RequestError(f"Insecure URL scheme blocked (must be HTTPS): {url}")
        if not parsed.netloc:
            raise RequestError(f"Invalid URL missing host: {url}")

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, IO[bytes]]] = None,
        base_url: Optional[str] = None,
        skip_headers: bool = False,
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """
        Perform an HTTP request with robust error handling.

        - Enforces HTTPS-only URLs
        - Disables automatic redirects to prevent HTTPS → HTTP downgrade attacks
        - Uses session with retries
        - Applies default timeout
        - Returns JSON if possible; otherwise returns text payload with status
        """
        base = (self._validate_https_base_url(base_url) if base_url else self.server_base_url).rstrip("/")
        url = f"{base}/{endpoint.lstrip('/') }"

        # Enforce HTTPS-only
        self._ensure_https_url(url)

        headers = self.default_headers if skip_headers else self.headers

        try:
            response: Response = self.session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=json,
                files=files,
                data=data,
                verify=self.verify,
                timeout=timeout or self.timeout,
                allow_redirects=False,  # security: do not auto-follow redirects
            )

            # Block any redirect response explicitly (3xx)
            if 300 <= response.status_code < 400:
                location = response.headers.get("Location", "")
                # Warn without leaking sensitive data
                self.logger.warning(
                    "Blocked redirect: method=%s url=%s status=%s location=%s",
                    method,
                    url,
                    response.status_code,
                    location,
                )
                raise RequestError(
                    f"Redirect blocked for security (no automatic redirects allowed). Location: {location}"
                )

            # Raise for 4xx/5xx
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            # Avoid logging sensitive payloads (e.g., tokens, message contents)
            self.logger.exception(
                "HTTP request failed: method=%s url=%s status=%s",
                method,
                url,
                getattr(exc.response, "status_code", None) if isinstance(exc, requests.HTTPError) else None,
            )
            raise RequestError(str(exc)) from exc

        # Attempt JSON decode
        try:
            return response.json()
        except ValueError:
            # Return raw text with metadata as a fallback
            return {
                "status_code": response.status_code,
                "text": response.text,
                "content_type": response.headers.get("Content-Type", ""),
            }

    @staticmethod
    def _json_dumps_safe(value: Any) -> str:
        """Serialize Python objects to compact JSON strings with safe defaults."""
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    # --------------- Auth ---------------
    def get_token(self, email: str, api_key: str) -> str:
        """
        Get a short-lived token (required for all other API calls).
        """
        resp = self._request(
            "POST",
            "get-token-with-api-key",
            json={"email": email, "api_key": api_key},
            base_url=self.user_base_url,
            skip_headers=True,
        )

        try:
            status = int(resp.get("status"))
        except Exception as exc:  # noqa: BLE001
            raise TokenError("Malformed token response: missing or invalid status") from exc

        if status != 200:
            raise TokenError("Error getting access token")

        try:
            return resp["response"]["access_token"]
        except Exception as exc:  # noqa: BLE001
            raise TokenError("Malformed token response: missing access_token") from exc

    # --------------- User-scoped endpoints ---------------
    def add_dataset(self, dataset: str, classification: Optional[str] = None) -> Any:
        """
        Add a dataset. An optional classification (e.g. "Unclassified", "CUI") may be provided.
        """
        payload: Dict[str, Any] = {"dataset": dataset}
        if classification is not None:
            payload["classification"] = classification
        return self._request(
            "POST",
            "add-dataset",
            json=payload,
            base_url=self.user_base_url,
        )

    def append_chat(self, chat_title: str, chats: Dict[str, Any]) -> Any:
        if not isinstance(chat_title, str):
            raise ValueError("chat_title must be a string")
        if len(chat_title) > 200:  # loosen a bit vs doc's 20 chars to avoid silent failures
            raise ValueError("chat_title too long")

        return self._request(
            "POST",
            "append-chat",
            json={"chats": chats, "chat_title": chat_title},
            base_url=self.user_base_url,
        )

    def delete_dataset(self, dataset: str) -> Any:
        return self._request(
            "POST",
            "delete-dataset",
            json={"dataset": dataset},
            base_url=self.user_base_url,
        )

    def assign_dataset(self, dataset: str, email: str) -> Any:
        return self._request(
            "POST",
            "assign-dataset",
            json={"dataset": dataset, "email": email},
            base_url=self.user_base_url,
        )

    def get_user_logs(self) -> Any:
        return self._request("POST", "get-user-logs", base_url=self.user_base_url)

    def get_user_logins(self, limit: int = 5) -> Any:
        if limit <= 0:
            raise ValueError("limit must be a positive integer")
        return self._request(
            "POST",
            "get-user-logins",
            json={"limit": limit},
            base_url=self.user_base_url,
        )

    # --------------- Server-scoped endpoints ---------------
    def get_models(self) -> Any:
        return self._request("POST", "get-models", json={})

    def get_personas(self) -> Any:
        return self._request("POST", "get-personas")

    def get_datasets(self) -> Any:
        return self._request("POST", "get-datasets")

    def get_plugins(self) -> Any:
        return self._request("POST", "get-plugins")

    def count_monthly_tokens(self) -> Any:
        return self._request("POST", "count-monthly-tokens")

    def count_monthly_teach_tokens(self) -> Any:
        return self._request("POST", "count-monthly-teach-tokens")

    def follow_up_questions(self, message: str) -> Any:
        return self._request("POST", "follow-up-questions", json={"message": message})

    def tokenizer(self, content: str) -> Any:
        return self._request("POST", "tokenizer", json={"content": content})

    def train(
        self,
        content: str,
        force_dataset: Optional[str] = None,
        context: str = "",
        skip_vectordb: bool = False,
    ) -> Any:
        payload = {
            "content": content,
            "force_dataset": force_dataset,
            "context": context,
            "skip_vectordb": skip_vectordb,
        }
        # Remove None values to avoid confusing the backend
        payload = {k: v for k, v in payload.items() if v is not None}
        return self._request("POST", "train", json=payload)

    def train_with_file(self, file_path: str, dataset: str) -> Any:
        with open(file_path, "rb") as f:
            files = {"file": f}
            return self._request(
                "POST", "train-with-file", files=files, data={"dataset": dataset}
            )

    def file(self, file_path: str, strategy: str = "auto") -> Any:
        with open(file_path, "rb") as f:
            files = {"file": f}
            return self._request(
                "POST", "file", files=files, data={"strategy": strategy}
            )

    # --------------- Query endpoints ---------------
    def query(
        self,
        message: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        persona: str = "default",
        dataset: str = "all",
        limit_references: Optional[int] = None,
        temperature: float = 0.0,
        live: int = 0,
        model: str = "openai_gpt",
        system_prompt: Optional[str] = None,
        file: Optional[Union[str, IO[bytes]]] = None,
        tools: Optional[Union[List[Dict[str, Any]], Dict[str, Any], str]] = None,
        tool_choice: Optional[Union[Dict[str, Any], str]] = None,
        reasoning_effort: Optional[str] = None,
    ) -> Any:
        """
        Interact with the /query endpoint of the Ask Sage API.

        Note: If a file is provided, a multipart/form-data request is sent; otherwise
        JSON fields are sent as form data as per the original API expectation.
        """
        # Normalize message to a string (API expects a string field even for arrays)
        if isinstance(message, (list, dict)):
            message_str = self._json_dumps_safe(message)
        elif isinstance(message, str):
            message_str = message
        else:
            message_str = self._json_dumps_safe(message)

        # Tools/tool_choice must be JSON strings if not already strings
        tools_str = tools
        if tools is not None and not isinstance(tools, str):
            tools_str = self._json_dumps_safe(tools)
        tool_choice_str = tool_choice
        if tool_choice is not None and not isinstance(tool_choice, str):
            tool_choice_str = self._json_dumps_safe(tool_choice)

        # Validate reasoning_effort if provided (new in client.py)
        if reasoning_effort is not None:
            if reasoning_effort not in ["low", "medium", "high"]:
                raise ValueError("reasoning_effort must be one of: low, medium, high")

        # Build form payload; omit None values entirely
        data: Dict[str, Any] = {
            "message": message_str,
            "persona": persona,
            "dataset": dataset,
            "temperature": temperature,
            "live": live,
            "model": model,
        }
        if limit_references is not None:
            data["limit_references"] = limit_references
        if system_prompt is not None:
            data["system_prompt"] = system_prompt
        if tools_str is not None:
            data["tools"] = tools_str
        if tool_choice_str is not None:
            data["tool_choice"] = tool_choice_str
        if reasoning_effort is not None:
            data["reasoning_effort"] = reasoning_effort

        # Handle optional file; support file path or file-like object
        opened_here = False
        files_dict: Optional[Dict[str, IO[bytes]]] = None
        try:
            if isinstance(file, str):
                f = open(file, "rb")
                opened_here = True
                files_dict = {"file": f}
            elif file is not None:
                files_dict = {"file": file}

            return self._request("POST", "query", files=files_dict, data=data)
        finally:
            if opened_here and files_dict and files_dict.get("file"):
                try:
                    files_dict["file"].close()
                except Exception:  # noqa: BLE001
                    self.logger.debug("Failed to close file handle opened by client.")

    def query_with_file(
        self,
        message: Union[str, Dict[str, Any], List[Dict[str, Any]]],
        file: Optional[Union[str, IO[bytes]]] = None,
        persona: str = "default",
        dataset: str = "all",
        limit_references: Optional[int] = None,
        temperature: float = 0.0,
        live: int = 0,
        model: str = "openai_gpt",
        tools: Optional[Union[List[Dict[str, Any]], Dict[str, Any], str]] = None,
        tool_choice: Optional[Union[Dict[str, Any], str]] = None,
        reasoning_effort: Optional[str] = None,
    ) -> Any:
        return self.query(
            message,
            persona=persona,
            dataset=dataset,
            limit_references=limit_references,
            temperature=temperature,
            live=live,
            model=model,
            file=file,
            tools=tools,
            tool_choice=tool_choice,
            reasoning_effort=reasoning_effort,
        )

    def query_plugin(
        self,
        plugin_tag: str,
        dataset: str = "all",
        limit_references: Optional[int] = None,
        model: str = "openai_gpt",
        **params: Any,
    ) -> Any:
        """
        Execute a plugin by expanding its prompt template with provided parameters
        and invoking the /query endpoint.
        """
        if "[[" not in plugin_tag:
            plugin_tag = f"[[{plugin_tag}]]"

        prompt_template: Optional[str] = None
        plugins = self.get_plugins()
        for plugin in plugins.get("response", []):
            try:
                if plugin_tag in plugin.get("prompt_template", ""):
                    prompt_template = plugin["prompt_template"]
                    break
            except Exception:  # noqa: BLE001
                continue

        if not prompt_template:
            raise KeyError(f"Plugin not found: {plugin_tag}")

        try:
            message = prompt_template.format(**params)
        except KeyError as exc:
            missing = str(exc)
            raise ValueError(
                f"Missing required plugin parameter {missing} for {plugin_tag}"
            ) from exc

        return self.query(
            message,
            persona="default",
            dataset=dataset,
            limit_references=limit_references,
            model=model,
        )

    def execute_plugin(self, plugin_name: str, plugin_values: Dict[str, Any], model: Optional[str] = None) -> Any:
        """
        Execute a plugin using the execute-plugin endpoint.

        Sends plugin_values as JSON (not a dumped string) to preserve types.
        """
        payload: Dict[str, Any] = {"plugin_name": plugin_name, "plugin_values": plugin_values}
        if model:
            payload["model"] = model
        return self._request("POST", "execute-plugin", json=payload)

    # --------------- Context manager support ---------------
    def close(self) -> None:
        """
        Close the underlying HTTP session.
        """
        try:
            self.session.close()
        except Exception:  # noqa: BLE001
            pass

    def __enter__(self) -> "ANLAskSageClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self.close()