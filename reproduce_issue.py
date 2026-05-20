
import sys
import os

# Adicionar o diretório raiz ao path para importar src
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from youtube_transcript_api import YouTubeTranscriptApi
from src.transcript_service import TranscriptService

def test_raw_api(video_id, f):
    f.write(f"--- Testando raw API para {video_id} ---\n")
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        for t in transcript_list:
            f.write(f"- Language: {t.language} ({t.language_code}), Generated: {t.is_generated}\n")
            try:
                data = t.fetch()
                f.write(f"  √ Fetch sucesso! ({len(data)} segmentos)\n")
            except Exception as e:
                f.write(f"  X Fetch falhou: {type(e).__name__}: {e}\n")
    except Exception as e:
        f.write(f"Erro na raw API para {video_id}: {type(e).__name__}: {e}\n")

if __name__ == "__main__":
    video_ids = ["BxRUXiV57qo", "qMtcWqzGe8M"] # Blinding Lights and a random one
    with open("repro_output_utf8.txt", "w", encoding="utf-8") as f:
        for vid in video_ids:
            test_raw_api(vid, f)
    print("Reproduction complete. Results in repro_output_utf8.txt")
