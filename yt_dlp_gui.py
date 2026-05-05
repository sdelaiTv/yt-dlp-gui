import os
import queue
import re
import shlex
import shutil
import subprocess
import sys
import threading
import tkinter as tk
import json
import locale
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


class YtDlpGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("yt-dlp Desktop GUI")
        self.geometry("1120x760")
        self.minsize(980, 660)
        self.configure(bg="#0e1219")

        self.proc = None
        self.log_queue = queue.Queue()
        self.is_downloading = False
        self.settings_path = Path.home() / ".yt_dlp_gui_settings.json"
        self.base_command = self._detect_yt_dlp_command()
        self.proc_encoding = locale.getpreferredencoding(False) or "utf-8"
        self.current_lang = "ru"

        self.lang_display_to_code = {
            "Русский": "ru",
            "English": "en",
            "中文": "zh",
        }
        self.lang_code_to_display = {v: k for k, v in self.lang_display_to_code.items()}
        self.i18n = {
            "ru": {
                "title": "Best video downloader",
                "language": "Язык",
                "url_playlist": "URL / Плейлист",
                "save_to": "Сохранить в",
                "browse": "Обзор...",
                "download_mode": "Режим загрузки",
                "video_audio": "Видео + Аудио",
                "audio_only": "Только аудио",
                "video_format": "Формат видео",
                "audio_format": "Формат аудио",
                "audio_quality": "Качество аудио",
                "download_playlist": "Скачивать плейлист",
                "embed_metadata": "Вшить метаданные",
                "write_thumbnail": "Скачать превью",
                "write_subs": "Скачать субтитры",
                "write_auto_subs": "Скачать авто-субтитры",
                "restrict_filenames": "Безопасные имена файлов",
                "subtitle_languages": "Языки субтитров",
                "subtitle_format": "Формат субтитров",
                "advanced": "Продвинутые настройки",
                "use_proxy": "Использовать proxy",
                "proxy_address": "Адрес proxy",
                "video_settings": "Настройки видео",
                "audio_settings": "Настройки аудио",
                "cookies_browser": "Cookies из браузера",
                "cookies_file": "Файл cookies",
                "pick_cookies_file": "Выбрать cookies...",
                "extra_args": "Доп. аргументы",
                "naming": "Имена файлов и библиотека",
                "filename_template": "Шаблон имени файла",
                "template_preset": "Пресет шаблона",
                "template_custom": "Свой шаблон",
                "template_title_only": "Только название",
                "template_date_title": "Дата + название",
                "template_channel_title": "Канал/плейлист/название",
                "template_title_id": "Название + ID",
                "media_profile": "Профиль медиатеки",
                "profile_standard": "Обычный",
                "profile_plex_emby": "Plex / Emby (папка на видео)",
                "template_preview": "Превью итогового шаблона",
                "command_preview": "Предпросмотр команды",
                "status": "Статус",
                "start_download": "Скачать",
                "stop": "Остановить",
                "check_url": "Проверить URL",
                "open_folder": "Открыть папку",
                "copy_command": "Копировать команду",
                "log": "Лог",
            },
            "en": {
                "title": "Best video downloader",
                "language": "Language",
                "url_playlist": "URL / Playlist",
                "save_to": "Save To",
                "browse": "Browse...",
                "download_mode": "Download Mode",
                "video_audio": "Video + Audio",
                "audio_only": "Audio only",
                "video_format": "Video format",
                "audio_format": "Audio format",
                "audio_quality": "Audio quality",
                "download_playlist": "Download playlist",
                "embed_metadata": "Embed metadata",
                "write_thumbnail": "Write thumbnail",
                "write_subs": "Write subtitles",
                "write_auto_subs": "Write auto-subs",
                "restrict_filenames": "Restrict filenames",
                "subtitle_languages": "Subtitle languages",
                "subtitle_format": "Subtitle format",
                "advanced": "Advanced",
                "use_proxy": "Use proxy",
                "proxy_address": "Proxy address",
                "video_settings": "Video settings",
                "audio_settings": "Audio settings",
                "cookies_browser": "Cookies from browser",
                "cookies_file": "Cookies file",
                "pick_cookies_file": "Pick cookies file...",
                "extra_args": "Extra args",
                "naming": "Naming and library",
                "filename_template": "Filename template",
                "template_preset": "Template preset",
                "template_custom": "Custom template",
                "template_title_only": "Title only",
                "template_date_title": "Date + title",
                "template_channel_title": "Channel/playlist/title",
                "template_title_id": "Title + ID",
                "media_profile": "Media profile",
                "profile_standard": "Standard",
                "profile_plex_emby": "Plex / Emby (folder per video)",
                "template_preview": "Effective template preview",
                "command_preview": "Command Preview",
                "status": "Status",
                "start_download": "Start Download",
                "stop": "Stop",
                "check_url": "Check URL",
                "open_folder": "Open Folder",
                "copy_command": "Copy Command",
                "log": "Log",
            },
            "zh": {
                "title": "Best video downloader",
                "language": "语言",
                "url_playlist": "链接 / 播放列表",
                "save_to": "保存到",
                "browse": "浏览...",
                "download_mode": "下载模式",
                "video_audio": "视频 + 音频",
                "audio_only": "仅音频",
                "video_format": "视频格式",
                "audio_format": "音频格式",
                "audio_quality": "音频质量",
                "download_playlist": "下载播放列表",
                "embed_metadata": "嵌入元数据",
                "write_thumbnail": "下载封面图",
                "write_subs": "下载字幕",
                "write_auto_subs": "下载自动字幕",
                "restrict_filenames": "限制文件名",
                "subtitle_languages": "字幕语言",
                "subtitle_format": "字幕格式",
                "advanced": "高级设置",
                "use_proxy": "使用代理",
                "proxy_address": "代理地址",
                "video_settings": "视频设置",
                "audio_settings": "音频设置",
                "cookies_browser": "浏览器 Cookies",
                "cookies_file": "Cookies 文件",
                "pick_cookies_file": "选择 cookies 文件...",
                "extra_args": "额外参数",
                "naming": "命名与媒体库",
                "filename_template": "文件名模板",
                "template_preset": "模板预设",
                "template_custom": "自定义模板",
                "template_title_only": "仅标题",
                "template_date_title": "日期 + 标题",
                "template_channel_title": "频道/播放列表/标题",
                "template_title_id": "标题 + ID",
                "media_profile": "媒体库配置",
                "profile_standard": "标准",
                "profile_plex_emby": "Plex / Emby（每个视频单独文件夹）",
                "template_preview": "最终模板预览",
                "command_preview": "命令预览",
                "status": "状态",
                "start_download": "开始下载",
                "stop": "停止",
                "check_url": "检查 URL",
                "open_folder": "打开文件夹",
                "copy_command": "复制命令",
                "log": "日志",
            },
        }

        self.url_var = tk.StringVar()
        self.output_path_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.download_mode_var = tk.StringVar(value="video")
        self.video_format_var = tk.StringVar(value="bestvideo+bestaudio/best")
        self.audio_format_var = tk.StringVar(value="mp3")
        self.audio_quality_var = tk.StringVar(value="0")
        self.subtitle_langs_var = tk.StringVar(value="en,ru")
        self.subtitle_format_var = tk.StringVar(value="srt")
        self.proxy_var = tk.StringVar()
        self.proxy_enabled_var = tk.BooleanVar(value=False)
        self.cookies_browser_var = tk.StringVar(value="")
        self.cookies_file_var = tk.StringVar()
        self.extra_args_var = tk.StringVar()
        self.filename_preset_var = tk.StringVar(value="custom")
        self.filename_template_var = tk.StringVar(value="%(title)s.%(ext)s")
        self.media_profile_var = tk.StringVar(value="standard")
        self.template_preview_var = tk.StringVar(value="")
        self._syncing_template = False
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.speed_var = tk.StringVar(value="")

        self.download_playlist_var = tk.BooleanVar(value=True)
        self.embed_metadata_var = tk.BooleanVar(value=False)
        self.write_thumbnail_var = tk.BooleanVar(value=False)
        self.write_subs_var = tk.BooleanVar(value=False)
        self.write_auto_subs_var = tk.BooleanVar(value=False)
        self.restrict_filenames_var = tk.BooleanVar(value=False)
        self.lang_var = tk.StringVar(value=self.lang_code_to_display[self.current_lang])

        self._load_settings()
        self._configure_colors()
        self._configure_style()
        self._build_ui()
        self._wire_events()
        self._bind_ctrl_shortcuts_layout_agnostic()
        self._sync_proxy_state()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(120, self._drain_log_queue)

    # ---------- Color palette ----------
    def _configure_colors(self):
        self.bg = "#0e1219"
        self.bg2 = "#131a26"
        self.card_bg = "#192033"
        self.card_hover = "#1f2842"
        self.fg = "#d4dce8"
        self.fg_bright = "#f0f4fa"
        self.fg_dim = "#8895a8"
        self.accent = "#3b7dd8"
        self.accent_hover = "#4d91f0"
        self.success = "#28a745"
        self.success_hover = "#34ce57"
        self.danger = "#dc3545"
        self.danger_hover = "#e74c5e"
        self.entry_bg = "#0c111c"
        self.entry_border = "#283453"
        self.progress_bg = "#3b7dd8"

    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("App.TFrame", background=self.bg)
        style.configure("Card.TFrame", background=self.card_bg)
        style.configure("TLabel", background=self.card_bg, foreground=self.fg, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=self.bg, foreground=self.accent_hover, font=("Segoe UI Semibold", 13))
        style.configure("Section.TLabel", background=self.card_bg, foreground=self.accent, font=("Segoe UI Semibold", 11))
        style.configure("TCheckbutton", background=self.card_bg, foreground=self.fg, font=("Segoe UI", 10))
        style.map("TCheckbutton", background=[("active", self.card_hover)])
        style.configure("TRadiobutton", background=self.card_bg, foreground=self.fg, font=("Segoe UI", 10))
        style.map("TRadiobutton", background=[("active", self.card_hover)])

        style.configure("TEntry", fieldbackground=self.entry_bg, foreground=self.fg, bordercolor=self.entry_border, insertcolor=self.fg_bright)
        style.configure("TCombobox", fieldbackground=self.entry_bg, foreground=self.fg, background=self.card_bg, arrowcolor=self.fg, selectbackground=self.accent)
        style.map("TCombobox", fieldbackground=[("readonly", self.entry_bg)], background=[("readonly", self.card_bg)])

        style.configure("TProgressbar", troughcolor=self.entry_bg, background=self.progress_bg, thickness=10)

        # Scrollbar theme
        style.configure("Vertical.TScrollbar", background=self.card_bg, troughcolor=self.bg, bordercolor=self.bg, arrowcolor=self.fg)
        style.map("Vertical.TScrollbar", background=[("active", self.card_hover)])

    def t(self, key):
        return self.i18n.get(self.current_lang, self.i18n["en"]).get(key, key)

    # ---------- Custom button ----------
    def _make_button(self, parent, text, command=None, style="accent", width=None, padx=14, pady=6, **kw):
        """Return a tk.Button with custom modern styling."""
        btn = tk.Button(
            parent,
            text=text,
            font=("Segoe UI Semibold", 10),
            relief="flat",
            padx=padx,
            pady=pady,
            cursor="hand2",
            activebackground=self.card_hover,
            **kw,
        )
        if style == "accent":
            btn.configure(bg=self.accent, fg=self.fg_bright, activebackground=self.accent_hover, activeforeground=self.fg_bright)
        elif style == "success":
            btn.configure(bg=self.success, fg=self.fg_bright, activebackground=self.success_hover, activeforeground=self.fg_bright)
        elif style == "danger":
            btn.configure(bg=self.danger, fg=self.fg_bright, activebackground=self.danger_hover, activeforeground=self.fg_bright)
        else:
            btn.configure(bg=self.card_bg, fg=self.fg, activebackground=self.card_hover, activeforeground=self.fg_bright)

        if width:
            btn.configure(width=width)

        if command:
            btn.configure(command=command)

        # Hover effect
        def on_enter(e):
            if btn["state"] == "normal":
                if style == "accent":
                    btn["bg"] = self.accent_hover
                elif style == "success":
                    btn["bg"] = self.success_hover
                elif style == "danger":
                    btn["bg"] = self.danger_hover
                else:
                    btn["bg"] = self.card_hover

        def on_leave(e):
            if btn["state"] == "normal":
                if style == "accent":
                    btn["bg"] = self.accent
                elif style == "success":
                    btn["bg"] = self.success
                elif style == "danger":
                    btn["bg"] = self.danger
                else:
                    btn["bg"] = self.card_bg

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def _make_entry(self, parent, textvariable, **kw):
        """Return a styled tk.Entry matching the dark theme."""
        entry = tk.Entry(
            parent,
            textvariable=textvariable,
            bg=self.entry_bg,
            fg=self.fg,
            insertbackground=self.fg_bright,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.entry_border,
            highlightcolor=self.accent,
            font=("Segoe UI", 10),
            **kw,
        )
        return entry

    def _make_combobox(self, parent, textvariable, values, **kw):
        """Return a ttk.Combobox with modern style."""
        combo = ttk.Combobox(
            parent,
            textvariable=textvariable,
            values=values,
            state="readonly",
            font=("Segoe UI", 10),
            **kw,
        )
        return combo

    # ---------- UI building ----------
    def _build_ui(self):
        for child in self.winfo_children():
            child.destroy()
        root = tk.Frame(self, bg=self.bg)
        root.pack(fill="both", expand=True)

        self.scroll_canvas = tk.Canvas(root, bg=self.bg, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.scroll_canvas.yview, style="Vertical.TScrollbar")
        self.scroll_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        self.content_frame = tk.Frame(self.scroll_canvas, bg=self.bg)
        self.canvas_window = self.scroll_canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        self.content_frame.bind("<Configure>", self._on_content_configure)
        self.scroll_canvas.bind("<Configure>", self._on_canvas_configure)
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.scroll_canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.scroll_canvas.bind_all("<Button-5>", self._on_mousewheel_linux)

        # Top bar
        top_bar = tk.Frame(self.content_frame, bg=self.bg)
        top_bar.pack(fill="x", pady=(6, 6), padx=6)
        tk.Label(top_bar, text=self.t("title"), bg=self.bg, fg=self.accent_hover, font=("Segoe UI Semibold", 14)).pack(side="left")

        lang_frame = tk.Frame(top_bar, bg=self.bg)
        lang_frame.pack(side="right")
        tk.Label(lang_frame, text=self.t("language"), bg=self.bg, fg=self.fg_dim, font=("Segoe UI", 9)).pack(side="left", padx=(0, 6))
        lang_combo = self._make_combobox(lang_frame, self.lang_var, list(self.lang_display_to_code.keys()), width=10)
        lang_combo.pack(side="right")
        lang_combo.bind("<<ComboboxSelected>>", self._on_language_changed)

        # Separator
        self._separator(self.content_frame)

        self._build_input_card(self.content_frame)
        self._separator(self.content_frame)
        self._build_options_card(self.content_frame)
        self._separator(self.content_frame)
        self._build_naming_card(self.content_frame)
        self._separator(self.content_frame)
        self._build_advanced_card(self.content_frame)
        self._separator(self.content_frame)
        self._build_command_card(self.content_frame)
        self._separator(self.content_frame)
        self._build_status_card(self.content_frame)
        self._separator(self.content_frame)
        self._build_log_card(self.content_frame)

    def _separator(self, parent):
        """Draw a thin horizontal line."""
        frame = tk.Frame(parent, bg=self.bg, height=2)
        frame.pack(fill="x", padx=6, pady=(0, 0))
        line = tk.Frame(frame, bg=self.entry_border, height=1)
        line.pack(fill="x")

    def _on_content_configure(self, _event):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.scroll_canvas.itemconfigure(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if event.delta:
            self.scroll_canvas.yview_scroll(int(-event.delta / 120), "units")

    def _on_mousewheel_linux(self, event):
        if event.num == 4:
            self.scroll_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.scroll_canvas.yview_scroll(1, "units")

    def _card(self, parent):
        frame = tk.Frame(parent, bg=self.card_bg, padx=12, pady=10)
        frame.pack(fill="x", pady=6, padx=6)
        return frame

    def _build_input_card(self, parent):
        card = self._card(parent)
        # URL
        tk.Label(card, text=self.t("url_playlist"), bg=self.card_bg, fg=self.fg_dim, font=("Segoe UI", 9)).grid(row=0, column=0, columnspan=2, sticky="w")
        url_entry = self._make_entry(card, self.url_var)
        url_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 8))
        url_entry.configure(highlightthickness=1, bd=0)

        # Save to
        tk.Label(card, text=self.t("save_to"), bg=self.card_bg, fg=self.fg_dim, font=("Segoe UI", 9)).grid(row=2, column=0, columnspan=2, sticky="w")
        out_entry = self._make_entry(card, self.output_path_var)
        out_entry.grid(row=3, column=0, sticky="ew", pady=(2, 0))
        out_entry.configure(highlightthickness=1, bd=0)
        self._make_button(card, self.t("browse"), command=self._pick_output_folder, style="default").grid(row=3, column=1, sticky="e", padx=(8, 0))

        card.columnconfigure(0, weight=1)

    def _build_options_card(self, parent):
        card = self._card(parent)
        card.grid_columnconfigure(0, weight=1, uniform="col")
        card.grid_columnconfigure(1, weight=1, uniform="col")
        card.grid_columnconfigure(2, weight=1, uniform="col")
        card.grid_rowconfigure(0, weight=1)

        # Row 0: Mode, Video, Audio
        mode_frame = tk.Frame(card, bg=self.card_bg)
        mode_frame.grid(row=0, column=0, sticky="nsew", padx=8)
        mode_frame.grid_rowconfigure(10, weight=1)
        tk.Label(mode_frame, text=self.t("download_mode"), bg=self.card_bg, fg=self.fg_dim, font=("Segoe UI", 9)).pack(anchor="w")
        ttk.Radiobutton(mode_frame, text=self.t("video_audio"), value="video", variable=self.download_mode_var, command=self._on_download_mode_changed).pack(anchor="w")
        ttk.Radiobutton(mode_frame, text=self.t("audio_only"), value="audio", variable=self.download_mode_var, command=self._on_download_mode_changed).pack(anchor="w")
        # spacer to fill remaining height
        tk.Frame(mode_frame, bg=self.card_bg).pack(expand=True)

        vframe = tk.Frame(card, bg=self.card_bg)
        vframe.grid(row=0, column=1, sticky="nsew", padx=8)
        vframe.grid_rowconfigure(10, weight=1)
        tk.Label(vframe, text=self.t("video_settings"), bg=self.card_bg, fg=self.fg_dim, font=("Segoe UI", 9)).pack(anchor="w")
        tk.Label(vframe, text=self.t("video_format"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 0))
        self.video_format_combo = self._make_combobox(vframe, self.video_format_var, [
            "bestvideo+bestaudio/best",
            "best",
            "bv*+ba/b",
            "bv*[height<=2160]+ba/best[height<=2160]",
            "bv*[height<=1440]+ba/best[height<=1440]",
            "bv*[height<=1080]+ba/best[height<=1080]",
            "bv*[height<=720]+ba/best[height<=720]",
            "bv*[height<=480]+ba/best[height<=480]",
            "worst",
        ])
        self.video_format_combo.pack(fill="x", pady=(2, 4))
        tk.Frame(vframe, bg=self.card_bg).pack(expand=True)

        aframe = tk.Frame(card, bg=self.card_bg)
        aframe.grid(row=0, column=2, sticky="nsew", padx=8)
        aframe.grid_rowconfigure(10, weight=1)
        tk.Label(aframe, text=self.t("audio_settings"), bg=self.card_bg, fg=self.fg_dim, font=("Segoe UI", 9)).pack(anchor="w")
        tk.Label(aframe, text=self.t("audio_format"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 0))
        self.audio_format_combo = self._make_combobox(aframe, self.audio_format_var, ["best", "mp3", "m4a", "aac", "flac", "opus", "vorbis", "wav"])
        self.audio_format_combo.pack(fill="x", pady=(2, 4))
        tk.Label(aframe, text=self.t("audio_quality"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).pack(anchor="w")
        self.audio_quality_combo = self._make_combobox(aframe, self.audio_quality_var, ["0", "1", "2", "3", "4", "5", "7", "10", "96K", "128K", "160K", "192K", "256K", "320K"], width=10)
        self.audio_quality_combo.pack(anchor="w", pady=(2, 0))
        tk.Frame(aframe, bg=self.card_bg).pack(expand=True)

        # Row 1: toggles
        toggles = tk.Frame(card, bg=self.card_bg)
        toggles.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(8, 4))
        for text, var in [
            (self.t("download_playlist"), self.download_playlist_var),
            (self.t("embed_metadata"), self.embed_metadata_var),
            (self.t("write_thumbnail"), self.write_thumbnail_var),
            (self.t("write_subs"), self.write_subs_var),
            (self.t("write_auto_subs"), self.write_auto_subs_var),
            (self.t("restrict_filenames"), self.restrict_filenames_var),
        ]:
            ttk.Checkbutton(toggles, text=text, variable=var, command=self._refresh_command).pack(side="left", padx=(0, 12))

        # Row 2: subtitle languages
        sub_frame = tk.Frame(card, bg=self.card_bg)
        sub_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(4, 0))
        tk.Label(sub_frame, text=self.t("subtitle_languages"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        sub_lang_entry = self._make_entry(sub_frame, self.subtitle_langs_var, width=18)
        sub_lang_entry.grid(row=1, column=0, sticky="w")
        sub_lang_entry.configure(highlightthickness=1, bd=0)
        tk.Label(sub_frame, text=self.t("subtitle_format"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).grid(row=0, column=1, sticky="w", padx=(14, 0))
        sub_fmt_entry = self._make_entry(sub_frame, self.subtitle_format_var, width=10)
        sub_fmt_entry.grid(row=1, column=1, sticky="w", padx=(14, 0))
        sub_fmt_entry.configure(highlightthickness=1, bd=0)

        self._sync_format_sections()

    def _build_advanced_card(self, parent):
        card = self._card(parent)
        card.grid_columnconfigure(0, weight=1, uniform="col")
        card.grid_columnconfigure(1, weight=1, uniform="col")

        tk.Label(card, text=self.t("advanced"), bg=self.card_bg, fg=self.accent, font=("Segoe UI Semibold", 11)).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        ttk.Checkbutton(card, text=self.t("use_proxy"), variable=self.proxy_enabled_var, command=self._sync_proxy_state).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 2))

        # Pair 1: proxy address <-> cookies browser
        tk.Label(card, text=self.t("proxy_address"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", padx=(0, 8), pady=(2, 0))
        tk.Label(card, text=self.t("cookies_browser"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).grid(row=2, column=1, sticky="w", padx=(8, 0), pady=(2, 0))

        self.proxy_entry = self._make_entry(card, self.proxy_var)
        self.proxy_entry.grid(row=3, column=0, sticky="ew", padx=(0, 8))
        self.proxy_entry.configure(highlightthickness=1, bd=0)
        cookie_browser_combo = self._make_combobox(card, self.cookies_browser_var, ["", "firefox", "chrome", "chromium", "edge", "opera", "brave", "vivaldi", "safari"])
        cookie_browser_combo.grid(row=3, column=1, sticky="ew", padx=(8, 0))

        # Pair 2: extra args <-> cookies file
        tk.Label(card, text=self.t("extra_args"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).grid(row=4, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        tk.Label(card, text=self.t("cookies_file"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).grid(row=4, column=1, sticky="w", padx=(8, 0), pady=(8, 0))

        extra_entry = self._make_entry(card, self.extra_args_var)
        extra_entry.grid(row=5, column=0, sticky="ew", padx=(0, 8))
        extra_entry.configure(highlightthickness=1, bd=0)

        cookie_file_frame = tk.Frame(card, bg=self.card_bg)
        cookie_file_frame.grid(row=5, column=1, sticky="ew", padx=(8, 0))
        cookie_file_entry = self._make_entry(cookie_file_frame, self.cookies_file_var)
        cookie_file_entry.pack(side="left", fill="x", expand=True)
        cookie_file_entry.configure(highlightthickness=1, bd=0)
        self._make_button(cookie_file_frame, "…", command=self._pick_cookie_file, style="default", padx=8, width=3).pack(side="right", padx=(6, 0))

    def _build_naming_card(self, parent):
        card = self._card(parent)
        card.grid_columnconfigure(0, weight=1, uniform="col")
        card.grid_columnconfigure(1, weight=1, uniform="col")

        tk.Label(card, text=self.t("naming"), bg=self.card_bg, fg=self.accent, font=("Segoe UI Semibold", 11)).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        tk.Label(card, text=self.t("template_preset"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", padx=(0, 8))
        preset_values = [
            ("title_id", self.t("template_title_id")),
            ("title_only", self.t("template_title_only")),
            ("date_title", self.t("template_date_title")),
            ("channel_title", self.t("template_channel_title")),
            ("custom", self.t("template_custom")),
        ]
        self.template_label_to_key = {label: key for key, label in preset_values}
        self.template_key_to_label = {key: label for key, label in preset_values}
        self.filename_preset_label_var = tk.StringVar(value=self.template_key_to_label.get(self.filename_preset_var.get(), self.t("template_title_id")))
        self.filename_preset_combo = self._make_combobox(card, self.filename_preset_label_var, [label for _, label in preset_values])
        self.filename_preset_combo.grid(row=2, column=0, sticky="ew", padx=(0, 8))
        self.filename_preset_combo.bind("<<ComboboxSelected>>", self._on_template_preset_changed)

        tk.Label(card, text=self.t("media_profile"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).grid(row=1, column=1, sticky="w", padx=(8, 0))
        profile_values = [self.t("profile_standard"), self.t("profile_plex_emby")]
        self.profile_label_to_key = {
            self.t("profile_standard"): "standard",
            self.t("profile_plex_emby"): "plex_emby",
        }
        self.profile_key_to_label = {v: k for k, v in self.profile_label_to_key.items()}
        self.media_profile_label_var = tk.StringVar(value=self.profile_key_to_label.get(self.media_profile_var.get(), self.t("profile_standard")))
        self.media_profile_combo = self._make_combobox(card, self.media_profile_label_var, profile_values)
        self.media_profile_combo.grid(row=2, column=1, sticky="ew", padx=(8, 0))
        self.media_profile_combo.bind("<<ComboboxSelected>>", self._on_media_profile_changed)

        tk.Label(card, text=self.t("filename_template"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))
        template_entry = self._make_entry(card, self.filename_template_var)
        template_entry.grid(row=4, column=0, columnspan=2, sticky="ew")
        template_entry.configure(highlightthickness=1, bd=0)
        template_entry.bind("<KeyRelease>", self._on_template_manual_edit)

        tk.Label(card, text=self.t("template_preview"), bg=self.card_bg, fg=self.fg_dim, font=("Segoe UI", 9)).grid(row=5, column=0, columnspan=2, sticky="w", pady=(8, 0))
        preview = self._make_entry(card, self.template_preview_var)
        preview.grid(row=6, column=0, columnspan=2, sticky="ew")
        preview.configure(state="readonly", readonlybackground=self.entry_bg, disabledforeground=self.fg_dim, highlightthickness=1, bd=0)
        self._sync_template_with_preset()

    def _build_command_card(self, parent):
        card = self._card(parent)
        tk.Label(card, text=self.t("command_preview"), bg=self.card_bg, fg=self.accent, font=("Segoe UI Semibold", 11)).pack(anchor="w")
        self.command_preview = tk.Text(
            card, height=3,
            bg=self.entry_bg, fg="#b8cce0",
            insertbackground=self.fg_bright,
            bd=0, relief="flat", wrap="word",
            font=("Consolas", 9),
            padx=8, pady=4,
        )
        self.command_preview.pack(fill="x", pady=(6, 0))
        self.command_preview.configure(state="disabled")
        self._refresh_command()

    def _build_status_card(self, parent):
        card = self._card(parent)
        top = tk.Frame(card, bg=self.card_bg)
        top.pack(fill="x")
        tk.Label(top, text=self.t("status"), bg=self.card_bg, fg=self.fg_dim, font=("Segoe UI", 9)).pack(side="left")
        tk.Label(top, textvariable=self.status_var, bg=self.card_bg, fg=self.fg_bright, font=("Segoe UI Semibold", 10)).pack(side="left", padx=(8, 0))
        # Speed next to status
        tk.Label(top, textvariable=self.speed_var, bg=self.card_bg, fg=self.accent_hover, font=("Segoe UI", 9)).pack(side="left", padx=(16, 0))

        self.progress = ttk.Progressbar(card, variable=self.progress_var, maximum=100)
        self.progress.pack(fill="x", pady=(8, 8))

        actions = tk.Frame(card, bg=self.card_bg)
        actions.pack(fill="x")
        self._make_button(actions, f"  {self.t('start_download')}  ", command=self.start_download, style="success").pack(side="left")
        self._make_button(actions, f"  {self.t('stop')}  ", command=self.stop_download, style="danger").pack(side="left", padx=(8, 0))
        self._make_button(actions, self.t("check_url"), command=self.check_url, style="default").pack(side="left", padx=(8, 0))
        self._make_button(actions, self.t("open_folder"), command=self.open_output_folder, style="default").pack(side="left", padx=(8, 0))
        self._make_button(actions, self.t("copy_command"), command=self.copy_command, style="default").pack(side="left", padx=(8, 0))

    def _build_log_card(self, parent):
        card = self._card(parent)
        header = tk.Frame(card, bg=self.card_bg)
        header.pack(fill="x")
        self.log_expanded = tk.BooleanVar(value=False)

        self.log_toggle_btn = tk.Label(
            header, text="▶", bg=self.card_bg, fg=self.fg_dim,
            font=("Segoe UI", 9), cursor="hand2",
        )
        self.log_toggle_btn.pack(side="left")
        tk.Label(header, text=self.t("log"), bg=self.card_bg, fg=self.accent, font=("Segoe UI Semibold", 11)).pack(side="left", padx=(4, 0))

        self.log_text = tk.Text(
            card, height=12,
            bg=self.entry_bg, fg="#b0c4d8",
            insertbackground=self.fg_bright,
            bd=0, relief="flat",
            font=("Consolas", 9),
            padx=8, pady=4,
        )
        self.log_text.pack(fill="both", expand=True, pady=(6, 0))
        self.log_text.pack_forget()  # collapsed by default

        def toggle_log(_event=None):
            if self.log_expanded.get():
                self.log_text.pack_forget()
                self.log_toggle_btn.configure(text="▶")
            else:
                self.log_text.pack(fill="both", expand=True, pady=(6, 0))
                self.log_toggle_btn.configure(text="▼")
            self.log_expanded.set(not self.log_expanded.get())

        self.log_toggle_btn.bind("<Button-1>", toggle_log)
        header.bind("<Button-1>", toggle_log)
        self.log_text.bind("<Control-c>", self._copy_from_log)
        self.log_text.bind("<Control-C>", self._copy_from_log)
        self.log_text.configure(state="disabled")

    def _wire_events(self):
        for var in (
            self.url_var,
            self.output_path_var,
            self.download_mode_var,
            self.video_format_var,
            self.audio_format_var,
            self.audio_quality_var,
            self.subtitle_langs_var,
            self.subtitle_format_var,
            self.proxy_var,
            self.proxy_enabled_var,
            self.cookies_browser_var,
            self.cookies_file_var,
            self.extra_args_var,
            self.filename_preset_var,
            self.filename_template_var,
            self.media_profile_var,
            self.download_playlist_var,
            self.embed_metadata_var,
            self.write_thumbnail_var,
            self.write_subs_var,
            self.write_auto_subs_var,
            self.restrict_filenames_var,
        ):
            var.trace_add("write", self._on_settings_changed)

    def _bind_ctrl_shortcuts_layout_agnostic(self):
        self.bind_all("<Control-KeyPress>", self._on_ctrl_keypress, add="+")

    def _on_language_changed(self, _event):
        selected = self.lang_var.get()
        self.current_lang = self.lang_display_to_code.get(selected, "ru")
        self._build_ui()
        self._refresh_command()

    def _on_template_preset_changed(self, _event):
        selected_label = self.filename_preset_label_var.get()
        selected_key = self.template_label_to_key.get(selected_label, "title_id")
        self.filename_preset_var.set(selected_key)
        self._apply_template_preset(selected_key)
        self._on_settings_changed()

    def _on_media_profile_changed(self, _event):
        selected_label = self.media_profile_label_var.get()
        selected_key = self.profile_label_to_key.get(selected_label, "standard")
        self.media_profile_var.set(selected_key)
        if selected_key == "plex_emby":
            current = self.filename_template_var.get().strip() or "%(title)s.%(ext)s"
            if "/" not in current and "\\" not in current:
                # Put each item into its own folder without forcing ID.
                self.filename_template_var.set(f"%(title)s/{current}")
        self._update_template_preview()
        self._on_settings_changed()

    def _on_template_manual_edit(self, _event):
        if self.filename_preset_var.get() != "custom":
            self.filename_preset_var.set("custom")
            if hasattr(self, "filename_preset_label_var") and hasattr(self, "template_key_to_label"):
                self.filename_preset_label_var.set(self.template_key_to_label.get("custom", self.t("template_custom")))
        self._update_template_preview()

    def _apply_template_preset(self, preset_key):
        templates = {
            "title_id": "%(title)s [%(id)s].%(ext)s",
            "title_only": "%(title)s.%(ext)s",
            "date_title": "%(upload_date>%Y-%m-%d)s - %(title)s [%(id)s].%(ext)s",
            "channel_title": "%(uploader)s/%(playlist_title|single)s/%(title)s [%(id)s].%(ext)s",
        }
        if preset_key != "custom":
            self.filename_template_var.set(templates.get(preset_key, templates["title_id"]))
        self._update_template_preview()

    def _sync_template_with_preset(self):
        if self._syncing_template:
            return
        preset_key = self.filename_preset_var.get().strip() or "title_id"
        if preset_key == "custom":
            self._update_template_preview()
            return
        self._syncing_template = True
        try:
            self._apply_template_preset(preset_key)
        finally:
            self._syncing_template = False

    def _effective_output_template(self):
        base_template = self.filename_template_var.get().strip() or "%(title)s.%(ext)s"
        return base_template

    def _update_template_preview(self):
        self.template_preview_var.set(self._effective_output_template())

    def _on_download_mode_changed(self):
        self._sync_format_sections()
        self._on_settings_changed()

    def _sync_format_sections(self):
        mode = self.download_mode_var.get()
        if mode == "audio":
            self.video_format_combo.configure(state="disabled")
            self.audio_format_combo.configure(state="readonly")
            self.audio_quality_combo.configure(state="readonly")
        else:
            self.video_format_combo.configure(state="readonly")
            self.audio_format_combo.configure(state="disabled")
            self.audio_quality_combo.configure(state="disabled")

    def _on_ctrl_keypress(self, event):
        widget = self.focus_get()
        if widget is None:
            return None

        keycode = event.keycode
        if keycode == 65:  # A
            return self._handle_ctrl_a(widget)
        if keycode == 67:  # C
            return self._handle_ctrl_c(widget)
        if keycode == 86:  # V
            return self._handle_ctrl_v(widget)
        if keycode == 88:  # X
            return self._handle_ctrl_x(widget)
        return None

    def _handle_ctrl_a(self, widget):
        if isinstance(widget, tk.Entry):
            widget.select_range(0, "end")
            widget.icursor("end")
            return "break"
        if isinstance(widget, tk.Text):
            widget.tag_add("sel", "1.0", "end-1c")
            return "break"
        return None

    def _handle_ctrl_c(self, widget):
        if widget is self.log_text:
            return self._copy_from_log(None)
        try:
            widget.event_generate("<<Copy>>")
            return "break"
        except tk.TclError:
            return None

    def _handle_ctrl_v(self, widget):
        if widget is self.log_text and str(widget.cget("state")) == "disabled":
            return "break"
        try:
            widget.event_generate("<<Paste>>")
            return "break"
        except tk.TclError:
            return None

    def _handle_ctrl_x(self, widget):
        try:
            widget.event_generate("<<Cut>>")
            return "break"
        except tk.TclError:
            return None

    def _copy_from_log(self, _event):
        try:
            selected = self.log_text.get("sel.first", "sel.last")
        except tk.TclError:
            return "break"
        self.clipboard_clear()
        self.clipboard_append(selected)
        return "break"

    def _on_settings_changed(self, *_):
        self._update_template_preview()
        self._refresh_command()
        self._save_settings()

    def _sync_proxy_state(self):
        state = "normal" if self.proxy_enabled_var.get() else "disabled"
        self.proxy_entry.configure(state=state)
        self._on_settings_changed()

    def _detect_ffmpeg_location(self):
        for base in self._runtime_dirs():
            for rel in (Path("portable-runtime/ffmpeg"), Path("ffmpeg/bin"), Path("ffmpeg"), Path(".")):
                candidate = base / rel
                if (candidate / "ffmpeg.exe").exists() and (candidate / "ffprobe.exe").exists():
                    return str(candidate.resolve())

        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            return str(Path(ffmpeg_path).parent)
        winget_link = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Links" / "ffmpeg.exe"
        if winget_link.exists():
            return str(winget_link.parent)
        for candidate in (Path("C:/Program Files/ffmpeg/bin"), Path("C:/ffmpeg/bin")):
            if (candidate / "ffmpeg.exe").exists():
                return str(candidate)
        return ""

    def _runtime_dirs(self):
        dirs = []
        if getattr(sys, "frozen", False):
            dirs.append(Path(sys.executable).resolve().parent)
            meipass = getattr(sys, "_MEIPASS", None)
            if meipass:
                dirs.append(Path(meipass).resolve())
        script_path = globals().get("__file__")
        if script_path:
            dirs.append(Path(script_path).resolve().parent)
        else:
            dirs.append(Path(sys.argv[0]).resolve().parent)
        return dirs

    def _detect_yt_dlp_command(self):
        if getattr(sys, "frozen", False):
            for base in self._runtime_dirs():
                for rel in (Path("yt-dlp.exe"), Path("yt_dlp.exe"), Path("portable-runtime/yt-dlp.exe")):
                    candidate = base / rel
                    if candidate.exists():
                        return [str(candidate.resolve())]
        return [sys.executable, "-m", "yt_dlp"]

    def _load_settings(self):
        if not self.settings_path.exists():
            return
        try:
            data = json.loads(self.settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        self.proxy_var.set(str(data.get("proxy_address", "")))
        self.proxy_enabled_var.set(bool(data.get("proxy_enabled", False)))
        self.filename_preset_var.set(str(data.get("filename_preset", "custom")))
        self.filename_template_var.set(str(data.get("filename_template", "%(title)s.%(ext)s")))
        self.media_profile_var.set(str(data.get("media_profile", "standard")))

    def _save_settings(self):
        data = {
            "proxy_address": self.proxy_var.get().strip(),
            "proxy_enabled": bool(self.proxy_enabled_var.get()),
            "filename_preset": self.filename_preset_var.get().strip() or "custom",
            "filename_template": self.filename_template_var.get().strip() or "%(title)s.%(ext)s",
            "media_profile": self.media_profile_var.get().strip() or "standard",
        }
        try:
            self.settings_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            return

    def _pick_output_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_path_var.get() or str(Path.home()))
        if folder:
            self.output_path_var.set(folder)
            self._refresh_command()

    def _pick_cookie_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            self.cookies_file_var.set(filename)
            self._refresh_command()

    def _set_command_preview(self, text):
        self.command_preview.configure(state="normal")
        self.command_preview.delete("1.0", "end")
        self.command_preview.insert("1.0", text)
        self.command_preview.configure(state="disabled")

    def _append_log(self, text):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _build_command(self, for_check=False):
        url = self.url_var.get().strip()
        cmd = list(self.base_command)

        output_path = self.output_path_var.get().strip()
        if output_path:
            cmd.extend(["--paths", output_path])
        cmd.extend(["--output", self._effective_output_template()])

        if self.download_mode_var.get() == "audio":
            cmd.append("--extract-audio")
            cmd.extend(["--audio-format", self.audio_format_var.get().strip() or "mp3"])
            cmd.extend(["--audio-quality", self.audio_quality_var.get().strip() or "0"])
        else:
            video_format = self.video_format_var.get().strip()
            if video_format:
                cmd.extend(["--format", video_format])

        if self.download_playlist_var.get():
            cmd.append("--yes-playlist")
        else:
            cmd.append("--no-playlist")

        if self.embed_metadata_var.get():
            cmd.append("--embed-metadata")

        if self.write_thumbnail_var.get():
            cmd.append("--write-thumbnail")

        if self.write_subs_var.get():
            cmd.append("--write-subs")
            if self.subtitle_langs_var.get().strip():
                cmd.extend(["--sub-langs", self.subtitle_langs_var.get().strip()])
            if self.subtitle_format_var.get().strip():
                cmd.extend(["--sub-format", self.subtitle_format_var.get().strip()])

        if self.write_auto_subs_var.get():
            cmd.append("--write-auto-subs")

        if self.media_profile_var.get() == "plex_emby":
            # Keep metadata files next to each item for media servers.
            cmd.extend(["--write-info-json", "--write-description", "--write-thumbnail"])

        if self.restrict_filenames_var.get():
            cmd.append("--restrict-filenames")

        if self.proxy_enabled_var.get() and self.proxy_var.get().strip():
            cmd.extend(["--proxy", self.proxy_var.get().strip()])

        ffmpeg_location = self._detect_ffmpeg_location()
        if ffmpeg_location:
            cmd.extend(["--ffmpeg-location", ffmpeg_location])

        if self.cookies_browser_var.get().strip():
            cmd.extend(["--cookies-from-browser", self.cookies_browser_var.get().strip()])

        if self.cookies_file_var.get().strip():
            cmd.extend(["--cookies", self.cookies_file_var.get().strip()])

        extra = self.extra_args_var.get().strip()
        if extra:
            try:
                cmd.extend(shlex.split(extra))
            except ValueError as exc:
                self.status_var.set(f"Extra args parse error: {exc}")

        if for_check:
            cmd.extend(["--simulate", "--skip-download", "--print", "title"])

        if url:
            cmd.append(url)
        return cmd

    def _refresh_command(self, *_):
        cmd = self._build_command()
        self._set_command_preview(" ".join(shlex.quote(part) for part in cmd))

    def _drain_log_queue(self):
        try:
            while True:
                item = self.log_queue.get_nowait()
                self._append_log(item)
        except queue.Empty:
            pass
        self.after(120, self._drain_log_queue)

    def _read_process_output(self):
        while self.proc and self.proc.stdout:
            line = self.proc.stdout.readline()
            if not line:
                break
            self.log_queue.put(line)
            self._parse_progress(line)

        if self.proc:
            code = self.proc.wait()
            if code == 0:
                self.status_var.set("Completed")
                self.progress_var.set(100.0)
            else:
                self.status_var.set(f"Failed (exit code {code})")
            self.is_downloading = False
            self.proc = None

    def _parse_progress(self, line):
        match = re.search(r"(\d{1,3}\.\d)%", line)
        if match:
            value = max(0.0, min(100.0, float(match.group(1))))
            self.progress_var.set(value)
            self.status_var.set(f"Downloading... {value:.1f}%")
        speed_match = re.search(r"at\s+([\d.]+)\s*(MiB|KiB|GiB)/s", line)
        if speed_match:
            speed_val = float(speed_match.group(1))
            unit = speed_match.group(2)
            self.speed_var.set(f"{speed_val:.2f} {unit}/s")

    def _validate_start(self):
        if self.is_downloading:
            messagebox.showwarning("Already running", "A download is already running.")
            return False

        if not self.url_var.get().strip():
            messagebox.showerror("Missing URL", "Please provide at least one URL.")
            return False

        if getattr(sys, "frozen", False) and self.base_command == [sys.executable, "-m", "yt_dlp"]:
            messagebox.showerror(
                "Missing yt-dlp runtime",
                "Portable build requires bundled yt-dlp.exe next to this app.\n"
                "Place yt-dlp.exe near the executable and restart.",
            )
            return False

        out_dir = self.output_path_var.get().strip()
        if not out_dir:
            messagebox.showerror("Missing output path", "Please choose an output directory.")
            return False

        try:
            Path(out_dir).mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            messagebox.showerror("Invalid output path", f"Cannot create output directory:\n{exc}")
            return False
        return True

    def start_download(self):
        self._refresh_command()
        if not self._validate_start():
            return

        cmd = self._build_command()
        self._append_log("\n" + "=" * 74 + "\n")
        self._append_log("Starting command:\n")
        self._append_log(" ".join(shlex.quote(part) for part in cmd) + "\n\n")

        self.status_var.set("Starting...")
        self.progress_var.set(0.0)
        self.is_downloading = True

        creation_flags = 0
        startup_info = None
        if os.name == "nt":
            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        self.proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding=self.proc_encoding,
            errors="replace",
            bufsize=1,
            creationflags=creation_flags,
            startupinfo=startup_info,
        )

        threading.Thread(target=self._read_process_output, daemon=True).start()

    def stop_download(self):
        if self.proc and self.is_downloading:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(self.proc.pid), "/T", "/F"], capture_output=True, text=True, check=False)
            else:
                self.proc.terminate()
            self.status_var.set("Stopping...")
            self.log_queue.put("[gui] Termination requested by user.\n")

    def check_url(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Missing URL", "Enter URL first.")
            return
        cmd = self._build_command(for_check=True)
        self._append_log("\n[gui] Checking URL metadata...\n")
        self._append_log(" ".join(shlex.quote(part) for part in cmd) + "\n")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding=self.proc_encoding,
                errors="replace",
                check=False,
            )
            if result.stdout:
                self._append_log(result.stdout + ("\n" if not result.stdout.endswith("\n") else ""))
            if result.returncode == 0:
                self.status_var.set("URL check OK")
            else:
                self.status_var.set(f"URL check failed ({result.returncode})")
                if result.stderr:
                    self._append_log(result.stderr + "\n")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Check failed", str(exc))

    def open_output_folder(self):
        path = self.output_path_var.get().strip()
        if not path:
            return
        Path(path).mkdir(parents=True, exist_ok=True)
        os.startfile(path)  # Windows

    def copy_command(self):
        self._refresh_command()
        cmd = self._build_command()
        text = " ".join(shlex.quote(part) for part in cmd)
        self.clipboard_clear()
        self.clipboard_append(text)
        self.status_var.set("Command copied")

    def _on_close(self):
        self._save_settings()
        if self.proc and self.is_downloading:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(self.proc.pid), "/T", "/F"], capture_output=True, text=True, check=False)
            else:
                self.proc.terminate()
        self.destroy()


def main():
    app = YtDlpGui()
    app.mainloop()


if __name__ == "__main__":
    main()
