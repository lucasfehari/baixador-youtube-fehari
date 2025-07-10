#!/usr/bin/env python3
"""
YouTube Video Downloader Pro - Versão Simplificada
Funciona sem MoviePy - Usa apenas yt-dlp e whisper
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import subprocess
from datetime import datetime
import re

# Imports básicos
try:
    import yt_dlp
except ImportError:
    print("Instalando yt-dlp...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

try:
    import whisper
except ImportError:
    print("Instalando whisper...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai-whisper"])
    import whisper

class YouTubeDownloaderSimple:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube Downloader Pro - Versão Simplificada")
        self.root.geometry("800x700")
        self.root.configure(bg='#2b2b2b')
        
        # Variáveis
        self.download_path = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.video_url = tk.StringVar()
        self.quality_var = tk.StringVar(value="best")
        self.format_var = tk.StringVar(value="mp4")
        self.transcribe_var = tk.BooleanVar(value=True)
        self.audio_only_var = tk.BooleanVar(value=False)
        self.playlist_var = tk.BooleanVar(value=False)
        
        # Modelo Whisper
        self.whisper_model = None
        
        self.setup_ui()
        self.center_window()
        
    def setup_ui(self):
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='white', background='#2b2b2b')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='white', background='#2b2b2b')
        style.configure('Custom.TButton', font=('Arial', 10, 'bold'))
        
        # Título principal
        title_label = ttk.Label(self.root, text="🎬 YouTube Downloader Pro", style='Title.TLabel')
        title_label.pack(pady=10)
        
        subtitle_label = ttk.Label(self.root, text="Versão Simplificada - Sem MoviePy", 
                                 font=('Arial', 10), foreground='#888888', background='#2b2b2b')
        subtitle_label.pack(pady=(0, 20))
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # URL Input
        url_frame = ttk.LabelFrame(main_frame, text="🔗 URL do Vídeo/Playlist", padding=10)
        url_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Entry(url_frame, textvariable=self.video_url, font=('Arial', 10), width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(url_frame, text="Info", command=self.get_video_info, style='Custom.TButton').pack(side=tk.RIGHT, padx=(10, 0))
        
        # Opções
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Configurações", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Linha 1 - Qualidade e Formato
        row1_frame = ttk.Frame(options_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(row1_frame, text="Qualidade:").pack(side=tk.LEFT)
        quality_combo = ttk.Combobox(row1_frame, textvariable=self.quality_var, width=15, state='readonly')
        quality_combo['values'] = ('best', 'worst', '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p')
        quality_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(row1_frame, text="Formato:").pack(side=tk.LEFT)
        format_combo = ttk.Combobox(row1_frame, textvariable=self.format_var, width=10, state='readonly')
        format_combo['values'] = ('mp4', 'webm', 'mkv', 'avi', 'mp3', 'wav', 'flac', 'm4a')
        format_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Linha 2 - Checkboxes
        row2_frame = ttk.Frame(options_frame)
        row2_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Checkbutton(row2_frame, text="🎵 Apenas Áudio", variable=self.audio_only_var).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Checkbutton(row2_frame, text="📝 Transcrever Automaticamente", variable=self.transcribe_var).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Checkbutton(row2_frame, text="📋 É Playlist", variable=self.playlist_var).pack(side=tk.LEFT)
        
        # Caminho de download
        path_frame = ttk.LabelFrame(main_frame, text="📁 Pasta de Download", padding=10)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Entry(path_frame, textvariable=self.download_path, font=('Arial', 10), width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="Procurar", command=self.browse_folder, style='Custom.TButton').pack(side=tk.RIGHT, padx=(10, 0))
        
        # Botões principais
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="🚀 BAIXAR", command=self.start_download, 
                  style='Custom.TButton', width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="🔄 Limpar", command=self.clear_log, 
                  style='Custom.TButton', width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="📂 Abrir Pasta", command=self.open_folder, 
                  style='Custom.TButton', width=15).pack(side=tk.LEFT)
        ttk.Button(buttons_frame, text="Instalar FFmpeg", command=self.install_ffmpeg, 
                  style='Custom.TButton', width=18).pack(side=tk.LEFT, padx=(10, 0))
        
        # Barra de progresso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Log de saída
        log_frame = ttk.LabelFrame(main_frame, text="📋 Log de Atividades", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, font=('Consolas', 9), 
                                                 bg='#1e1e1e', fg='#ffffff', insertbackground='white')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Pronto para download")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Mensagem inicial
        self.log_message("✅ YouTube Downloader Pro carregado com sucesso!")
        self.log_message("💡 Esta versão não precisa do MoviePy")
        self.log_message("🎤 Transcrição funciona apenas com arquivos de áudio")
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def log_message(self, message):
        """Adiciona mensagem ao log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path.set(folder)
            
    def open_folder(self):
        path = self.download_path.get()
        if os.path.exists(path):
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        else:
            messagebox.showerror("Erro", "Pasta não encontrada!")
            
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_var.set("Log limpo")
        
    def get_video_info(self):
        """Obtém informações do vídeo"""
        url = self.video_url.get().strip()
        if not url:
            messagebox.showerror("Erro", "Por favor, insira uma URL!")
            return
            
        def fetch_info():
            try:
                self.status_var.set("Obtendo informações do vídeo...")
                
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    if 'entries' in info:  # Playlist
                        self.log_message(f"🎬 PLAYLIST DETECTADA: {info.get('title', 'Sem título')}")
                        self.log_message(f"📊 Total de vídeos: {len(info['entries'])}")
                        self.log_message(f"📝 Descrição: {info.get('description', 'Sem descrição')[:100]}...")
                        
                        for i, entry in enumerate(info['entries'][:3]):  # Mostra apenas os 3 primeiros
                            duration = entry.get('duration', 0)
                            duration_str = f"{duration//60}:{duration%60:02d}" if duration else "N/A"
                            self.log_message(f"  {i+1}. {entry.get('title', 'Sem título')} ({duration_str})")
                            
                        if len(info['entries']) > 3:
                            self.log_message(f"  ... e mais {len(info['entries']) - 3} vídeos")
                            
                    else:  # Vídeo único
                        duration = info.get('duration', 0)
                        duration_str = f"{duration//60}:{duration%60:02d}" if duration else "N/A"
                        
                        self.log_message(f"🎬 TÍTULO: {info.get('title', 'Sem título')}")
                        self.log_message(f"👤 CANAL: {info.get('uploader', 'Desconhecido')}")
                        self.log_message(f"⏱️ DURAÇÃO: {duration_str}")
                        self.log_message(f"👁️ VISUALIZAÇÕES: {info.get('view_count', 'N/A'):,}")
                        self.log_message(f"📅 DATA: {info.get('upload_date', 'N/A')}")
                        self.log_message(f"📝 DESCRIÇÃO: {info.get('description', 'Sem descrição')[:200]}...")
                        
                        # Formatos disponíveis
                        formats = info.get('formats', [])
                        video_formats = [f for f in formats if f.get('vcodec') != 'none']
                        audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                        
                        self.log_message(f"🎥 FORMATOS DE VÍDEO: {len(video_formats)} disponíveis")
                        self.log_message(f"🎵 FORMATOS DE ÁUDIO: {len(audio_formats)} disponíveis")
                        
                        # Melhores qualidades disponíveis
                        best_video = max(video_formats, key=lambda x: x.get('height', 0), default=None)
                        if best_video:
                            self.log_message(f"🏆 MELHOR QUALIDADE: {best_video.get('height', 'N/A')}p - {best_video.get('ext', 'N/A')}")
                            
                self.status_var.set("Informações obtidas com sucesso!")
                
            except Exception as e:
                self.log_message(f"❌ ERRO ao obter informações: {str(e)}")
                self.status_var.set("Erro ao obter informações")
                
        threading.Thread(target=fetch_info, daemon=True).start()

    def progress_hook(self, d):
        """Hook para acompanhar progresso do download"""
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total and downloaded:
                percent = (downloaded / total) * 100
                self.progress_var.set(percent)
            else:
                self.progress_var.set(0)
            
            # Velocidade e ETA
            speed = d.get('speed', 0)
            eta = d.get('eta', 0)
            speed_str = f"{speed/1024/1024:.1f} MB/s" if speed else "N/A"
            eta_str = f"{eta}s" if eta else "N/A"
            
            self.status_var.set(f"Baixando: {self.progress_var.get():.1f}% | {speed_str} | ETA: {eta_str}")
            
        elif d['status'] == 'finished':
            self.progress_var.set(100)
            self.status_var.set("Download concluído!")
            
    def transcribe_audio(self, audio_path, output_path):
        """Transcreve áudio usando Whisper"""
        try:
            self.log_message("🎤 Iniciando transcrição com Whisper...")
            
            # Carrega modelo Whisper se não estiver carregado
            if self.whisper_model is None:
                self.log_message("📥 Carregando modelo Whisper (primeira vez pode demorar)...")
                self.whisper_model = whisper.load_model("base")
                
            # Transcreve
            result = self.whisper_model.transcribe(audio_path, language="pt")
            
            # Salva transcrição
            transcript_file = os.path.join(output_path, "transcricao.txt")
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write("=" * 50 + "\n")
                f.write("TRANSCRIÇÃO AUTOMÁTICA\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Arquivo: {os.path.basename(audio_path)}\n")
                f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Idioma detectado: {result.get('language', 'português')}\n")
                f.write("\n" + "=" * 50 + "\n")
                f.write("TEXTO COMPLETO:\n")
                f.write("=" * 50 + "\n\n")
                f.write(result["text"])
                f.write("\n\n" + "=" * 50 + "\n")
                f.write("SEGMENTOS COM TIMESTAMPS:\n")
                f.write("=" * 50 + "\n\n")
                
                for segment in result["segments"]:
                    start_time = segment["start"]
                    end_time = segment["end"]
                    text = segment["text"]
                    
                    start_str = f"{int(start_time//60):02d}:{int(start_time%60):02d}"
                    end_str = f"{int(end_time//60):02d}:{int(end_time%60):02d}"
                    
                    f.write(f"[{start_str} - {end_str}] {text}\n")
                    
            self.log_message(f"✅ Transcrição salva em: {transcript_file}")
            return transcript_file
            
        except Exception as e:
            self.log_message(f"❌ Erro na transcrição: {str(e)}")
            return None
            
    def start_download(self):
        """Inicia o processo de download"""
        url = self.video_url.get().strip()
        if not url:
            messagebox.showerror("Erro", "Por favor, insira uma URL!")
            return

        if not os.path.exists(self.download_path.get()):
            messagebox.showerror("Erro", "Pasta de download não existe!")
            return

        # Verifica se ffmpeg está instalado
        if not self.is_ffmpeg_installed():
            messagebox.showerror(
                "FFmpeg não encontrado",
                "O FFmpeg é necessário para juntar vídeo e áudio e converter para o formato final.\n"
                "Por favor, instale o FFmpeg antes de baixar vídeos.\n\n"
                "No Mac: brew install ffmpeg\nNo Ubuntu: sudo apt install ffmpeg\nNo Windows: https://ffmpeg.org/download.html"
            )
            return

        # Executa download em thread separada
        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def is_ffmpeg_installed(self):
        """Verifica se ffmpeg está disponível no sistema"""
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

    def download_video(self, url):
        """Executa o download do vídeo"""
        try:
            self.log_message("🚀 Iniciando download...")
            self.status_var.set("Preparando download...")
            
            # Cria pasta para o vídeo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_folder = os.path.join(self.download_path.get(), f"video_{timestamp}")
            os.makedirs(video_folder, exist_ok=True)
            
            # Configurações do yt-dlp
            quality = self.quality_var.get()
            format_ext = self.format_var.get()
            audio_only = self.audio_only_var.get()
            
            # Formato de saída
            if audio_only:
                format_selector = f"bestaudio/best"
                outtmpl = os.path.join(video_folder, f"%(title)s.%(ext)s")
                merge_output_format = format_ext
            else:
                if quality == "best":
                    # Melhor vídeo + melhor áudio, depois melhor disponível
                    format_selector = f"bestvideo+bestaudio/best"
                elif quality == "worst":
                    format_selector = f"worstvideo+worstaudio/worst"
                else:
                    # Exemplo: 1080p -> height<=1080
                    height = re.sub(r'\D', '', quality)
                    format_selector = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
                outtmpl = os.path.join(video_folder, f"%(title)s.%(ext)s")
                merge_output_format = format_ext

            ydl_opts = {
                'format': format_selector,
                'outtmpl': outtmpl,
                'progress_hooks': [self.progress_hook],
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['pt', 'en'],
                'ignoreerrors': True,
                'merge_output_format': merge_output_format,
            }
            
            # Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if self.playlist_var.get():
                    self.log_message("📋 Baixando playlist...")
                    ydl.download([url])
                else:
                    self.log_message("🎬 Baixando vídeo...")
                    ydl.download([url])
                    
            self.log_message("✅ Download concluído!")
            
            # Transcrição automática (apenas para áudio)
            if self.transcribe_var.get():
                self.log_message("🎤 Verificando arquivos de áudio para transcrição...")
                
                # Procura arquivos de áudio
                audio_files = []
                for file in os.listdir(video_folder):
                    if file.lower().endswith(('.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg')):
                        audio_files.append(file)
                
                if audio_files:
                    for audio_file in audio_files:
                        audio_path = os.path.join(video_folder, audio_file)
                        self.log_message(f"🎵 Transcrevendo: {audio_file}")
                        self.transcribe_audio(audio_path, video_folder)
                else:
                    self.log_message("⚠️  Nenhum arquivo de áudio encontrado para transcrição")
                    self.log_message("💡 Para transcrever vídeos, marque 'Apenas Áudio' ou use ffmpeg para extrair áudio")
                    
            # Salva informações do download
            info_file = os.path.join(video_folder, "info_download.txt")
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write("INFORMAÇÕES DO DOWNLOAD\n")
                f.write("=" * 30 + "\n\n")
                f.write(f"URL: {url}\n")
                f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Qualidade: {quality}\n")
                f.write(f"Formato: {format_ext}\n")
                f.write(f"Apenas áudio: {'Sim' if audio_only else 'Não'}\n")
                f.write(f"Transcrição: {'Sim' if self.transcribe_var.get() else 'Não'}\n")
                f.write(f"Playlist: {'Sim' if self.playlist_var.get() else 'Não'}\n")
                f.write(f"Versão: Simplificada (sem MoviePy)\n")
                
            self.log_message(f"📁 Arquivos salvos em: {video_folder}")
            self.status_var.set("Download e processamento concluídos!")
            
            # Notificação de sucesso
            messagebox.showinfo("Sucesso!", f"Download concluído!\nPasta: {video_folder}")
            
        except Exception as e:
            self.log_message(f"❌ ERRO no download: {str(e)}")
            self.status_var.set("Erro no download")
            messagebox.showerror("Erro", f"Erro no download: {str(e)}")
            
    def install_ffmpeg(self):
        """Instala o ffmpeg automaticamente conforme o sistema operacional"""
        self.log_message("🔧 Instalando FFmpeg...")
        self.status_var.set("Instalando FFmpeg...")
        try:
            if sys.platform == "darwin":
                # MacOS
                subprocess.check_call(["brew", "install", "ffmpeg"])
            elif sys.platform.startswith("linux"):
                # Linux
                subprocess.check_call(["sudo", "apt", "update"])
                subprocess.check_call(["sudo", "apt", "install", "-y", "ffmpeg"])
            elif sys.platform == "win32":
                # Windows: instrução para baixar manualmente
                messagebox.showinfo(
                    "FFmpeg no Windows",
                    "No Windows, baixe e instale manualmente:\nhttps://ffmpeg.org/download.html"
                )
                self.log_message("ℹ️ No Windows, baixe manualmente: https://ffmpeg.org/download.html")
                self.status_var.set("FFmpeg: instale manualmente no Windows")
                return
            self.log_message("✅ FFmpeg instalado com sucesso!")
            self.status_var.set("FFmpeg instalado com sucesso!")
        except Exception as e:
            self.log_message(f"❌ Erro ao instalar FFmpeg: {str(e)}")
            self.status_var.set("Erro ao instalar FFmpeg")
            
    def run(self):
        """Executa a aplicação"""
        self.root.mainloop()

if __name__ == "__main__":
    print("🎬 Iniciando YouTube Downloader Pro (Versão Simplificada)...")
    print("📋 Esta versão não precisa do MoviePy!")
    
    app = YouTubeDownloaderSimple()
    app.run()