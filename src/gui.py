import sys
import threading
import tkinter
from pathlib import Path
from typing import Optional, Callable
import os
import subprocess
import customtkinter as ctk
from PIL import Image

from .youtube_client import YouTubeClient
from .transcript_service import TranscriptService
from .comments_service import CommentsService
from .url_parser import URLParser
from .data_models import VideoData
from .config import settings
from utils.exporters import DataExporter
from utils.logger import logger

# Configurar aparência global
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class LogRedirector:
    """Redireciona stdout/stderr para o widget de texto da GUI."""
    def __init__(self, text_widget: ctk.CTkTextbox):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, text: str):
        self.buffer += text
        # Atualizar GUI na thread principal
        self.text_widget.after(0, self._update_widget)

    def _update_widget(self):
        if self.buffer:
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", self.buffer)
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")
            self.buffer = ""

    def flush(self):
        pass

class YoutubeExtractorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da Janela
        self.title("YouTube Data Extractor Pro")
        self.geometry("800x600")
        self.minsize(600, 500)
        
        # Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Área de log expande

        # Header
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.label_title = ctk.CTkLabel(
            self.header_frame, 
            text="YouTube Data Extractor", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.label_title.pack(pady=10)

        # Input Area
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.url_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Cole a URL do vídeo aqui (ex: https://youtu.be/...)",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.url_entry.pack(fill="x", padx=20, pady=(20, 10))
        
        # Opções
        self.options_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.options_frame.pack(fill="x", padx=20, pady=10)
        
        self.check_json = ctk.CTkCheckBox(self.options_frame, text="JSON Completo", onvalue=True, offvalue=False)
        self.check_json.select()
        self.check_json.pack(side="left", padx=10)
        
        self.check_simple = ctk.CTkCheckBox(self.options_frame, text="JSON Simplificado", onvalue=True, offvalue=False)
        self.check_simple.pack(side="left", padx=10)
        
        self.check_csv = ctk.CTkCheckBox(self.options_frame, text="CSV (Excel)", onvalue=True, offvalue=False)
        self.check_csv.pack(side="left", padx=10)
        
        self.check_replies = ctk.CTkCheckBox(self.options_frame, text="Extrair Respostas", onvalue=True, offvalue=False)
        self.check_replies.pack(side="left", padx=10)
        
        # Limite de Comentários
        self.label_comments = ctk.CTkLabel(self.options_frame, text="Limite de Comentários:")
        self.label_comments.pack(side="left", padx=(20, 5))
        
        self.comments_entry = ctk.CTkEntry(self.options_frame, width=60)
        self.comments_entry.insert(0, str(settings.max_comments))
        self.comments_entry.pack(side="left", padx=5)
        
        self.btn_extract = ctk.CTkButton(
            self.input_frame,
            text="EXTRAIR DADOS",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self.start_extraction_thread
        )
        self.btn_extract.pack(fill="x", padx=20, pady=10)

        # Seleção de Pasta
        self.dir_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.dir_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.dir_entry = ctk.CTkEntry(
            self.dir_frame, 
            placeholder_text="Pasta de destino",
            height=30,
            font=ctk.CTkFont(size=12)
        )
        # Caminho padrão: Downloads
        default_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.dir_entry.insert(0, default_dir)
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_browse = ctk.CTkButton(
            self.dir_frame,
            text="PROCURAR",
            width=100,
            height=30,
            command=self.browse_directory
        )
        self.btn_browse.pack(side="right")

        self.btn_open_folder = ctk.CTkButton(
            self.input_frame,
            text="ABRIR PASTA",
            font=ctk.CTkFont(size=12),
            height=30,
            fg_color="gray",
            state="disabled",
            command=self.open_output_folder
        )
        self.btn_open_folder.pack(fill="x", padx=20, pady=(0, 20))

        # Log Area
        self.log_textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_textbox.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.log_textbox.configure(state="disabled")
        
        # Footer
        self.footer_frame = ctk.CTkFrame(self, height=30)
        self.footer_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.status_label = ctk.CTkLabel(self.footer_frame, text="Pronto para extrair", text_color="gray")
        self.status_label.pack(side="left", padx=10)

        # Redirecionar logs
        self.redirector = LogRedirector(self.log_textbox)
        # Redirecionar print e logs do sistema
        
    def log(self, message: str):
        """Helper para logar na GUI."""
        self.redirector.write(f"{message}\n")
        # Também manter logging no arquivo via logger
        logger.info(message)

    def start_extraction_thread(self):
        """Inicia extração em thread separada para não travar a GUI."""
        url = self.url_entry.get().strip()
        if not url:
            self.log("❌ Erro: Por favor insira uma URL válida.")
            return

        self.btn_extract.configure(state="disabled", text="Extraindo...")
        self.status_label.configure(text="Processando...", text_color="orange")
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        
        threading.Thread(target=self.run_extraction, args=(url,), daemon=True).start()

    def browse_directory(self):
        """Abre seletor de diretório."""
        directory = tkinter.filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)

    def open_output_folder(self):
        """Abre a pasta selecionada no explorador de arquivos."""
        path = self.dir_entry.get().strip()
        if os.path.exists(path):
            os.startfile(path)
        else:
            self.log(f"⚠️ Erro: Pasta não encontrada: {path}")

    def run_extraction(self, url: str):
        try:
            # Usar pasta selecionada
            output_dir = self.dir_entry.get().strip()
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            self.log(f"📂 Diretório de saída: {output_dir}")
            self.log("🔄 Iniciando processo de extração...")
            
            # 1. Validar URL
            video_id = URLParser.extract_video_id(url)
            self.log(f"✅ Vídeo identificado: {video_id}")
            
            # 2. Inicializar Clientes
            yt_client = YouTubeClient()
            transcript_service = TranscriptService()
            comments_service = CommentsService(yt_client)
            
            # 3. Obter Metadados
            self.log("📡 Buscando metadados...")
            video_details = yt_client.get_video_details(video_id)
            if not video_details:
                self.log("❌ Erro: Vídeo não encontrado ou privado.")
                return

            # 4. Obter Transcrição
            self.log("📝 Buscando transcrição...")
            transcript = transcript_service.get_transcript(video_id)
            if transcript:
                self.log("✅ Transcrição obtida com sucesso.")
            else:
                self.log("⚠️ Transcrição indisponível.")

            # 5. Obter Comentários
            try:
                max_comments = int(self.comments_entry.get().strip())
            except ValueError:
                max_comments = settings.max_comments
                self.log(f"⚠️ Valor de limite inválido, usando padrão: {max_comments}")
            
            include_replies = self.check_replies.get()
            if include_replies:
                self.log("💬 Buscando comentários e respostas (até 5 por comentário)...")
            else:
                self.log("💬 Buscando comentários recentes...")
                
            comments = comments_service.get_recent_comments(
                video_id, 
                max_results=max_comments,
                include_replies=include_replies
            )
            self.log(f"✅ {len(comments)} comentários obtidos.")

            # Montar Objeto de Dados
            video_data = VideoData(
                video_id=video_id,
                title=video_details.get("snippet", {}).get("title", ""),
                description=video_details.get("snippet", {}).get("description", ""),
                channel_title=video_details.get("snippet", {}).get("channelTitle", ""),
                published_at=video_details.get("snippet", {}).get("publishedAt", ""),
                duration=video_details.get("contentDetails", {}).get("duration", ""),
                view_count=int(video_details.get("statistics", {}).get("viewCount", "0")),
                like_count=int(video_details.get("statistics", {}).get("likeCount", "0")),
                comment_count=int(video_details.get("statistics", {}).get("commentCount", "0")),
                hashtags=URLParser.extract_hashtags(video_details.get("snippet", {}).get("description", "")),
                transcript=transcript,
                recent_comments=comments
            )

            # 6. Exportar
            self.log("💾 Salvando arquivos...")
            exporter = DataExporter()
            base_filename = exporter.generate_filename(video_id, "")
            
            saved_files = []
            
            if self.check_json.get():
                filename = f"{base_filename}.json"
                path = os.path.join(output_dir, filename)
                exporter.to_json(video_data, path)
                saved_files.append(filename)
                
            if self.check_simple.get():
                filename = f"{base_filename}_simple.json"
                path = os.path.join(output_dir, filename)
                exporter.to_simple_json(video_data, path)
                saved_files.append(filename)
                
            if self.check_csv.get():
                filename = f"{base_filename}.csv"
                path = os.path.join(output_dir, filename)
                exporter.to_csv(video_data, path)
                saved_files.append(filename)
                
            self.log("\n✨ SUCESSO! Arquivos salvos:")
            for f in saved_files:
                self.log(f"   📂 {f}")
                
            self.after(0, lambda: self.status_label.configure(text="Concluído com sucesso!", text_color="green"))
            self.after(0, lambda: self.btn_open_folder.configure(state="normal", fg_color="#1f538d"))

        except Exception as e:
            self.log(f"\n❌ ERRO CRÍTICO: {str(e)}")
            self.after(0, lambda: self.status_label.configure(text="Erro na extração", text_color="red"))
        finally:
            self.after(0, lambda: self.btn_extract.configure(state="normal", text="EXTRAIR DADOS"))


def run_app():
    app = YoutubeExtractorGUI()
    app.mainloop()

if __name__ == "__main__":
    run_app()
