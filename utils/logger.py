"""
Sistema de logging estruturado.

Fornece logging configurável com suporte a JSON e texto formatado.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler

from src.config import settings


class JSONFormatter(logging.Formatter):
    """Formatador de logs em JSON estruturado."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata o log como JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Adicionar campos extras
        if hasattr(record, "video_id"):
            log_data["video_id"] = record.video_id
        if hasattr(record, "extra"):
            log_data["extra"] = record.extra
            
        return json.dumps(log_data, ensure_ascii=False)


def setup_logger(name: str = "youtube_extractor") -> logging.Logger:
    """
    Configura e retorna um logger estruturado.
    
    Args:
        name: Nome do logger
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Criar diretório de logs se necessário
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Handler para console
    if settings.log_format.lower() == "json":
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
    else:
        console = Console()
        console_handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            show_time=True,
            show_path=True
        )
    
    logger.addHandler(console_handler)
    
    # Handler para arquivo (sempre JSON para parsing posterior)
    file_handler = logging.FileHandler(
        log_dir / f"{name}.log",
        encoding="utf-8"
    )
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    return logger


# Logger global
logger = setup_logger()


def log_extraction_start(video_id: str) -> None:
    """Registra início de extração."""
    logger.info(
        f"Iniciando extração de dados para vídeo: {video_id}",
        extra={"video_id": video_id, "stage": "start"}
    )


def log_extraction_success(video_id: str, components: Dict[str, bool]) -> None:
    """Registra sucesso na extração."""
    logger.info(
        f"Extração concluída com sucesso para vídeo: {video_id}",
        extra={"video_id": video_id, "components": components, "stage": "success"}
    )


def log_extraction_error(video_id: str, error: Exception, component: str) -> None:
    """Registra erro durante extração."""
    logger.error(
        f"Erro em {component} para vídeo {video_id}: {str(error)}",
        extra={"video_id": video_id, "component": component, "stage": "error"},
        exc_info=True
    )


def log_api_call(service: str, method: str, params: Dict[str, Any]) -> None:
    """Registra chamada de API."""
    logger.debug(
        f"Chamada API: {service}.{method}",
        extra={"service": service, "method": method, "params": params}
    )
