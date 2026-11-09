"""
Módulo de download e extração de áudio de alta fidelidade com yt-dlp e ffmpeg.
Suporta playlists do YouTube, YouTube Music e vídeos individuais SEM limite de faixas.
"""

import os
import re
import threading
import traceback
import yt_dlp


class DownloadCancelledException(Exception):
    """Exceção levantada quando o usuário cancela o download."""
    pass


def sanitize_filename(name: str) -> str:
    """Remove caracteres inválidos para nomes de arquivos e pastas no Windows."""
    clean = re.sub(r'[\\/*?:"<>|]', '', name).strip()
    return clean or "Playlist"


class PlaylistDownloader:
    def __init__(self, callbacks=None):
        self.callbacks = callbacks or {}
        self.cancelled = False
        self._thread = None
        self._current_track_idx = 0
        self._total_tracks = 0

    def cancel(self):
        """Sinaliza cancelamento."""
        self.cancelled = True
        self._emit("on_status", "Cancelando download...")

    def _emit(self, event, *args, **kwargs):
        fn = self.callbacks.get(event)
        if fn:
            try:
                fn(*args, **kwargs)
            except Exception:
                pass

    def start_download(self, url: str, output_base_dir: str, options: dict):
        """Inicia o download em uma thread separada para não travar a interface."""
        self.cancelled = False
        self._thread = threading.Thread(
            target=self._worker,
            args=(url, output_base_dir, options),
            daemon=True
        )
        self._thread.start()

    def _worker(self, url: str, output_base_dir: str, options: dict):
        try:
            self._emit("on_status", "Analisando playlist completa (sem limites)...")

            use_cookies = options.get('use_cookies', False)
            browser = options.get('browser', 'brave')

            # Opções de extração de metadados com múltiplos clients para evitar corte em 30 itens
            flat_opts = {
                'extract_flat': 'in_playlist',
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
                'js_runtimes': {'node': {}},
                'playlistend': None,  # Explicitamente sem limite de fim
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web', 'default']
                    }
                }
            }

            if use_cookies:
                flat_opts['cookiesfrombrowser'] = (browser,)

            with yt_dlp.YoutubeDL(flat_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                except Exception as e:
                    self._emit("on_status", f"Erro ao acessar link: {e}")
                    self._emit("on_all_finished", 0, 1, output_base_dir)
                    return

            if not info:
                self._emit("on_status", "Nenhuma informação encontrada no link fornecido.")
                self._emit("on_all_finished", 0, 1, output_base_dir)
                return

            if self.cancelled:
                self._emit("on_cancelled")
                return

            is_playlist = 'entries' in info and info.get('_type') == 'playlist'
            playlist_title = info.get('title') or "Playlist"
            
            # Coleta todas as entradas do gerador da playlist
            raw_entries = []
            if is_playlist:
                self._emit("on_status", "Carregando todas as faixas da playlist...")
                for entry in info.get('entries', []):
                    if entry:
                        raw_entries.append(entry)
            else:
                raw_entries = [info]

            # Filtrar entradas válidas
            entries = [e for e in raw_entries if e]

            if not entries:
                self._emit("on_status", "A playlist está vazia ou os vídeos são privados.")
                self._emit("on_all_finished", 0, 0, output_base_dir)
                return

            # Aplicar limite personalizado se o usuário tiver especificado explicitamente
            custom_range = options.get('custom_range', '').strip()
            if custom_range and '-' in custom_range:
                try:
                    parts = custom_range.split('-')
                    start_idx = max(0, int(parts[0].strip()) - 1)
                    end_idx = int(parts[1].strip())
                    entries = entries[start_idx:end_idx]
                except Exception:
                    pass

            self._total_tracks = len(entries)
            self._emit("on_info_ready", {
                'is_playlist': is_playlist,
                'title': playlist_title,
                'total_tracks': self._total_tracks,
                'entries': entries
            })

            # Define diretório de saída
            create_subfolder = options.get('create_subfolder', True)
            if is_playlist and create_subfolder:
                folder_name = sanitize_filename(playlist_title)
                target_dir = os.path.join(output_base_dir, folder_name)
            else:
                target_dir = output_base_dir

            os.makedirs(target_dir, exist_ok=True)

            quality = options.get('quality', '320')
            embed_thumbnail = options.get('embed_thumbnail', True)
            embed_metadata = options.get('embed_metadata', True)
            number_tracks = options.get('number_tracks', True) and is_playlist

            success_count = 0
            error_count = 0

            # Loop por cada faixa (sem limite)
            for idx, entry in enumerate(entries):
                if self.cancelled:
                    break

                self._current_track_idx = idx
                entry_title = entry.get('title') or f"Faixa {idx + 1}"
                entry_url = entry.get('url') or entry.get('webpage_url')
                if not entry_url and entry.get('id'):
                    entry_url = f"https://www.youtube.com/watch?v={entry['id']}"

                self._emit("on_track_start", idx, self._total_tracks, entry_title)

                # Formato de numeração ajustável ao total de dígitos
                digits = len(str(self._total_tracks))
                if digits < 2:
                    digits = 2

                if number_tracks:
                    prefix = f"{idx + 1:0{digits}d} - "
                    out_template = os.path.join(target_dir, f"{prefix}%(title)s.%(ext)s")
                else:
                    out_template = os.path.join(target_dir, "%(title)s.%(ext)s")

                postprocessors = [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': quality,
                    }
                ]

                if embed_metadata:
                    postprocessors.append({
                        'key': 'FFmpegMetadata',
                        'add_metadata': True,
                    })

                ydl_track_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': out_template,
                    'postprocessors': postprocessors,
                    'js_runtimes': {'node': {}},
                    'quiet': True,
                    'no_warnings': True,
                    'ignoreerrors': False,
                    'windowsfilenames': True,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'web', 'default']
                        }
                    }
                }

                if use_cookies:
                    ydl_track_opts['cookiesfrombrowser'] = (browser,)

                if embed_thumbnail:
                    ydl_track_opts['writethumbnail'] = True
                    postprocessors.extend([
                        {'key': 'FFmpegThumbnailsConvertor', 'format': 'jpg'},
                        {'key': 'EmbedThumbnail', 'already_have_thumbnail': False},
                    ])

                def progress_hook(d):
                    if self.cancelled:
                        raise DownloadCancelledException()
                    status = d.get('status')
                    if status == 'downloading':
                        total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                        downloaded = d.get('downloaded_bytes') or 0
                        speed = d.get('speed') or 0
                        eta = d.get('eta') or 0

                        percent = (downloaded / total) if total > 0 else 0
                        speed_str = f"{speed / (1024*1024):.1f} MB/s" if speed else ""
                        eta_str = f"{eta}s" if eta else ""
                        self._emit("on_track_progress", idx, self._total_tracks, percent, speed_str, eta_str)
                    elif status == 'finished':
                        self._emit("on_track_postprocess", idx, self._total_tracks, "Convertendo para MP3 320kbps...")

                def pp_hook(d):
                    if self.cancelled:
                        raise DownloadCancelledException()
                    pp_key = d.get('postprocessor')
                    if d.get('status') == 'started':
                        if 'ExtractAudio' in str(pp_key):
                            self._emit("on_track_postprocess", idx, self._total_tracks, "Extraindo áudio de alta fidelidade...")
                        elif 'EmbedThumbnail' in str(pp_key):
                            self._emit("on_track_postprocess", idx, self._total_tracks, "Embutindo capa do álbum...")
                        elif 'Metadata' in str(pp_key):
                            self._emit("on_track_postprocess", idx, self._total_tracks, "Adicionando tags ID3...")

                ydl_track_opts['progress_hooks'] = [progress_hook]
                ydl_track_opts['postprocessor_hooks'] = [pp_hook]

                try:
                    with yt_dlp.YoutubeDL(ydl_track_opts) as ydl_track:
                        ydl_track.download([entry_url])
                    success_count += 1
                    self._emit("on_track_complete", idx, self._total_tracks, entry_title, target_dir)
                except DownloadCancelledException:
                    self.cancelled = True
                    break
                except Exception as ex:
                    error_count += 1
                    err_msg = str(ex).split('\n')[0]
                    self._emit("on_track_error", idx, self._total_tracks, entry_title, err_msg)

            if self.cancelled:
                self._emit("on_cancelled")
            else:
                self._emit("on_all_finished", success_count, error_count, target_dir)

        except Exception as e:
            traceback.print_exc()
            self._emit("on_status", f"Erro inesperado: {e}")
            self._emit("on_all_finished", 0, 1, output_base_dir)
