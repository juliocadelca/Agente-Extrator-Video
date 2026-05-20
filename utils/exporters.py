"""
Exportadores de dados para diferentes formatos.

Suporta exportação em JSON e CSV.
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

import pandas as pd

from src.data_models import VideoData, Comment
from utils.logger import logger


class ExportError(Exception):
    """Erro durante exportação de dados."""
    pass


class DataExporter:
    """Exportador de dados para múltiplos formatos."""
    
    @staticmethod
    def to_json(
        data: VideoData,
        filepath: str = None,
        indent: int = 2
    ) -> str:
        """
        Exporta dados para JSON.
        
        Args:
            data: Dados do vídeo
            filepath: Caminho para salvar (opcional)
            indent: Indentação do JSON
            
        Returns:
            String JSON
        """
        try:
            # Converter para dict
            data_dict = data.model_dump(mode="json")
            
            # Gerar JSON
            json_str = json.dumps(data_dict, ensure_ascii=False, indent=indent)
            
            # Salvar em arquivo se especificado
            if filepath:
                output_path = Path(filepath)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(json_str)
                
                logger.info(f"Dados exportados para JSON: {filepath}")
            
            return json_str
            
        except Exception as e:
            logger.error(f"Erro ao exportar para JSON: {e}", exc_info=True)
            raise ExportError(f"Falha na exportação JSON: {str(e)}")
    
    @staticmethod
    def to_simple_json(
        data: VideoData,
        filepath: str = None,
        indent: int = 2
    ) -> str:
        """
        Exporta dados no formato JSON simplificado (conforme requisitos).
        
        Args:
            data: Dados do vídeo
            filepath: Caminho para salvar (opcional)
            indent: Indentação do JSON
            
        Returns:
            String JSON
        """
        try:
            # Usar método to_simple_dict do modelo
            simple_dict = data.to_simple_dict()
            
            # Gerar JSON
            json_str = json.dumps(simple_dict, ensure_ascii=False, indent=indent)
            
            # Salvar em arquivo se especificado
            if filepath:
                output_path = Path(filepath)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(json_str)
                
                logger.info(f"Dados exportados para JSON simplificado: {filepath}")
            
            return json_str
            
        except Exception as e:
            logger.error(f"Erro ao exportar para JSON simplificado: {e}", exc_info=True)
            raise ExportError(f"Falha na exportação JSON: {str(e)}")
    
    @staticmethod
    def to_csv(data: VideoData, filepath: str) -> None:
        """
        Exporta dados para CSV.
        
        Args:
            data: Dados do vídeo
            filepath: Caminho para salvar
        """
        try:
            output_path = Path(filepath)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Preparar dados para CSV
            rows = []
            
            # Informações do vídeo
            video_info = {
                "tipo": "video",
                "video_id": data.video_id,
                "titulo": data.title,
                "descricao": data.description,
                "canal": data.channel_title or "",
                "publicado_em": data.published_at or "",
                "duracao": data.duration or "",
                "visualizacoes": data.view_count or 0,
                "likes": data.like_count or 0,
                "comentarios_total": data.comment_count or 0,
                "transcricao_disponivel": data.transcript_available,
                "comentarios_habilitados": data.comments_enabled,
                "extracao_em": data.extraction_timestamp,
                "conteudo": ""
            }
            rows.append(video_info)
            
            # Hashtags
            for tag in data.hashtags:
                rows.append({
                    "tipo": "hashtag",
                    "video_id": data.video_id,
                    "titulo": "",
                    "descricao": "",
                    "canal": "",
                    "publicado_em": "",
                    "duracao": "",
                    "visualizacoes": "",
                    "likes": "",
                    "comentarios_total": "",
                    "transcricao_disponivel": "",
                    "comentarios_habilitados": "",
                    "extracao_em": "",
                    "conteudo": tag
                })
            
            # Transcrição
            if data.transcript:
                rows.append({
                    "tipo": "transcricao",
                    "video_id": data.video_id,
                    "titulo": "",
                    "descricao": "",
                    "canal": "",
                    "publicado_em": "",
                    "duracao": "",
                    "visualizacoes": "",
                    "likes": "",
                    "comentarios_total": "",
                    "transcricao_disponivel": "",
                    "comentarios_habilitados": "",
                    "extracao_em": "",
                    "conteudo": data.transcript
                })
            
            # Comentários e Respostas
            for comment in data.recent_comments:
                rows.append({
                    "tipo": "comentario",
                    "video_id": data.video_id,
                    "titulo": "",
                    "descricao": "",
                    "canal": "",
                    "publicado_em": comment.published_at,
                    "duracao": "",
                    "visualizacoes": "",
                    "likes": comment.likes,
                    "comentarios_total": "",
                    "transcricao_disponivel": "",
                    "comentarios_habilitados": "",
                    "extracao_em": "",
                    "conteudo": f"{comment.author}: {comment.text}"
                })
                
                # Respostas
                for reply in comment.replies:
                    rows.append({
                        "tipo": "resposta",
                        "video_id": data.video_id,
                        "titulo": "",
                        "descricao": "",
                        "canal": "",
                        "publicado_em": reply.published_at,
                        "duracao": "",
                        "visualizacoes": "",
                        "likes": reply.likes,
                        "comentarios_total": "",
                        "transcricao_disponivel": "",
                        "comentarios_habilitados": "",
                        "extracao_em": "",
                        "conteudo": f"   ⤷ {reply.author}: {reply.text}"
                    })
            
            # Criar DataFrame e salvar
            df = pd.DataFrame(rows)
            df.to_csv(output_path, index=False, encoding="utf-8-sig")
            
            logger.info(f"Dados exportados para CSV: {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao exportar para CSV: {e}", exc_info=True)
            raise ExportError(f"Falha na exportação CSV: {str(e)}")
    
    @staticmethod
    def generate_filename(video_id: str, format: str = "json") -> str:
        """
        Gera nome de arquivo padrão.
        
        Args:
            video_id: ID do vídeo
            format: Formato do arquivo (json ou csv)
            
        Returns:
            Nome do arquivo
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"youtube_{video_id}_{timestamp}.{format}"
