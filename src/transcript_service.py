"""
Serviço de extração de transcrições.

Obtém legendas/transcrições de vídeos do YouTube.
"""

from typing import Optional, List
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)

from src.config import settings
from utils.logger import logger


class TranscriptService:
    """Serviço para extração de transcrições."""
    
    def __init__(self):
        """Inicializa o serviço de transcrições."""
        self.api = YouTubeTranscriptApi()  # Mantém uma instância da API
        self.languages = settings.get_transcript_languages()
        self.fallback_enabled = settings.transcript_fallback
        logger.info("Serviço de transcrições inicializado")
    
    def get_transcript(self, video_id: str) -> Optional[str]:
        """
        Obtém a transcrição completa de um vídeo.
        
        Args:
            video_id: ID do vídeo no YouTube
            
        Returns:
            Transcrição completa como string ou None se indisponível
        """
        logger.info(f"Buscando transcrição para vídeo {video_id}")
        
        try:
            # Tentar obter transcrição nos idiomas preferidos
            transcript = self._fetch_transcript(video_id)
            
            if transcript:
                full_text = self._format_transcript(transcript)
                logger.info(
                    f"Transcrição obtida com sucesso ({len(full_text)} caracteres)"
                )
                return full_text
            
            return None
            
        except TranscriptsDisabled:
            logger.warning(f"Transcrições desabilitadas para vídeo {video_id}")
            return None
        
        except NoTranscriptFound:
            logger.warning(
                f"Nenhuma transcrição encontrada para vídeo {video_id} "
                f"nos idiomas: {self.languages}"
            )
            return None
        
        except VideoUnavailable:
            logger.error(f"Vídeo {video_id} indisponível")
            return None
        
        except Exception as e:
            logger.error(f"Erro ao obter transcrição: {e}", exc_info=True)
            return None
    
    def _fetch_transcript(self, video_id: str) -> Optional[List[dict]]:
        """
        Busca transcrição com fallback por idiomas.
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            Lista de segmentos (objetos ou dicts) ou None
        """
        try:
            transcript_list = self.api.list(video_id)
            
            # 1. Tentar idiomas específicos (Manual primeiro, depois Automática)
            for lang in self.languages:
                # Tentar manual
                try:
                    transcript = transcript_list.find_manually_created_transcript([lang])
                    logger.info(f"Transcrição manual encontrada em {lang}")
                    return transcript.fetch()
                except NoTranscriptFound:
                    pass
                except Exception as e:
                    logger.warning(f"Erro ao buscar transcrição manual em {lang}: {e}")

                # Tentar automática (se habilitado)
                if self.fallback_enabled:
                    try:
                        transcript = transcript_list.find_generated_transcript([lang])
                        logger.info(f"Transcrição automática encontrada em {lang}")
                        return transcript.fetch()
                    except NoTranscriptFound:
                        pass
                    except Exception as e:
                        logger.warning(f"Erro ao buscar transcrição automática em {lang}: {e}")
            
            # 2. Última tentativa: qualquer transcrição disponível nos idiomas preferidos
            if self.fallback_enabled:
                try:
                    transcript = transcript_list.find_transcript(self.languages)
                    logger.info("Tentando transcrição disponível (fallback de idiomas)")
                    return transcript.fetch()
                except NoTranscriptFound:
                    pass
                except Exception as e:
                    logger.warning(f"Erro no fallback de idiomas: {e}")
            
            # 3. Se tudo falhar, mas houver QUALQUER transcrição, tentar a primeira disponível
            if self.fallback_enabled:
                try:
                    # Pegar a primeira da lista
                    for transcript in transcript_list:
                        logger.info(f"Tentando última alternativa: {transcript.language_code}")
                        try:
                            return transcript.fetch()
                        except Exception as e:
                            logger.warning(f"Falha ao buscar {transcript.language_code}: {e}")
                            continue
                except Exception:
                    pass
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao listar transcrições para {video_id}: {e}")
            return None
    
    def _format_transcript(self, transcript: List[dict]) -> str:
        """
        Formata segmentos da transcrição em texto contínuo.
        
        Args:
            transcript: Lista de segmentos da transcrição
            
        Returns:
            Texto formatado
        """
        if not transcript:
            return ""
        
        # Concatenar todos os textos (suporta tanto dicts quanto objetos FetchedTranscriptSnippet)
        texts = []
        for segment in transcript:
            if hasattr(segment, "text"):
                texts.append(segment.text)
            elif isinstance(segment, dict) and "text" in segment:
                texts.append(segment["text"])
            else:
                texts.append(str(segment))
                
        full_text = " ".join(texts)
        
        # Limpar espaços extras
        full_text = " ".join(full_text.split())
        
        return full_text
    
    def is_available(self, video_id: str) -> bool:
        """
        Verifica se transcrição está disponível para um vídeo.
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            True se transcrição disponível, False caso contrário
        """
        try:
            self.api.list(video_id)
            return True
        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar disponibilidade: {e}")
            return False
    
    def get_available_languages(self, video_id: str) -> List[str]:
        """
        Obtém lista de idiomas de transcrição disponíveis.
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            Lista de códigos de idioma
        """
        try:
            transcript_list = self.api.list(video_id)
            
            languages = []
            for transcript in transcript_list:
                languages.append(transcript.language_code)
            
            logger.debug(f"Idiomas disponíveis: {languages}")
            return languages
            
        except Exception as e:
            logger.error(f"Erro ao listar idiomas: {e}")
            return []
