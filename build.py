import os
import shutil
import PyInstaller.__main__
from pathlib import Path

def build_exe():
    print("Iniciando build do YouTube Data Extractor Pro...")
    
    # 1. Limpar builds anteriores
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Pasta {folder} limpa.")

    # 2. Configurar caminhos
    base_dir = Path(__file__).parent.resolve()
    icon_path = base_dir / "assets" / "app.ico"
    
    # Verificar ícone
    if not icon_path.exists():
        print("Icone nao encontrado, usando padrao.")
        icon_option = []
    else:
        icon_option = [f"--icon={str(icon_path)}"]

    # 3. Executar PyInstaller
    print("Empacotando aplicacao...")
    
    args = [
        "main.py",                      # Script principal
        "--name=YouTubeExtractor",      # Nome do executável
        "--onefile",                    # Arquivo único
        "--noconsole",                  # Sem console (GUI app)
        "--clean",                      # Limpar cache
        "--collect-all=customtkinter",  # Incluir tudo do customtkinter
        "--hidden-import=customtkinter", # Forçar import
        *icon_option,                   # Ícone
        # Incluir pacotes ocultos necessários
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=rich",
        # Incluir pastas de código fonte
        f"--add-data=src{os.pathsep}src",
        f"--add-data=assets{os.pathsep}assets",
        # Otimizações
        "--noupx",
    ]
    
    PyInstaller.__main__.run(args)
    
    print("\nBuild concluido com sucesso!")
    print(f"Executavel em: {base_dir / 'dist' / 'YouTubeExtractor.exe'}")

if __name__ == "__main__":
    build_exe()
