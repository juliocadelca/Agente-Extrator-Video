"""
Cliente para YouTube Data API v3.

Gerencia autenticação e requisições à API do YouTube.
"""

from typing import Dict, Any, Optional
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.config import settings
from utils.logger import logger, log_api_call


class YouTubeAPIError(Exception):
    """Erro personalizado para problemas com a API do YouTube."""
    pass


class YouTubeClient:
    """Cliente para interação com YouTube Data API v3."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o cliente da YouTube API.
        
        Args:
            api_key: Chave da API (usa configuração se não fornecida)
        """
        self.api_key = api_key or settings.youtube_api_key
        
        if not self.api_key or self.api_key == "your_api_key_here":
            raise YouTubeAPIError(
                "Chave da API do YouTube não configurada. "
                "Configure YOUTUBE_API_KEY no arquivo .env"
            )
        
        self._youtube = None
        logger.info("Cliente YouTube API inicializado")
    
    @property
    def youtube(self):
        """Lazy loading do cliente da API."""
        if self._youtube is None:
            self._youtube = build("youtube", "v3", developerKey=self.api_key)
            logger.debug("Serviço YouTube API construído")
        return self._youtube
    
    def _execute_with_retry(
        self,
        request,
        max_retries: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Executa requisição com retry logic.
        
        Args:
            request: Requisição a ser executada
            max_retries: Número máximo de tentativas
            
        Returns:
            Resposta da API
            
        Raises:
            YouTubeAPIError: Em caso de erro irrecuperável
        """
        max_retries = max_retries or settings.max_retries
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                response = request.execute()
                return response
            
            except HttpError as e:
                last_exception = e
                status_code = e.resp.status
                
                # Erros fatais que não devem ser retentados
                if status_code in [400, 401, 403, 404]:
                    error_msg = self._parse_http_error(e)
                    logger.error(f"Erro HTTP fatal {status_code}: {error_msg}")
                    raise YouTubeAPIError(error_msg) from e
                
                # Erros temporários - retry
                if status_code in [429, 500, 503]:
                    wait_time = settings.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(
                        f"Erro HTTP {status_code}, tentativa {attempt + 1}/{max_retries}. "
                        f"Aguardando {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue
                
                # Erro desconhecido
                logger.error(f"Erro HTTP desconhecido {status_code}: {e}")
                raise YouTubeAPIError(f"Erro HTTP {status_code}") from e
            
            except Exception as e:
                logger.error(f"Erro inesperado na API: {e}", exc_info=True)
                raise YouTubeAPIError(f"Erro inesperado: {str(e)}") from e
        
        # Todas as tentativas falharam
        raise YouTubeAPIError(
            f"Falha após {max_retries} tentativas: {str(last_exception)}"
        )
    
    def _parse_http_error(self, error: HttpError) -> str:
        """
        Extrai mensagem de erro legível de HttpError.
        
        Args:
            error: Erro HTTP da API
            
        Returns:
            Mensagem de erro formatada
        """
        status = error.resp.status
        
        error_map = {
            400: "Requisição inválida - verifique o ID do vídeo",
            401: "Chave da API inválida ou não autorizada",
            403: "Acesso negado - verifique suas quotas e permissões",
            404: "Vídeo não encontrado ou foi removido",
            429: "Limite de requisições excedido - aguarde alguns segundos",
            500: "Erro interno do servidor YouTube",
            503: "Serviço temporariamente indisponível"
        }
        
        return error_map.get(status, f"Erro HTTP {status}")
    
    def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes completos de um vídeo.
        
        Args:
            video_id: ID do vídeo no YouTube
            
        Returns:
            Dados do vídeo
            
        Raises:
            YouTubeAPIError: Se houver erro na requisição
        """
        logger.info(f"Buscando detalhes do vídeo: {video_id}")
        
        params = {
            "part": "snippet,contentDetails,statistics,status",
            "id": video_id
        }
        
        log_api_call("videos", "list", params)
        
        request = self.youtube.videos().list(**params)
        response = self._execute_with_retry(request)
        
        if not response.get("items"):
            raise YouTubeAPIError(
                f"Vídeo {video_id} não encontrado ou não está acessível"
            )
        
        video_data = response["items"][0]
        logger.info(f"Dados do vídeo {video_id} obtidos com sucesso")
        
        return video_data
    
    def extract_hashtags(self, description: str) -> list:
        """
        Extrai hashtags da descrição do vídeo.
        
        Args:
            description: Descrição do vídeo
            
        Returns:
            Lista de hashtags (sem o símbolo #)
        """
        import re
        
        # Regex para capturar hashtags
        hashtag_pattern = r"#(\w+)"
        hashtags = re.findall(hashtag_pattern, description)
        
        logger.debug(f"Extraídas {len(hashtags)} hashtags")
        return hashtags
