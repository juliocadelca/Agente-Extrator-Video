"""
YouTube Video Data Extractor - CLI Principal

Aplicação profissional para extração de dados de vídeos do YouTube.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import settings
from src.url_parser import URLParser
from src.youtube_client import YouTubeClient, YouTubeAPIError
from src.transcript_service import TranscriptService
from src.comments_service import CommentsService
from src.data_models import VideoData, Comment
from utils.logger import logger, log_extraction_start, log_extraction_success, log_extraction_error
from utils.exporters import DataExporter, ExportError


console = Console()


def get_video_data(url: str, max_comments: Optional[int] = None, include_replies: bool = False) -> dict:
    """
    Função principal para extração de dados de vídeo do YouTube.
    
    Esta é a interface pública da aplicação conforme especificado
    nos requisitos.
    
    Args:
        url: URL completa do vídeo ou ID do vídeo
        
    Returns:
        Dicionário com dados do vídeo no formato simplificado
        
    Raises:
        ValueError: Se URL/ID inválido
        YouTubeAPIError: Se houver erro na API
    """
    # Extrair e validar ID do vídeo
    video_id = URLParser.extract_video_id(url)
    
    if not video_id:
        raise ValueError(f"URL ou ID inválido: {url}")
    
    log_extraction_start(video_id)
    
    # Inicializar serviços
    youtube_client = YouTubeClient()
    transcript_service = TranscriptService()
    comments_service = CommentsService(youtube_client)
    
    components_status = {
        "metadata": False,
        "transcript": False,
        "comments": False
    }
    
    try:
        # 1. Obter metadados do vídeo
        console.print(f"[cyan]Extraindo metadados do vídeo {video_id}...[/cyan]")
        video_details = youtube_client.get_video_details(video_id)
        
        snippet = video_details["snippet"]
        statistics = video_details.get("statistics", {})
        content_details = video_details.get("contentDetails", {})
        
        # Extrair hashtags
        description = snippet.get("description", "")
        hashtags = youtube_client.extract_hashtags(description)
        
        components_status["metadata"] = True
        
        # 2. Obter transcrição
        console.print(f"[cyan]Buscando transcrição...[/cyan]")
        transcript = None
        transcript_available = False
        
        try:
            transcript = transcript_service.get_transcript(video_id)
            transcript_available = transcript is not None
            components_status["transcript"] = True
            
            if transcript:
                console.print("[green]✓[/green] Transcrição obtida")
            else:
                console.print("[yellow]⚠[/yellow] Transcrição não disponível")
                
        except Exception as e:
            log_extraction_error(video_id, e, "transcript")
            console.print(f"[yellow]⚠[/yellow] Erro ao obter transcrição: {str(e)}")
        
        # 3. Obter comentários
        console.print(f"[cyan]Buscando comentários...[/cyan]")
        comments = []
        comments_enabled = True
        
        try:
            comments = comments_service.get_recent_comments(
                video_id, 
                max_results=max_comments,
                include_replies=include_replies
            )
            components_status["comments"] = True
            
            if comments:
                console.print(f"[green]✓[/green] {len(comments)} comentários obtidos")
            else:
                console.print("[yellow]⚠[/yellow] Nenhum comentário disponível")
                comments_enabled = False
                
        except Exception as e:
            log_extraction_error(video_id, e, "comments")
            console.print(f"[yellow]⚠[/yellow] Erro ao obter comentários: {str(e)}")
            comments_enabled = False
        
        # 4. Montar objeto VideoData
        video_data = VideoData(
            video_id=video_id,
            title=snippet.get("title", ""),
            description=description,
            hashtags=hashtags,
            transcript=transcript,
            recent_comments=comments,
            channel_title=snippet.get("channelTitle"),
            published_at=snippet.get("publishedAt"),
            duration=content_details.get("duration"),
            view_count=int(statistics.get("viewCount", 0)),
            like_count=int(statistics.get("likeCount", 0)),
            comment_count=int(statistics.get("commentCount", 0)),
            transcript_available=transcript_available,
            comments_enabled=comments_enabled
        )
        
        log_extraction_success(video_id, components_status)
        
        # Retornar formato simplificado conforme requisitos
        return video_data.to_simple_dict()
        
    except YouTubeAPIError as e:
        log_extraction_error(video_id, e, "youtube_api")
        raise
    
    except Exception as e:
        log_extraction_error(video_id, e, "general")
        raise


def main():
    """Função principal da CLI."""
    
    # Se nenhum argumento for passado, iniciar GUI
    if len(sys.argv) == 1:
        try:
            from src.gui import run_app
            run_app()
        except ImportError as e:
            print(f"Erro ao iniciar GUI: {e}")
            print("Certifique-se de instalar as dependências: pip install customtkinter pillow")
        return

    # Modo CLI (Argumentos presentes)
    parser = argparse.ArgumentParser(
        description="YouTube Video Data Extractor - Extraia metadados, transcrições e comentários de vídeos do YouTube.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--url", "-u",
        type=str,
        required=True,
        help="URL ou ID do vídeo do YouTube (suporta Shorts)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        choices=["json", "csv", "both"],
        default="json",
        help="Formato de saída (padrão: json)"
    )
    
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Nome do arquivo de saída (opcional)"
    )
    
    parser.add_argument(
        "--simple", "-s",
        action="store_true",
        help="Gera JSON simplificado com apenas campos essenciais"
    )
    
    parser.add_argument(
        "--comments", "-c",
        type=int,
        default=settings.max_comments,
        help=f"Número máximo de comentários a extrair (padrão: {settings.max_comments})"
    )
    parser.add_argument(
        "--replies", "-r",
        action="store_true",
        help="Extrair até 5 respostas mais recentes por comentário"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="YouTube Data Extractor v1.0.0"
    )
    
    args = parser.parse_args()
    
    # console = Console() # Already initialized globally
    
    # Validação inicial
    if not settings.validate_api_key():
        console.print(Panel(
            "[bold red]ERRO: API Key não configurada![/bold red]\n"
            "Configure a variável YOUTUBE_API_KEY no arquivo .env",
            title="Erro de Configuração",
            border_style="red"
        ))
        sys.exit(1)

    try:
        with console.status("[bold green]Processando...", spinner="dots"):
            # 1. Validar e Extrair ID
            video_id = URLParser.extract_video_id(args.url)
            if not video_id:
                raise ValueError(f"URL ou ID inválido: {args.url}")
            console.print(f"[cyan]ℹ Vídeo identificado:[/cyan] [bold]{video_id}[/bold]")
            
            # 2. Inicializar Clientes
            yt_client = YouTubeClient()
            transcript_service = TranscriptService()
            comments_service = CommentsService(yt_client) # Pass yt_client to comments_service
            
            # 3. Obter Metadados
            console.print("[cyan]⏳ Obtendo metadados...[/cyan]")
            video_details = yt_client.get_video_details(video_id)
            if not video_details:
                raise YouTubeAPIError(f"Vídeo {video_id} não encontrado ou privado.")
                
            snippet = video_details.get("snippet", {})
            statistics = video_details.get("statistics", {})
            content_details = video_details.get("contentDetails", {})
            
            # 4. Obter Transcrição
            console.print("[cyan]📝 Buscando transcrição...[/cyan]")
            transcript = transcript_service.get_transcript(video_id)
            if transcript:
                console.print("[green]✓ Transcrição obtida[/green]")
            else:
                console.print("[yellow]⚠ Transcrição indisponível[/yellow]")
                
            # 5. Obter Comentários
            console.print("[cyan]💬 Buscando comentários...[/cyan]")
            comments = comments_service.get_recent_comments(
                video_id, 
                max_results=args.comments,
                include_replies=args.replies
            )
            console.print(f"[green]✓ {len(comments)} comentários obtidos[/green]")
            
            # 6. Montar Objeto de Dados
            video_data = VideoData(
                video_id=video_id,
                title=snippet.get("title", ""),
                description=snippet.get("description", ""),
                channel_title=snippet.get("channelTitle", ""),
                published_at=snippet.get("publishedAt", ""),
                duration=content_details.get("duration", ""),
                view_count=int(statistics.get("viewCount", "0")),
                like_count=int(statistics.get("likeCount", "0")),
                comment_count=int(statistics.get("commentCount", "0")),
                hashtags=yt_client.extract_hashtags(snippet.get("description", "")), # Use yt_client for hashtags
                transcript=transcript,
                recent_comments=comments,
                transcript_available=transcript is not None, # Added for consistency
                comments_enabled=len(comments) > 0 # Added for consistency
            )
            
            # 7. Exportar
            exporter = DataExporter()
            
            # Determinar nome do arquivo
            if args.file:
                filename = args.file
                # Remover extensão se fornecida, pois o exporter adiciona
                if filename.lower().endswith(('.json', '.csv')):
                    filename = os.path.splitext(filename)[0]
            else:
                filename = exporter.generate_filename(video_id, "")
                
            saved_files = []
            
            # Lógica de exportação baseada nos argumentos
            if args.output in ["json", "both"]:
                if args.simple:
                    path = f"{filename}_simple.json"
                    exporter.to_simple_json(video_data, path)
                else:
                    path = f"{filename}.json"
                    exporter.to_json(video_data, path)
                saved_files.append(path)
                
            if args.output in ["csv", "both"]:
                path = f"{filename}.csv"
                exporter.to_csv(video_data, path)
                saved_files.append(path)
                
            # Exibir Resumo Final
            panel_content = (
                f"[bold]Título:[/bold] {video_data.title}\n"
                f"[bold]Canal:[/bold] {video_data.channel_title}\n"
                f"[bold]Duração:[/bold] {video_data.duration}\n"
                f"[bold]Visualizações:[/bold] {video_data.view_count:,}\n"
                f"[bold]Comentários Extraídos:[/bold] {len(video_data.recent_comments)}\n"
                f"[bold]Transcrição:[/bold] {'Sim' if video_data.transcript else 'Não'}\n\n"
                "[bold green]Arquivos Salvos:[/bold green]\n"
            )
            
            for f in saved_files:
                panel_content += f"📂 {f}\n"

            console.print(Panel(
                panel_content,
                title="Extração Concluída com Sucesso",
                border_style="green"
            ))

    except ValueError as e:
        console.print(f"[bold red]Erro de validação:[/bold red] {str(e)}")
        sys.exit(1)
    
    except YouTubeAPIError as e:
        logger.error(f"Erro na API do YouTube: {str(e)}")
        console.print(f"[bold red]Erro na API:[/bold red] {str(e)}")
        sys.exit(1)
            
    except ExportError as e:
        console.print(f"[bold red]Erro na exportação:[/bold red] {str(e)}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Operação cancelada pelo usuário[/yellow]")
        sys.exit(0)
    
    except Exception as e:
        console.print(f"[bold red]Erro inesperado:[/bold red] {str(e)}")
        logger.error("Erro fatal", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
