"""
Configuration Management System

This module implements the configuration layer following best practices:
1. Environment-based configuration (dev/prod/test)
2. Type-safe settings using Pydantic
3. Centralized configuration management
4. Secret management through environment variables

Why this matters for resume-quality:
- Shows understanding of 12-factor app principles
- Demonstrates separation of config from code
- Makes the app deployable to different environments
"""

from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OllamaSettings(BaseSettings):
    """
    Ollama LLM Provider Configuration
    
    This is our "Infrastructure Layer" adapter for the LLM.
    Following Ports & Adapters: we can swap this for OpenAISettings
    later without touching business logic.
    """
    base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API endpoint"
    )
    model: str = Field(
        default="llama3:latest",
        description="Model to use for inference"
    )
    temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0=deterministic, 2=creative)"
    )
    timeout: int = Field(
        default=120,
        description="Request timeout in seconds"
    )


class AgentSettings(BaseSettings):
    """
    CrewAI Agent Behavior Configuration
    
    Controls how agents operate and communicate.
    """
    verbose: bool = Field(
        default=True,
        description="Enable detailed agent logging"
    )
    max_iterations: int = Field(
        default=15,
        description="Maximum reasoning steps per agent"
    )
    allow_delegation: bool = Field(
        default=False,
        description="Allow agents to delegate tasks to each other"
    )


class Settings(BaseSettings):
    """
    Master Configuration Class
    
    Aggregates all configuration sections.
    Uses Pydantic's settings management to load from:
    1. Environment variables (highest priority)
    2. .env file
    3. Default values (lowest priority)
    """
    
    # Application settings
    environment: Literal["development", "production", "test"] = "development"
    log_level: str = Field(default="INFO")
    
    # Nested configuration sections
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)
    
    # Pydantic configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",  # Allows OLLAMA__MODEL=llama3
        case_sensitive=False
    )
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == "development"
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == "production"


# Singleton instance - import this throughout the application
settings = Settings()


# Example usage and testing function
if __name__ == "__main__":
    """
    This allows you to test configuration loading:
    python src/config/settings.py
    """
    print("🔧 Configuration Loaded Successfully!")
    print(f"Environment: {settings.environment}")
    print(f"Ollama URL: {settings.ollama.base_url}")
    print(f"Ollama Model: {settings.ollama.model}")
    print(f"Agent Verbose: {settings.agent.verbose}")
    print(f"Log Level: {settings.log_level}")