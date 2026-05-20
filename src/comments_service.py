"""
Serviço de extração de comentários.

Gerencia a obtenção de comentários de vídeos do YouTube.
"""

from typing import List, Dict, Any
from datetime import datetime

from src.youtube_client import YouTubeClient, YouTubeAPIError
from src.data_models import Comment
from src.config import settings
from utils.logger import logger, log_api_call


class CommentsService:
    """Serviço para extração de comentários."""
    
    def __init__(self, youtube_client: YouTubeClient):
        """
        Inicializa o serviço de comentários.
        
        Args:
            youtube_client: Cliente da YouTube API
        """
        self.client = youtube_client
        logger.info("Serviço de comentários inicializado")
    
    def get_recent_comments(
        self,
        video_id: str,
        max_results: int = None,
        include_replies: bool = False
    ) -> List[Comment]:
        """
        Obtém os comentários mais recentes de um vídeo.
        
        Args:
            video_id: ID do vídeo
            max_results: Número máximo de comentários (default: 15)
            
        Returns:
            Lista de comentários ordenados por data
            
        Raises:
            YouTubeAPIError: Se houver erro na requisição
        """
        max_results = max_results or settings.max_comments
        
        logger.info(f"Buscando até {max_results} comentários para vídeo {video_id}")
        
        try:
            params = {
                "part": "snippet,replies" if include_replies else "snippet",
                "videoId": video_id,
                "maxResults": max_results,
                "order": "time",  # Ordenar por data (mais recentes primeiro)
                "textFormat": "plainText"
            }
            
            log_api_call("commentThreads", "list", params)
            
            request = self.client.youtube.commentThreads().list(**params)
            response = self.client._execute_with_retry(request)
            
            comments = self._parse_comments(response, include_replies=include_replies)
            
            logger.info(f"{len(comments)} comentários extraídos com sucesso")
            return comments
            
        except YouTubeAPIError as e:
            # Verificar se comentários estão desabilitados
            if "commentsDisabled" in str(e) or "disabled comments" in str(e).lower():
                logger.warning(f"Comentários desabilitados para vídeo {video_id}")
                return []
            
            # Outros erros
            logger.error(f"Erro ao buscar comentários: {e}")
            raise
    
    def _parse_comments(self, response: Dict[str, Any], include_replies: bool = False) -> List[Comment]:
        """
        Processa resposta da API e extrai comentários.
        
        Args:
            response: Resposta da API
            
        Returns:
            Lista de objetos Comment
        """
        comments = []
        
        for item in response.get("items", []):
            try:
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                
                comment = Comment(
                    author=snippet["authorDisplayName"],
                    text=snippet["textDisplay"],
                    published_at=snippet["publishedAt"],
                    likes=snippet.get("likeCount", 0)
                )
                
                # Processar respostas se incluídas
                if include_replies and "replies" in item:
                    replies_data = item["replies"].get("comments", [])
                    # Limitar a 5 respostas fixo conforme pedido
                    for reply_item in replies_data[:5]:
                        reply_snippet = reply_item["snippet"]
                        reply = Comment(
                            author=reply_snippet["authorDisplayName"],
                            text=reply_snippet["textDisplay"],
                            published_at=reply_snippet["publishedAt"],
                            likes=reply_snippet.get("likeCount", 0)
                        )
                        comment.replies.append(reply)
                
                comments.append(comment)
                
            except (KeyError, TypeError) as e:
                logger.warning(f"Erro ao processar comentário: {e}")
                continue
        
        return comments
    
    def check_comments_enabled(self, video_id: str) -> bool:
        """
        Verifica se comentários estão habilitados para um vídeo.
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            True se comentários estão habilitados, False caso contrário
        """
        try:
            # Tenta buscar apenas 1 comentário
            params = {
                "part": "snippet",
                "videoId": video_id,
                "maxResults": 1
            }
            
            request = self.client.youtube.commentThreads().list(**params)
            self.client._execute_with_retry(request)
            
            return True
            
        except YouTubeAPIError:
            return False
