"""
Parser e validador de URLs do YouTube.

Extrai IDs de vídeo de diferentes formatos de URL do YouTube.
"""

import re
from typing import Optional
from urllib.parse import urlparse, parse_qs

from utils.logger import logger


class URLParser:
    """Parser de URLs do YouTube."""
    
    # Padrões de URL suportados
    PATTERNS = {
        "standard": r"(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})",
        "shorts": r"youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
        "embed": r"youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        "direct_id": r"^([a-zA-Z0-9_-]{11})$"
    }
    
    @classmethod
    def extract_video_id(cls, url_or_id: str) -> Optional[str]:
        """
        Extrai o ID do vídeo de uma URL ou valida um ID direto.
        
        Args:
            url_or_id: URL completa do YouTube ou ID do vídeo
            
        Returns:
            ID do vídeo se válido, None caso contrário
            
        Examples:
            >>> URLParser.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            'dQw4w9WgXcQ'
            >>> URLParser.extract_video_id("https://youtu.be/dQw4w9WgXcQ")
            'dQw4w9WgXcQ'
            >>> URLParser.extract_video_id("https://youtube.com/shorts/dQw4w9WgXcQ")
            'dQw4w9WgXcQ'
            >>> URLParser.extract_video_id("dQw4w9WgXcQ")
            'dQw4w9WgXcQ'
        """
        url_or_id = url_or_id.strip()
        
        logger.debug(f"Tentando extrair ID do vídeo de: {url_or_id}")
        
        # Tentar cada padrão
        for pattern_name, pattern in cls.PATTERNS.items():
            match = re.search(pattern, url_or_id)
            if match:
                video_id = match.group(1)
                logger.info(f"ID do vídeo extraído ({pattern_name}): {video_id}")
                return video_id
        
        logger.warning(f"Não foi possível extrair ID do vídeo de: {url_or_id}")
        return None
    
    @classmethod
    def validate_video_id(cls, video_id: str) -> bool:
        """
        Valida se uma string é um ID de vídeo válido do YouTube.
        
        Args:
            video_id: String para validar
            
        Returns:
            True se válido, False caso contrário
        """
        if not video_id:
            return False
        
        # IDs do YouTube têm 11 caracteres alfanuméricos, underscore ou hífen
        pattern = r"^[a-zA-Z0-9_-]{11}$"
        return bool(re.match(pattern, video_id))
    
    @classmethod
    def is_youtube_url(cls, url: str) -> bool:
        """
        Verifica se uma URL é do YouTube.
        
        Args:
            url: URL para verificar
            
        Returns:
            True se for URL do YouTube, False caso contrário
        """
        try:
            parsed = urlparse(url)
            youtube_domains = ["youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"]
            return parsed.netloc in youtube_domains
        except Exception as e:
            logger.error(f"Erro ao validar URL: {e}")
            return False
    

    @classmethod
    def extract_hashtags(cls, text: str) -> list[str]:
        """
        Extrai hashtags de um texto.
        
        Args:
            text: Texto para extrair hashtags (ex: descrição)
            
        Returns:
            Lista de hashtags encontradas (sem o #)
        """
        if not text:
            return []
            
        # Encontrar todas as ocorrências de #palavra
        # \w inclui letras, números e underscore
        hashtags = re.findall(r"#(\w+)", text)
        
        # Remover duplicatas mantendo ordem
        return list(dict.fromkeys(hashtags))

    @classmethod
    def get_url_type(cls, url: str) -> Optional[str]:
        """
        Identifica o tipo de URL do YouTube.
        
        Args:
            url: URL para identificar
            
        Returns:
            Tipo da URL ('standard', 'shorts', 'embed') ou None
        """
        for url_type, pattern in cls.PATTERNS.items():
            if url_type != "direct_id" and re.search(pattern, url):
                return url_type
        return None
