"""
Exemplo de uso do YouTube Data Extractor

Demonstra como usar a aplicação tanto via CLI quanto como biblioteca.
"""

from main import get_video_data
from utils.exporters import DataExporter


def exemplo_como_biblioteca():
    """
    Demonstra uso da função get_video_data como biblioteca Python.
    """
    print("=" * 60)
    print("EXEMPLO: Uso como Biblioteca Python")
    print("=" * 60)
    
    # URLs de exemplo (substitua por URLs reais para testar)
    exemplos = [
        "https://youtube.com/watch?v=dQw4w9WgXcQ",  # Vídeo padrão
        "https://youtu.be/dQw4w9WgXcQ",             # URL curta
        "https://youtube.com/shorts/abc123",        # Short
        "dQw4w9WgXcQ"                               # Apenas ID
    ]
    
    # Usar a primeira URL como exemplo
    url = exemplos[0]
    
    try:
        print(f"\nExtraindo dados de: {url}\n")
        
        # Chamar função principal
        dados = get_video_data(url)
        
        # Exibir resultados
        print(f"✓ Título: {dados['title']}")
        print(f"✓ Descrição: {dados['description'][:100]}...")
        print(f"✓ Hashtags: {', '.join(dados['hashtags']) if dados['hashtags'] else 'Nenhuma'}")
        print(f"✓ Transcrição: {'Disponível' if dados['transcript'] else 'Não disponível'}")
        print(f"✓ Comentários: {len(dados['recent_comments'])} encontrados")
        
        # Exportar para arquivo
        exporter = DataExporter()
        filename = exporter.generate_filename("exemplo", "json")
        exporter.to_simple_json(dados, filename)
        
        print(f"\n✓ Dados salvos em: {filename}")
        
    except Exception as e:
        print(f"\n✗ Erro: {str(e)}")


def exemplo_cli():
    """
    Demonstra uso via linha de comando.
    """
    print("\n" + "=" * 60)
    print("EXEMPLO: Uso via CLI")
    print("=" * 60)
    
    exemplos_cli = [
        {
            "descricao": "Extração básica (JSON)",
            "comando": 'python main.py --url "https://youtube.com/watch?v=VIDEO_ID"'
        },
        {
            "descricao": "Extração simplificada",
            "comando": 'python main.py --url "VIDEO_ID" --simple'
        },
        {
            "descricao": "Exportação para CSV",
            "comando": 'python main.py --url "URL_DO_VIDEO" --output csv --file dados.csv'
        },
        {
            "descricao": "Exportação para ambos formatos",
            "comando": 'python main.py --url "https://youtube.com/shorts/SHORT_ID" --output both'
        },
        {
            "descricao": "Salvar em arquivo específico",
            "comando": 'python main.py --url "VIDEO_ID" --output json --file /caminho/personalizado/resultado.json'
        }
    ]
    
    for i, exemplo in enumerate(exemplos_cli, 1):
        print(f"\n{i}. {exemplo['descricao']}:")
        print(f"   {exemplo['comando']}")


if __name__ == "__main__":
    print("\nYouTube Video Data Extractor - Exemplos de Uso\n")
    
    # Descomentar para testar (requer URL de vídeo válida e API configurada)
    # exemplo_como_biblioteca()
    
    # Exemplos de CLI (sempre seguro de executar)
    exemplo_cli()
    
    print("\n" + "=" * 60)
    print("Para mais informacoes, consulte o README.md")
    print("=" * 60 + "\n")
