"""
Modelos de dados para estruturação e validação.

Define as estruturas de dados usadas em toda a aplicação.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class Comment(BaseModel):
    """Modelo para comentário do YouTube."""
    
    author: str = Field(..., description="Nome do autor do comentário")
    text: str = Field(..., description="Texto do comentário")
    published_at: str = Field(..., description="Data de publicação (ISO 8601)")
    likes: int = Field(default=0, description="Quantidade de likes")
    replies: List['Comment'] = Field(default_factory=list, description="Respostas ao comentário")
    
    class Config:
        json_schema_extra = {
            "example": {
                "author": "João Silva",
                "text": "Excelente vídeo!",
                "published_at": "2024-01-15T10:30:00Z",
                "likes": 42
            }
        }


class VideoData(BaseModel):
    """Modelo completo de dados do vídeo."""
    
    video_id: str = Field(..., description="ID único do vídeo no YouTube")
    title: str = Field(..., description="Título do vídeo")
    description: str = Field(..., description="Descrição completa do vídeo")
    hashtags: List[str] = Field(default_factory=list, description="Hashtags extraídas da descrição")
    transcript: Optional[str] = Field(None, description="Transcrição completa do áudio")
    recent_comments: List[Comment] = Field(default_factory=list, description="15 comentários mais recentes")
    
    # Metadados adicionais
    channel_title: Optional[str] = Field(None, description="Nome do canal")
    published_at: Optional[str] = Field(None, description="Data de publicação do vídeo")
    duration: Optional[str] = Field(None, description="Duração do vídeo (ISO 8601)")
    view_count: Optional[int] = Field(None, description="Quantidade de visualizações")
    like_count: Optional[int] = Field(None, description="Quantidade de likes")
    comment_count: Optional[int] = Field(None, description="Quantidade total de comentários")
    
    # Status de extração
    extraction_timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp da extração"
    )
    transcript_available: bool = Field(default=False, description="Indica se transcrição está disponível")
    comments_enabled: bool = Field(default=True, description="Indica se comentários estão habilitados")
    
    class Config:
        json_schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "title": "Exemplo de Vídeo",
                "description": "Esta é uma descrição de exemplo #tutorial #python",
                "hashtags": ["tutorial", "python"],
                "transcript": "Bem-vindo ao nosso tutorial...",
                "recent_comments": [
                    {
                        "author": "João Silva",
                        "text": "Ótimo conteúdo!",
                        "published_at": "2024-01-15T10:30:00Z",
                        "likes": 10
                    }
                ],
                "channel_title": "Canal Exemplo",
                "published_at": "2024-01-01T12:00:00Z",
                "duration": "PT10M30S",
                "view_count": 1000000,
                "like_count": 50000,
                "comment_count": 1500,
                "extraction_timestamp": "2024-01-15T15:00:00Z",
                "transcript_available": True,
                "comments_enabled": True
            }
        }
    
    def to_simple_dict(self) -> dict:
        """Retorna versão simplificada para compatibilidade com requisitos."""
        return {
            "title": self.title,
            "description": self.description,
            "hashtags": self.hashtags,
            "transcript": self.transcript or "",
            "recent_comments": [
                {
                    "author": c.author,
                    "text": c.text,
                    "published_at": c.published_at,
                    "replies": [
                        {
                            "author": r.author,
                            "text": r.text,
                            "published_at": r.published_at
                        }
                        for r in c.replies
                    ]
                }
                for c in self.recent_comments
            ]
        }


class ExtractionError(BaseModel):
    """Modelo para erros de extração."""
    
    error_type: str = Field(..., description="Tipo do erro")
    message: str = Field(..., description="Mensagem de erro")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp do erro"
    )
    video_id: Optional[str] = Field(None, description="ID do vídeo relacionado")
