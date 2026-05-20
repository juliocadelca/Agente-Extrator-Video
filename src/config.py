"""
Configuração central da aplicação.

Gerencia variáveis de ambiente e configurações globais.
"""

import os
from typing import List
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


# Carregar variáveis de ambiente
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """Configurações da aplicação validadas com Pydantic."""
    
    # YouTube API
    youtube_api_key: str = ""
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "text"
    
    # Rate Limiting
    max_retries: int = 3
    retry_delay: int = 2
    
    # Transcrição
    transcript_languages: str = "pt,en,es"  # Será convertido para lista no getter
    transcript_fallback: bool = True
    
    # Comentários
    max_comments: int = 15
    
    model_config = SettingsConfigDict(
        env_file=str(env_path),
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="",
        extra="ignore"
    )
    
    def get_transcript_languages(self) -> List[str]:
        """Retorna lista de idiomas para transcrição."""
        if isinstance(self.transcript_languages, str):
            return [lang.strip() for lang in self.transcript_languages.split(",")]
        return self.transcript_languages
    
    def validate_api_key(self) -> bool:
        """Valida se a chave da API está configurada."""
        if not self.youtube_api_key or self.youtube_api_key == "your_api_key_here":
            return False
        return True


# Instância global de configurações
settings = Settings()
