"""Utilities for data loading, Neo4j operations, and Databricks AI services."""

import asyncio
from pathlib import Path
from typing import Any, Optional, Sequence

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j_graphrag.embeddings.base import Embedder
from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import FixedSizeSplitter
from neo4j_graphrag.llm.base import LLMInterface
from neo4j_graphrag.llm.types import LLMResponse
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load configuration from project root
_config_file = Path(__file__).parent.parent / "CONFIG.txt"
load_dotenv(_config_file)


# =============================================================================
# Configuration Classes
# =============================================================================

class Neo4jConfig(BaseSettings):
    """Neo4j configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    uri: str = Field(validation_alias="NEO4J_URI")
    username: str = Field(validation_alias="NEO4J_USERNAME")
    password: str = Field(validation_alias="NEO4J_PASSWORD")


class DatabricksConfig(BaseSettings):
    """Databricks Model Serving configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    host: str = Field(validation_alias="DATABRICKS_HOST")
    token: str = Field(validation_alias="DATABRICKS_TOKEN")
    llm_endpoint: str = Field(
        default="databricks-meta-llama-3-3-70b-instruct",
        validation_alias="DATABRICKS_LLM_ENDPOINT"
    )
    embedding_endpoint: str = Field(
        default="databricks-gte-large-en",
        validation_alias="DATABRICKS_EMBEDDING_ENDPOINT"
    )


# =============================================================================
# Databricks Embedder (implements neo4j-graphrag Embedder interface)
# =============================================================================

class DatabricksEmbedder(Embedder):
    """Databricks Model Serving embedder compatible with neo4j-graphrag."""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        host: Optional[str] = None,
        token: Optional[str] = None,
    ):
        """Initialize Databricks embedder.

        Args:
            endpoint: Model serving endpoint name (default: from config)
            host: Databricks workspace URL (default: from config)
            token: Databricks access token (default: from config)
        """
        config = DatabricksConfig()
        self.endpoint = endpoint or config.embedding_endpoint
        self._host = host or config.host
        self._token = token or config.token
        self._embeddings = None

    @property
    def embeddings(self):
        """Lazy initialization of DatabricksEmbeddings."""
        if self._embeddings is None:
            from databricks_langchain import DatabricksEmbeddings
            self._embeddings = DatabricksEmbeddings(
                endpoint=self.endpoint,
                host=self._host,
                api_key=self._token,
            )
        return self._embeddings

    def embed_query(self, text: str) -> list[float]:
        """Embed query text synchronously.

        Args:
            text: Text to embed

        Returns:
            Vector embedding as list of floats
        """
        return self.embeddings.embed_query(text)

    async def async_embed_query(self, text: str) -> list[float]:
        """Embed query text asynchronously.

        Args:
            text: Text to embed

        Returns:
            Vector embedding as list of floats
        """
        return await self.embeddings.aembed_query(text)


# =============================================================================
# Databricks LLM (implements neo4j-graphrag LLMInterface)
# =============================================================================

class DatabricksLLM(LLMInterface):
    """Databricks Model Serving LLM compatible with neo4j-graphrag."""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        host: Optional[str] = None,
        token: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 1000,
    ):
        """Initialize Databricks LLM.

        Args:
            endpoint: Model serving endpoint name (default: from config)
            host: Databricks workspace URL (default: from config)
            token: Databricks access token (default: from config)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        config = DatabricksConfig()
        self.endpoint = endpoint or config.llm_endpoint
        self._host = host or config.host
        self._token = token or config.token
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._chat_model = None

    @property
    def model_id(self) -> str:
        """Return the model endpoint name."""
        return self.endpoint

    @property
    def supports_structured_output(self) -> bool:
        """Whether this LLM supports structured output."""
        return False

    @property
    def chat_model(self):
        """Lazy initialization of ChatDatabricks."""
        if self._chat_model is None:
            from databricks_langchain import ChatDatabricks
            self._chat_model = ChatDatabricks(
                endpoint=self.endpoint,
                host=self._host,
                api_key=self._token,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        return self._chat_model

    def invoke(
        self,
        input: str,
        message_history: Optional[list[dict[str, str]]] = None,
        system_instruction: Optional[str] = None,
    ) -> LLMResponse:
        """Send text to the model and get a response.

        Args:
            input: User input text
            message_history: Optional conversation history
            system_instruction: Optional system prompt override

        Returns:
            LLMResponse with generated content
        """
        messages = []

        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})

        if message_history:
            messages.extend(message_history)

        messages.append({"role": "user", "content": input})

        response = self.chat_model.invoke(messages)
        return LLMResponse(content=response.content)

    async def ainvoke(
        self,
        input: str,
        message_history: Optional[list[dict[str, str]]] = None,
        system_instruction: Optional[str] = None,
    ) -> LLMResponse:
        """Send text to the model asynchronously.

        Args:
            input: User input text
            message_history: Optional conversation history
            system_instruction: Optional system prompt override

        Returns:
            LLMResponse with generated content
        """
        messages = []

        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})

        if message_history:
            messages.extend(message_history)

        messages.append({"role": "user", "content": input})

        response = await self.chat_model.ainvoke(messages)
        return LLMResponse(content=response.content)

    def invoke_with_tools(
        self,
        input: str,
        tools: Sequence[Any],
        message_history: Optional[list[dict[str, str]]] = None,
        system_instruction: Optional[str] = None,
    ) -> Any:
        """Invoke with tool calling (not implemented)."""
        raise NotImplementedError("Tool calling not implemented for Databricks LLM wrapper")

    async def ainvoke_with_tools(
        self,
        input: str,
        tools: Sequence[Any],
        message_history: Optional[list[dict[str, str]]] = None,
        system_instruction: Optional[str] = None,
    ) -> Any:
        """Invoke with tool calling asynchronously (not implemented)."""
        raise NotImplementedError("Tool calling not implemented for Databricks LLM wrapper")


# =============================================================================
# AI Service Factory Functions
# =============================================================================

def get_embedder() -> DatabricksEmbedder:
    """Get embedder using Databricks Model Serving."""
    return DatabricksEmbedder()


def get_llm() -> DatabricksLLM:
    """Get LLM using Databricks Model Serving."""
    return DatabricksLLM()


# =============================================================================
# Neo4j Connection
# =============================================================================

class Neo4jConnection:
    """Manages Neo4j database connection."""

    def __init__(self):
        """Initialize and connect to Neo4j using environment configuration."""
        self.config = Neo4jConfig()
        self.driver = GraphDatabase.driver(
            self.config.uri,
            auth=(self.config.username, self.config.password)
        )

    def verify(self):
        """Verify the connection is working."""
        self.driver.verify_connectivity()
        print("Connected to Neo4j successfully!")
        return self

    def clear_graph(self):
        """Remove all Document and Chunk nodes."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n) WHERE n:Document OR n:Chunk
                DETACH DELETE n
                RETURN count(n) as deleted
            """)
            count = result.single()["deleted"]
            print(f"Deleted {count} nodes")
        return self

    def close(self):
        """Close the database connection."""
        self.driver.close()
        print("Connection closed.")


# =============================================================================
# Data Loading
# =============================================================================

class DataLoader:
    """Handles loading text data from files."""

    def __init__(self, file_path: str):
        """Initialize with path to data file."""
        self.file_path = Path(file_path)
        self._text = None

    @property
    def text(self) -> str:
        """Load and return the text content from the file."""
        if self._text is None:
            self._text = self.file_path.read_text().strip()
        return self._text

    def get_metadata(self) -> dict:
        """Return metadata about the loaded file."""
        return {
            "path": str(self.file_path),
            "name": self.file_path.name,
            "size": len(self.text)
        }


# =============================================================================
# Text Splitting
# =============================================================================

def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    """Split text into chunks using FixedSizeSplitter.

    Args:
        text: Text to split
        chunk_size: Maximum characters per chunk
        chunk_overlap: Characters to overlap between chunks

    Returns:
        List of chunk text strings
    """
    splitter = FixedSizeSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        approximate=True
    )

    # Handle both Jupyter (running event loop) and regular Python
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None:
        # Running in Jupyter or async context - use nest_asyncio
        import nest_asyncio
        nest_asyncio.apply()
        result = asyncio.run(splitter.run(text))
    else:
        # Regular Python - use asyncio.run directly
        result = asyncio.run(splitter.run(text))

    return [chunk.text for chunk in result.chunks]
