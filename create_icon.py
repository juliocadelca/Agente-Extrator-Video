from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Criar uma imagem base 256x256
    img = Image.new('RGBA', (256, 256), color=(255, 0, 0, 0)) # Transparente
    draw = ImageDraw.Draw(img)
    
    # Desenhar um círculo vermelho (estilo YouTube)
    draw.ellipse([28, 28, 228, 228], fill="#FF0000")
    
    # Desenhar o triângulo de "Play" branco
    draw.polygon([(100, 80), (100, 176), (180, 128)], fill="white")
    
    # Salvar como PNG e ICO
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        
    img.save(f"{assets_dir}/icon.png")
    img.save(f"{assets_dir}/app.ico", format="ICO", sizes=[(256, 256)])
    print("Icones criados em assets/")

if __name__ == "__main__":
    create_icon()
