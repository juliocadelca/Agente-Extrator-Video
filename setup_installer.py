import os
import sys
import shutil
import winshell
from win32com.client import Dispatch

def create_shortcut(target, shortcut_path, icon_path=None):
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.TargetPath = target
    shortcut.WorkingDirectory = os.path.dirname(target)
    if icon_path and os.path.exists(icon_path):
        shortcut.IconLocation = icon_path
    shortcut.save()
    print(f"Atalho criado: {shortcut_path}")

def install():
    print("Iniciando instalacao do YouTube Data Extractor Pro...")
    
    # Caminhos
    base_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(base_dir, "dist", "YouTubeExtractor.exe")
    icon_path = os.path.join(base_dir, "assets", "app.ico")
    
    if not os.path.exists(exe_path):
        print("ERRO: Executavel nao encontrado em dist/. Rode 'python build.py' primeiro.")
        return

    # Destino de Instalação (AppData/Local/Programs)
    app_data = os.getenv('LOCALAPPDATA')
    install_dir = os.path.join(app_data, "Programs", "YouTubeExtractor")
    
    if not os.path.exists(install_dir):
        os.makedirs(install_dir)
        
    dest_exe = os.path.join(install_dir, "YouTubeExtractor.exe")
    dest_icon = os.path.join(install_dir, "app.ico")
    
    # Copiar arquivos
    print(f"Copiando arquivos para {install_dir}...")
    shutil.copy2(exe_path, dest_exe)
    if os.path.exists(icon_path):
        shutil.copy2(icon_path, dest_icon)
        
    # Criar Atalhos
    desktop = winshell.desktop()
    start_menu = winshell.programs()
    
    # Atalho Desktop
    create_shortcut(
        dest_exe, 
        os.path.join(desktop, "YouTube Extractor Pro.lnk"),
        dest_icon
    )
    
    # Atalho Menu Iniciar
    create_shortcut(
        dest_exe, 
        os.path.join(start_menu, "YouTube Extractor Pro.lnk"),
        dest_icon
    )
    
    print("\nInstalacao concluida com sucesso!")
    print("Voce pode iniciar o aplicativo pelo atalho na Area de Trabalho.")

if __name__ == "__main__":
    try:
        install()
    except Exception as e:
        print(f"Erro na instalacao: {e}")
        input("Pressione Enter para sair...")
