# YouTube Downloader Pro - Versão Simplificada

Uma interface gráfica para baixar vídeos e playlists do YouTube, com suporte a transcrição automática de áudio usando Whisper.  
**Não requer MoviePy** — utiliza apenas `yt-dlp` e `whisper`.

## Funcionalidades

- Baixe vídeos ou playlists do YouTube em várias qualidades e formatos.
- Baixe apenas o áudio, se desejar.
- Transcreva automaticamente o áudio usando Whisper (opcional).
- Suporte a legendas automáticas.
- Interface gráfica amigável em Tkinter.
- Botão para instalar o FFmpeg automaticamente (Linux/Mac).

## Requisitos

- Python 3.7+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [openai-whisper](https://github.com/openai/whisper)
- FFmpeg (necessário para juntar vídeo e áudio e converter formatos)

## Instalação

1. **Clone este repositório:**
   ```bash
   git clone https://github.com/seuusuario/BAIXADORDEVIDEOS.git
   cd BAIXADORDEVIDEOS
   ```

2. **Instale as dependências Python:**
   ```bash
   pip install yt-dlp openai-whisper
   ```

3. **Instale o FFmpeg:**
   - **Linux (Ubuntu/Debian):**
     ```bash
     sudo apt update
     sudo apt install ffmpeg
     ```
   - **MacOS (Homebrew):**
     ```bash
     brew install ffmpeg
     ```
   - **Windows:**  
     Baixe manualmente em: https://ffmpeg.org/download.html

Ou utilize o botão "Instalar FFmpeg" na interface (Linux/Mac).

## Como usar

1. Execute o programa:
   ```bash
   python3 youtube_downloader_pro.py
   ```
2. Cole a URL do vídeo ou playlist.
3. Escolha a qualidade, formato e opções desejadas.
4. Clique em **BAIXAR**.
5. (Opcional) Clique em **Instalar FFmpeg** se necessário.

## Observações

- Para transcrição, marque "Apenas Áudio" para garantir que o áudio será extraído.
- O download de vídeos em alta qualidade requer o FFmpeg instalado.
- O programa salva os arquivos baixados na pasta escolhida, organizando por data/hora.

## Licença

MIT

---
Desenvolvido por [Seu Nome]
