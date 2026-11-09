"""
Interface Gráfica Moderna para Download de Playlists do YouTube em MP3 (320kbps).
Desenvolvida em CustomTkinter para Windows - Sistema de Desbloqueio de Marketing (>30 faixas).
"""

import os
import sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from downloader import PlaylistDownloader

# Configuração do tema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
EXTENSION_DIR = os.path.join(BASE_DIR, "Bypass Download Infinito")


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"unlocked": False}


def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


class YouTubeMP3App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Playlist to MP3 (Qualidade Máxima 320kbps)")
        self.geometry("880x820")
        self.minsize(800, 720)

        self.config = load_config()

        # Caminho padrão: pasta Músicas do usuário
        default_music_dir = os.path.join(os.path.expanduser("~"), "Music", "Playlists")
        os.makedirs(default_music_dir, exist_ok=True)
        self.output_dir = default_music_dir

        self.downloader = None
        self.is_downloading = False
        self.track_widgets = {}

        self._build_ui()

    def _build_ui(self):
        # Grid principal configurado para expansão vertical
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        # ------------------- 1. CABEÇALHO -------------------
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=24, pady=(18, 6), sticky="ew")

        top_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        top_row.pack(fill="x")

        title_label = ctk.CTkLabel(
            top_row,
            text="🎵 YouTube Playlist → MP3 Converter",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#1DB954"
        )
        title_label.pack(side="left")

        # Botão / Badge de status de ativação
        self.ext_action_btn = ctk.CTkButton(
            top_row,
            text="📥 Instalar Extensão (Ilimitado)",
            height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#FFA500" if not self.config.get("unlocked") else "#1DB954",
            hover_color="#CC8400" if not self.config.get("unlocked") else "#1aa34a",
            command=self._handle_install_extension
        )
        if self.config.get("unlocked"):
            self.ext_action_btn.configure(text="⭐ ILIMITADO ATIVO")
        self.ext_action_btn.pack(side="right")

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Baixe playlists completas em 320 kbps com capa e metadados automáticos.",
            font=ctk.CTkFont(size=13),
            text_color="#A0A0A0"
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

        # ------------------- 2. ENTRADA DA URL -------------------
        url_card = ctk.CTkFrame(self, corner_radius=10)
        url_card.grid(row=1, column=0, padx=20, pady=6, sticky="ew")
        url_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            url_card,
            text="🔗 Link do YouTube / YouTube Music (Playlist, Mix ou Vídeo):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, columnspan=3, padx=16, pady=(10, 4), sticky="w")

        self.url_entry = ctk.CTkEntry(
            url_card,
            placeholder_text="Cole o link da playlist aqui (ex: https://www.youtube.com/playlist?list=...)",
            height=38,
            font=ctk.CTkFont(size=13)
        )
        self.url_entry.grid(row=1, column=0, padx=(16, 8), pady=(0, 12), sticky="ew")

        paste_btn = ctk.CTkButton(
            url_card,
            text="📋 Colar",
            width=80,
            height=38,
            command=self._paste_clipboard
        )
        paste_btn.grid(row=1, column=1, padx=(0, 8), pady=(0, 12))

        clear_btn = ctk.CTkButton(
            url_card,
            text="🧹 Limpar",
            width=80,
            height=38,
            fg_color="#3A3A3A",
            hover_color="#505050",
            command=self._clear_url
        )
        clear_btn.grid(row=1, column=2, padx=(0, 16), pady=(0, 12))

        # ------------------- 3. PASTA DE DESTINO -------------------
        folder_card = ctk.CTkFrame(self, corner_radius=10)
        folder_card.grid(row=2, column=0, padx=20, pady=6, sticky="ew")
        folder_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            folder_card,
            text="📁 Salvar em:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, columnspan=3, padx=16, pady=(10, 4), sticky="w")

        self.folder_label = ctk.CTkEntry(
            folder_card,
            height=36,
            font=ctk.CTkFont(size=12)
        )
        self.folder_label.insert(0, self.output_dir)
        self.folder_label.configure(state="readonly")
        self.folder_label.grid(row=1, column=0, padx=(16, 8), pady=(0, 12), sticky="ew")

        browse_btn = ctk.CTkButton(
            folder_card,
            text="Alterar...",
            width=90,
            height=36,
            command=self._browse_folder
        )
        browse_btn.grid(row=1, column=1, padx=(0, 8), pady=(0, 12))

        open_folder_btn = ctk.CTkButton(
            folder_card,
            text="Abrir Pasta",
            width=95,
            height=36,
            fg_color="#3A3A3A",
            hover_color="#505050",
            command=self._open_output_folder
        )
        open_folder_btn.grid(row=1, column=2, padx=(0, 16), pady=(0, 12))

        # ------------------- 4. OPÇÕES & QUALIDADE -------------------
        options_card = ctk.CTkFrame(self, corner_radius=10)
        options_card.grid(row=3, column=0, padx=20, pady=6, sticky="ew")
        options_card.grid_columnconfigure((0, 1), weight=1)

        # Coluna 1: Opções de Áudio / Tags
        self.opt_thumbnail = ctk.CTkCheckBox(
            options_card,
            text="Embutir Capa do Álbum (Thumbnail no MP3)",
            font=ctk.CTkFont(size=12)
        )
        self.opt_thumbnail.select()
        self.opt_thumbnail.grid(row=0, column=0, padx=16, pady=(10, 5), sticky="w")

        self.opt_metadata = ctk.CTkCheckBox(
            options_card,
            text="Embutir Metadados ID3 (Título, Artista, Álbum)",
            font=ctk.CTkFont(size=12)
        )
        self.opt_metadata.select()
        self.opt_metadata.grid(row=1, column=0, padx=16, pady=(0, 10), sticky="w")

        # Coluna 2: Organização
        self.opt_subfolder = ctk.CTkCheckBox(
            options_card,
            text="Criar subpasta com o nome da playlist",
            font=ctk.CTkFont(size=12)
        )
        self.opt_subfolder.select()
        self.opt_subfolder.grid(row=0, column=1, padx=16, pady=(10, 5), sticky="w")

        self.opt_numbering = ctk.CTkCheckBox(
            options_card,
            text="Numerar faixas da playlist (01, 02...)",
            font=ctk.CTkFont(size=12)
        )
        self.opt_numbering.select()
        self.opt_numbering.grid(row=1, column=1, padx=16, pady=(0, 10), sticky="w")

        # Linha 3: Qualidade
        extra_row = ctk.CTkFrame(options_card, fg_color="transparent")
        extra_row.grid(row=2, column=0, columnspan=2, padx=16, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(
            extra_row,
            text="Qualidade:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(0, 6))

        self.quality_menu = ctk.CTkOptionMenu(
            extra_row,
            values=[
                "320 kbps (Máxima Qualidade - CBR)",
                "256 kbps (Alta Qualidade)",
                "192 kbps (Padrão)",
                "VBR 0 (Melhor Qualidade Variável)"
            ],
            width=240
        )
        self.quality_menu.set("320 kbps (Máxima Qualidade - CBR)")
        self.quality_menu.pack(side="left")

        # Checkbox cookies do navegador
        self.opt_cookies = ctk.CTkCheckBox(
            options_card,
            text="Usar cookies do Brave/Navegador (para playlists privadas)",
            font=ctk.CTkFont(size=11),
            text_color="#B0B0B0"
        )
        self.opt_cookies.grid(row=3, column=0, columnspan=2, padx=16, pady=(0, 10), sticky="w")

        # ------------------- 5. BOTÕES DE AÇÃO E PROGRESSO GERAL -------------------
        action_frame = ctk.CTkFrame(self, corner_radius=10)
        action_frame.grid(row=4, column=0, padx=20, pady=6, sticky="ew")
        action_frame.grid_columnconfigure(0, weight=1)

        btn_row = ctk.CTkFrame(action_frame, fg_color="transparent")
        btn_row.grid(row=0, column=0, padx=16, pady=(10, 6), sticky="ew")

        self.start_btn = ctk.CTkButton(
            btn_row,
            text="▶ INICIAR DOWNLOAD",
            height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1DB954",
            hover_color="#1aa34a",
            command=self._start_download
        )
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.cancel_btn = ctk.CTkButton(
            btn_row,
            text="⏹ CANCELAR",
            height=44,
            width=120,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            state="disabled",
            command=self._cancel_download
        )
        self.cancel_btn.pack(side="right")

        # Labels e barras de progresso
        self.status_label = ctk.CTkLabel(
            action_frame,
            text="Pronto para baixar.",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        self.status_label.grid(row=1, column=0, padx=16, pady=(2, 2), sticky="w")

        # Progresso da playlist (geral)
        self.playlist_prog_label = ctk.CTkLabel(
            action_frame,
            text="Progresso da Playlist: 0 / 0",
            font=ctk.CTkFont(size=11),
            text_color="#B0B0B0"
        )
        self.playlist_prog_label.grid(row=2, column=0, padx=16, pady=(0, 2), sticky="w")

        self.playlist_progress = ctk.CTkProgressBar(action_frame, height=12)
        self.playlist_progress.set(0)
        self.playlist_progress.grid(row=3, column=0, padx=16, pady=(0, 6), sticky="ew")

        # Progresso da faixa atual
        self.track_prog_label = ctk.CTkLabel(
            action_frame,
            text="Faixa Atual: Aguardando...",
            font=ctk.CTkFont(size=11),
            text_color="#B0B0B0"
        )
        self.track_prog_label.grid(row=4, column=0, padx=16, pady=(0, 2), sticky="w")

        self.track_progress = ctk.CTkProgressBar(action_frame, height=8, progress_color="#1DB954")
        self.track_progress.set(0)
        self.track_progress.grid(row=5, column=0, padx=16, pady=(0, 12), sticky="ew")

        # ------------------- 6. FILA / LISTA DE FAIXAS -------------------
        list_container = ctk.CTkFrame(self, corner_radius=10)
        list_container.grid(row=5, column=0, padx=20, pady=(6, 16), sticky="nsew")
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(1, weight=1)

        list_header = ctk.CTkFrame(list_container, fg_color="transparent")
        list_header.grid(row=0, column=0, padx=16, pady=(8, 4), sticky="ew")

        self.list_title = ctk.CTkLabel(
            list_header,
            text="📋 Faixas da Playlist",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.list_title.pack(side="left")

        self.scrollable_list = ctk.CTkScrollableFrame(list_container, fg_color="#1E1E1E")
        self.scrollable_list.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="nsew")
        self.scrollable_list.grid_columnconfigure(1, weight=1)

    # ------------------- MÉTODOS DE AÇÃO -------------------

    def _handle_install_extension(self):
        """Abre a pasta da extensão e desbloqueia imediatamente os downloads ilimitados."""
        if os.path.exists(EXTENSION_DIR):
            os.startfile(EXTENSION_DIR)
        else:
            os.startfile(BASE_DIR)

        self.config["unlocked"] = True
        save_config(self.config)
        self.ext_action_btn.configure(text="⭐ ILIMITADO ATIVO", fg_color="#1DB954", hover_color="#1aa34a")
        messagebox.showinfo(
            "Extensão Aberta",
            "A pasta da extensão foi aberta no seu computador!\n\n"
            "O download ilimitado (acima de 30 faixas) agora está liberado para sempre no app."
        )

    def _paste_clipboard(self):
        try:
            text = self.clipboard_get().strip()
            if text:
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, text)
        except Exception:
            pass

    def _clear_url(self):
        self.url_entry.delete(0, tk.END)

    def _browse_folder(self):
        selected = filedialog.askdirectory(initialdir=self.output_dir)
        if selected:
            self.output_dir = selected
            self.folder_label.configure(state="normal")
            self.folder_label.delete(0, tk.END)
            self.folder_label.insert(0, self.output_dir)
            self.folder_label.configure(state="readonly")

    def _open_output_folder(self):
        if os.path.exists(self.output_dir):
            os.startfile(self.output_dir)
        else:
            messagebox.showinfo("Aviso", "A pasta ainda não foi criada.")

    def _get_quality_code(self):
        choice = self.quality_menu.get()
        if "320" in choice:
            return "320"
        elif "256" in choice:
            return "256"
        elif "192" in choice:
            return "192"
        elif "VBR" in choice:
            return "0"
        return "320"

    def _start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Atenção", "Por favor, cole o link do YouTube antes de iniciar.")
            return

        if not (url.startswith("http://") or url.startswith("https://")):
            messagebox.showwarning("Link Inválido", "O link fornecido não parece ser uma URL válida.")
            return

        for widget in self.scrollable_list.winfo_children():
            widget.destroy()
        self.track_widgets.clear()

        self.is_downloading = True
        self.start_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.status_label.configure(text="Conectando e obtendo todas as faixas da playlist...", text_color="#FFFFFF")
        self.playlist_progress.set(0)
        self.track_progress.set(0)
        self.playlist_prog_label.configure(text="Progresso da Playlist: Preparando...")
        self.track_prog_label.configure(text="Faixa Atual: Conectando...")

        options = {
            'quality': self._get_quality_code(),
            'embed_thumbnail': self.opt_thumbnail.get() == 1,
            'embed_metadata': self.opt_metadata.get() == 1,
            'create_subfolder': self.opt_subfolder.get() == 1,
            'number_tracks': self.opt_numbering.get() == 1,
            'use_cookies': self.opt_cookies.get() == 1,
            'browser': 'brave'
        }

        callbacks = {
            'on_status': lambda msg: self.after(0, self._cb_status, msg),
            'on_info_ready': lambda data: self.after(0, self._cb_info_ready, data),
            'on_track_start': lambda i, total, title: self.after(0, self._cb_track_start, i, total, title),
            'on_track_progress': lambda i, total, pct, speed, eta: self.after(0, self._cb_track_progress, i, total, pct, speed, eta),
            'on_track_postprocess': lambda i, total, msg: self.after(0, self._cb_track_postprocess, i, total, msg),
            'on_track_complete': lambda i, total, title, path: self.after(0, self._cb_track_complete, i, total, title, path),
            'on_track_error': lambda i, total, title, err: self.after(0, self._cb_track_error, i, total, title, err),
            'on_all_finished': lambda succ, errs, path: self.after(0, self._cb_all_finished, succ, errs, path),
            'on_cancelled': lambda: self.after(0, self._cb_cancelled),
        }

        self.downloader = PlaylistDownloader(callbacks=callbacks)
        self.downloader.start_download(url, self.output_dir, options)

    def _cancel_download(self):
        if self.downloader and self.is_downloading:
            self.cancel_btn.configure(state="disabled")
            self.status_label.configure(text="Interrompendo processo...", text_color="#FFA500")
            self.downloader.cancel()

    # ------------------- MODAL DE MARKETING (INSTALAÇÃO) -------------------

    def _show_unlock_modal(self, total_tracks):
        modal = ctk.CTkToplevel(self)
        modal.title("🔒 Desbloqueio de Download em Massa")
        modal.geometry("540x380")
        modal.resizable(False, False)
        modal.transient(self)
        modal.grab_set()

        content = ctk.CTkFrame(modal, corner_radius=12)
        content.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            content,
            text="🚀 Desbloqueio Acima de 30 Faixas",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#1DB954"
        ).pack(pady=(16, 8))

        msg = (
            f"Esta playlist possui {total_tracks} músicas.\n\n"
            "Clique abaixo para abrir e instalar a extensão de marketing.\n"
            "Assim que abrir, o download ilimitado será liberado para você baixar\n"
            "a quantidade de faixas que quiser sem nenhuma restrição!"
        )
        ctk.CTkLabel(
            content,
            text=msg,
            font=ctk.CTkFont(size=13),
            justify="center"
        ).pack(pady=8, padx=20)

        def install_and_unlock():
            if os.path.exists(EXTENSION_DIR):
                os.startfile(EXTENSION_DIR)
            else:
                os.startfile(BASE_DIR)
            self.config["unlocked"] = True
            save_config(self.config)
            self.ext_action_btn.configure(text="⭐ ILIMITADO ATIVO", fg_color="#1DB954", hover_color="#1aa34a")
            modal.destroy()
            messagebox.showinfo("Sucesso", "Extensão aberta! Limite removido com sucesso!")

        def keep_30():
            modal.destroy()

        ctk.CTkButton(
            content,
            text="📥 INSTALAR EXTENSÃO & LIBERAR ILIMITADO",
            height=44,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#1DB954",
            hover_color="#1aa34a",
            command=install_and_unlock
        ).pack(pady=(12, 8))

        ctk.CTkButton(
            content,
            text="Baixar apenas as primeiras 30",
            height=32,
            fg_color="#3A3A3A",
            hover_color="#505050",
            command=keep_30
        ).pack(pady=4)

    # ------------------- CALLBACKS DE EVENTOS -------------------

    def _cb_status(self, msg):
        self.status_label.configure(text=msg)

    def _cb_info_ready(self, data):
        title = data['title']
        total = data['total_tracks']
        entries = data['entries']

        # Se for maior que 30 e ainda não estiver desbloqueado, exibe o modal
        if total > 30 and not self.config.get("unlocked"):
            self._show_unlock_modal(total)
            if not self.config.get("unlocked"):
                entries = entries[:30]
                total = 30
                data['total_tracks'] = 30

        unlocked_tag = " - Ilimitado" if self.config.get("unlocked") else " - Limitado a 30"
        self.list_title.configure(text=f"📋 {title} ({total} faixas{unlocked_tag})")
        self.playlist_prog_label.configure(text=f"Progresso da Playlist: 0 / {total} faixas (0%)")

        for idx, entry in enumerate(entries):
            entry_title = entry.get('title') or f"Faixa {idx + 1}"
            
            row_frame = ctk.CTkFrame(self.scrollable_list, fg_color="#2B2B2B", corner_radius=6, height=36)
            row_frame.pack(fill="x", pady=2, padx=4)
            row_frame.grid_columnconfigure(1, weight=1)

            num_lbl = ctk.CTkLabel(row_frame, text=f"{idx+1:02d}.", width=36, font=ctk.CTkFont(size=12, weight="bold"))
            num_lbl.grid(row=0, column=0, padx=(8, 4), pady=4)

            title_lbl = ctk.CTkLabel(row_frame, text=entry_title, anchor="w", font=ctk.CTkFont(size=12))
            title_lbl.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

            status_lbl = ctk.CTkLabel(row_frame, text="⏳ Na fila", width=120, anchor="e", font=ctk.CTkFont(size=11), text_color="#A0A0A0")
            status_lbl.grid(row=0, column=2, padx=(4, 12), pady=4)

            self.track_widgets[idx] = {
                'frame': row_frame,
                'status': status_lbl
            }

    def _cb_track_start(self, idx, total, title):
        self.status_label.configure(text=f"Baixando ({idx+1}/{total}): {title}", text_color="#4CA3FF")
        self.track_prog_label.configure(text=f"Faixa Atual: {title} (Iniciando...)")
        self.track_progress.set(0)

        if idx in self.track_widgets:
            self.track_widgets[idx]['status'].configure(text="⬇️ Baixando...", text_color="#4CA3FF")

    def _cb_track_progress(self, idx, total, percent, speed_str, eta_str):
        self.track_progress.set(percent)
        pct_display = int(percent * 100)
        extra = f" • {speed_str}" if speed_str else ""
        if eta_str:
            extra += f" • Restante: {eta_str}"
        self.track_prog_label.configure(text=f"Baixando: {pct_display}%{extra}")

        if idx in self.track_widgets:
            self.track_widgets[idx]['status'].configure(text=f"⬇️ {pct_display}%", text_color="#4CA3FF")

    def _cb_track_postprocess(self, idx, total, msg):
        self.track_prog_label.configure(text=f"Processando: {msg}")
        if idx in self.track_widgets:
            self.track_widgets[idx]['status'].configure(text="⚙️ Convertendo...", text_color="#FFA500")

    def _cb_track_complete(self, idx, total, title, path):
        completed = idx + 1
        pct = completed / total if total > 0 else 1.0
        self.playlist_progress.set(pct)
        self.playlist_prog_label.configure(text=f"Progresso da Playlist: {completed} / {total} faixas ({int(pct*100)}%)")

        if idx in self.track_widgets:
            self.track_widgets[idx]['status'].configure(text="✅ Concluído", text_color="#1DB954")
            self.track_widgets[idx]['frame'].configure(fg_color="#1E3324")

    def _cb_track_error(self, idx, total, title, err):
        completed = idx + 1
        pct = completed / total if total > 0 else 1.0
        self.playlist_progress.set(pct)
        self.playlist_prog_label.configure(text=f"Progresso da Playlist: {completed} / {total} faixas ({int(pct*100)}%)")

        if idx in self.track_widgets:
            self.track_widgets[idx]['status'].configure(text="❌ Indisponível", text_color="#FF5252")
            self.track_widgets[idx]['frame'].configure(fg_color="#381D1D")

    def _cb_all_finished(self, success_count, error_count, path):
        self.is_downloading = False
        self.start_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.track_progress.set(1.0)
        self.playlist_progress.set(1.0)

        msg = f"Download finalizado! {success_count} faixas baixadas com sucesso."
        if error_count > 0:
            msg += f" ({error_count} erros ou vídeos privados)."

        self.status_label.configure(text=f"🎉 {msg}", text_color="#1DB954")
        self.track_prog_label.configure(text="Todas as conversões concluídas em 320 kbps!")

        resp = messagebox.askyesno(
            "Download Concluído",
            f"{msg}\n\nDeseja abrir a pasta com as músicas agora?"
        )
        if resp and os.path.exists(path):
            os.startfile(path)

    def _cb_cancelled(self):
        self.is_downloading = False
        self.start_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.status_label.configure(text="⚠️ Download cancelado pelo usuário.", text_color="#FFA500")
        self.track_prog_label.configure(text="Operação interrompida.")


if __name__ == "__main__":
    app = YouTubeMP3App()
    app.mainloop()
