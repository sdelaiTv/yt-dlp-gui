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
import time
import tempfile
import urllib.request
import io
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

try:
    from PIL import Image, ImageTk
except Exception:  # noqa: BLE001
    Image = None
    ImageTk = None


class YtDlpGui(tk.Tk):
    def __init__(self):
        # Windows: set App User Model ID before creating the Tk window so the shell
        # does not group this app under python.exe (feather) — see MSDN + Tk docs.
        self._set_app_user_model_id()
        super().__init__()
        self.title("Electrolab Video Downloader (Based on yt-dlp)")
        self.geometry("1120x760")
        self.minsize(980, 660)
        self.configure(bg="#0e1219")
        self._icon_photo = None  # non-Windows: PhotoImage must stay referenced

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
                "library_folder_checkbox": "Plex/Emby: вложить файл в одноименную папку",
                "template_preview": "Превью итогового шаблона",
                "command_preview": "Предпросмотр команды",
                "status": "Статус",
                "fetch_list": "Получить список",
                "clear_list": "Очистить список",
                "select_all": "Выбрать все",
                "select_none": "Снять все",
                "playlist_items": "Список видео",
                "playlist_count": "Количество",
                "playlist_selected": "Выбрано",
                "playlist_total_size": "Суммарный размер",
                "download_selected": "Скачать выбранные",
                "thumbnail": "Превью",
                "size": "Размер",
                "start_download": "Скачать",
                "stop": "Остановить",
                "check_url": "Проверить URL",
                "open_folder": "Открыть папку",
                "copy_command": "Копировать команду",
                "log": "Лог",
                "status_ready": "Готов",
                "status_starting": "Запуск...",
                "status_stopping": "Остановка...",
                "status_completed": "Готово",
                "status_continuing_queue": "Продолжение очереди...",
                "status_downloading": "Скачивание... {value:.1f}%",
                "status_failed_code": "Ошибка (код {code})",
                "status_extra_args_parse_error": "Ошибка разбора доп. аргументов: {error}",
                "fetch_status_started": "Получение списка...",
                "fetch_status_progress": "Получение списка... {count}",
                "fetch_status_loaded": "Загружено {count} элементов",
                "fetch_status_no_items": "Элементы не найдены",
                "fetch_status_failed_code": "Не удалось получить список (код {code})",
                "fetch_status_no_ytdlp": "yt-dlp не найден",
                "fetch_status_cancelled": "Получение списка отменено",
                "fetch_speed_initial": "Получение: 0 эл/с",
                "fetch_speed_progress": "Получение: {speed:.2f} эл/с | {count}",
                "fetch_speed_done": "Готово: {count} эл.",
                "status_url_check_started": "Проверка URL...",
                "status_url_check_ok": "URL проверен",
                "status_url_check_failed": "Проверка URL не удалась (код {code})",
                "status_command_copied": "Команда скопирована",
                "msg_missing_url_title": "Нет URL",
                "msg_missing_url_text": "Сначала укажите URL.",
                "msg_already_running_title": "Уже выполняется",
                "msg_already_running_dl_text": "Загрузка уже идёт.",
                "msg_already_running_fetch_text": "Получение списка уже идёт.",
                "msg_no_selection_title": "Ничего не выбрано",
                "msg_no_selection_text": "Выберите хотя бы одно видео.",
                "msg_missing_runtime_title": "Нет yt-dlp",
                "msg_missing_runtime_text": "Портативной сборке нужен yt-dlp.exe рядом с приложением.\nПоложите yt-dlp.exe возле .exe и перезапустите.",
                "msg_missing_output_title": "Нет папки для сохранения",
                "msg_missing_output_text": "Выберите папку для сохранения.",
                "msg_invalid_output_title": "Неверная папка",
                "msg_invalid_output_text": "Не удалось создать папку:\n{error}",
                "msg_check_failed_title": "Проверка не удалась",
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
                "library_folder_checkbox": "Plex/Emby: put file in same-name folder",
                "template_preview": "Effective template preview",
                "command_preview": "Command Preview",
                "status": "Status",
                "fetch_list": "Fetch List",
                "clear_list": "Clear List",
                "select_all": "Select All",
                "select_none": "Select None",
                "playlist_items": "Playlist Items",
                "playlist_count": "Count",
                "playlist_selected": "Selected",
                "playlist_total_size": "Total size",
                "download_selected": "Download Selected",
                "thumbnail": "Thumbnail",
                "size": "Size",
                "start_download": "Start Download",
                "stop": "Stop",
                "check_url": "Check URL",
                "open_folder": "Open Folder",
                "copy_command": "Copy Command",
                "log": "Log",
                "status_ready": "Ready",
                "status_starting": "Starting...",
                "status_stopping": "Stopping...",
                "status_completed": "Completed",
                "status_continuing_queue": "Continuing queue...",
                "status_downloading": "Downloading... {value:.1f}%",
                "status_failed_code": "Failed (exit code {code})",
                "status_extra_args_parse_error": "Extra args parse error: {error}",
                "fetch_status_started": "Fetching playlist items...",
                "fetch_status_progress": "Fetching list... {count}",
                "fetch_status_loaded": "Loaded {count} items",
                "fetch_status_no_items": "No items found",
                "fetch_status_failed_code": "List fetch failed ({code})",
                "fetch_status_no_ytdlp": "yt-dlp not found",
                "fetch_status_cancelled": "Fetch cancelled",
                "fetch_speed_initial": "Fetch: 0 items/s",
                "fetch_speed_progress": "Fetch: {speed:.2f} items/s | {count}",
                "fetch_speed_done": "Fetch done: {count} items",
                "status_url_check_started": "Checking URL...",
                "status_url_check_ok": "URL check OK",
                "status_url_check_failed": "URL check failed ({code})",
                "status_command_copied": "Command copied",
                "msg_missing_url_title": "Missing URL",
                "msg_missing_url_text": "Please provide a URL first.",
                "msg_already_running_title": "Already running",
                "msg_already_running_dl_text": "A download is already running.",
                "msg_already_running_fetch_text": "List fetch is already in progress.",
                "msg_no_selection_title": "No selection",
                "msg_no_selection_text": "Select at least one video.",
                "msg_missing_runtime_title": "Missing yt-dlp runtime",
                "msg_missing_runtime_text": "Portable build requires bundled yt-dlp.exe next to this app.\nPlace yt-dlp.exe near the executable and restart.",
                "msg_missing_output_title": "Missing output path",
                "msg_missing_output_text": "Please choose an output directory.",
                "msg_invalid_output_title": "Invalid output path",
                "msg_invalid_output_text": "Cannot create output directory:\n{error}",
                "msg_check_failed_title": "Check failed",
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
                "library_folder_checkbox": "Plex/Emby：将文件放入同名文件夹",
                "template_preview": "最终模板预览",
                "command_preview": "命令预览",
                "status": "状态",
                "fetch_list": "获取列表",
                "clear_list": "清空列表",
                "select_all": "全选",
                "select_none": "取消全选",
                "playlist_items": "视频列表",
                "playlist_count": "数量",
                "playlist_selected": "已选",
                "playlist_total_size": "总大小",
                "download_selected": "下载所选",
                "thumbnail": "预览",
                "size": "大小",
                "start_download": "开始下载",
                "stop": "停止",
                "check_url": "检查 URL",
                "open_folder": "打开文件夹",
                "copy_command": "复制命令",
                "log": "日志",
                "status_ready": "就绪",
                "status_starting": "正在启动...",
                "status_stopping": "正在停止...",
                "status_completed": "已完成",
                "status_continuing_queue": "继续队列...",
                "status_downloading": "下载中... {value:.1f}%",
                "status_failed_code": "失败（代码 {code}）",
                "status_extra_args_parse_error": "额外参数解析错误：{error}",
                "fetch_status_started": "正在获取列表...",
                "fetch_status_progress": "正在获取列表... {count}",
                "fetch_status_loaded": "已加载 {count} 项",
                "fetch_status_no_items": "未找到任何项",
                "fetch_status_failed_code": "获取列表失败（{code}）",
                "fetch_status_no_ytdlp": "未找到 yt-dlp",
                "fetch_status_cancelled": "已取消获取",
                "fetch_speed_initial": "获取：0 项/秒",
                "fetch_speed_progress": "获取：{speed:.2f} 项/秒 | {count}",
                "fetch_speed_done": "已完成：{count} 项",
                "status_url_check_started": "正在检查 URL...",
                "status_url_check_ok": "URL 检查通过",
                "status_url_check_failed": "URL 检查失败（{code}）",
                "status_command_copied": "命令已复制",
                "msg_missing_url_title": "缺少 URL",
                "msg_missing_url_text": "请先填写 URL。",
                "msg_already_running_title": "正在运行",
                "msg_already_running_dl_text": "已有下载在运行。",
                "msg_already_running_fetch_text": "列表获取已在进行中。",
                "msg_no_selection_title": "未选择",
                "msg_no_selection_text": "请至少选择一个视频。",
                "msg_missing_runtime_title": "缺少 yt-dlp",
                "msg_missing_runtime_text": "便携版需要在可执行文件旁放置 yt-dlp.exe。\n请放入并重新启动。",
                "msg_missing_output_title": "缺少保存目录",
                "msg_missing_output_text": "请选择保存目录。",
                "msg_invalid_output_title": "目录无效",
                "msg_invalid_output_text": "无法创建目录：\n{error}",
                "msg_check_failed_title": "检查失败",
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
        self.library_folder_var = tk.BooleanVar(value=False)
        self.template_preview_var = tk.StringVar(value="")
        self._syncing_template = False
        self.status_var = tk.StringVar(value="")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.speed_var = tk.StringVar(value="")
        self.playlist_count_var = tk.StringVar(value="0")
        self.playlist_selected_var = tk.StringVar(value="0")
        self.playlist_total_size_var = tk.StringVar(value="?")

        self.download_playlist_var = tk.BooleanVar(value=True)
        self.embed_metadata_var = tk.BooleanVar(value=False)
        self.write_thumbnail_var = tk.BooleanVar(value=False)
        self.write_subs_var = tk.BooleanVar(value=False)
        self.write_auto_subs_var = tk.BooleanVar(value=False)
        self.restrict_filenames_var = tk.BooleanVar(value=False)
        self.lang_var = tk.StringVar(value=self.lang_code_to_display[self.current_lang])
        self.playlist_entries = []
        self.playlist_images = []
        self.playlist_render_id = 0
        self.pending_urls = []
        self.queue_total = 1
        self.queue_done = 0
        self.current_item_percent = 0.0
        self.current_queue_label = tk.StringVar(value="")
        self.is_fetching = False
        self.fetch_proc = None
        self.fetch_cancel_requested = False
        self.auto_cookies_file = ""
        self.cookies_exporting = False
        self.cookies_export_token = 0
        self._load_settings()
        self._configure_colors()
        self._configure_style()
        self._build_ui()
        self._wire_events()
        if self.cookies_browser_var.get().strip():
            self._on_cookies_browser_changed()
        self._bind_ctrl_shortcuts_layout_agnostic()
        self._set_window_icon()
        self._sync_proxy_state()
        self.status_var.set(self.t("status_ready"))
        self._sync_queue_label()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(120, self._drain_log_queue)

    def _make_collapsible_header(self, card, title_text, default_expanded=False):
        """Create a log-like collapsible header; returns (body_frame, expanded_var)."""
        header = tk.Frame(card, bg=self.card_bg)
        header.pack(fill="x")
        expanded = tk.BooleanVar(value=bool(default_expanded))

        toggle = tk.Label(
            header, text="▼" if expanded.get() else "▶",
            bg=self.card_bg, fg=self.fg_dim,
            font=("Segoe UI", 9), cursor="hand2",
        )
        toggle.pack(side="left")
        tk.Label(header, text=title_text, bg=self.card_bg, fg=self.accent, font=("Segoe UI Semibold", 11)).pack(side="left", padx=(4, 0))

        body = tk.Frame(card, bg=self.card_bg)
        body.pack(fill="x", pady=(6, 0))
        if not expanded.get():
            body.pack_forget()

        def do_toggle(_event=None):
            if expanded.get():
                body.pack_forget()
                toggle.configure(text="▶")
            else:
                body.pack(fill="x", pady=(6, 0))
                toggle.configure(text="▼")
            expanded.set(not expanded.get())

        toggle.bind("<Button-1>", do_toggle)
        header.bind("<Button-1>", do_toggle)
        return body, expanded

    def _sync_queue_label(self):
        total = max(int(self.queue_total or 1), 1)
        done = max(int(self.queue_done or 0), 0)
        cur = min(done + 1, total) if self.is_downloading else min(done, total)
        self.current_queue_label.set(f"{cur} / {total}")

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

    def tf(self, key, **kwargs):
        """Translate and apply str.format with kwargs."""
        template = self.t(key)
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return template

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
        self._bind_scroll_passthrough(entry)
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
        self._bind_scroll_passthrough(combo)
        return combo

    def _bind_scroll_passthrough(self, widget):
        """Prevent widget wheel side-effects and scroll the page instead."""
        widget.bind("<MouseWheel>", self._on_input_mousewheel, add="+")
        widget.bind("<Button-4>", self._on_input_mousewheel_linux, add="+")
        widget.bind("<Button-5>", self._on_input_mousewheel_linux, add="+")

    def _on_input_mousewheel(self, event):
        self._on_mousewheel(event)
        return "break"

    def _on_input_mousewheel_linux(self, event):
        self._on_mousewheel_linux(event)
        return "break"

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
        self._build_playlist_card(self.content_frame)
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
        return "break"

    def _on_mousewheel_linux(self, event):
        if event.num == 4:
            self.scroll_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.scroll_canvas.yview_scroll(1, "units")
        return "break"

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

    def _build_playlist_card(self, parent):
        card = self._card(parent)
        body, _expanded = self._make_collapsible_header(card, self.t("playlist_items"), default_expanded=False)
        body.grid_columnconfigure(0, weight=1)
        row0 = tk.Frame(body, bg=self.card_bg)
        row0.grid(row=0, column=0, columnspan=3, sticky="ew")
        tk.Label(row0, text=f"{self.t('playlist_count')}: ", bg=self.card_bg, fg=self.fg_dim, font=("Segoe UI", 9)).pack(side="left")
        tk.Label(row0, textvariable=self.playlist_count_var, bg=self.card_bg, fg=self.fg_bright, font=("Segoe UI Semibold", 10)).pack(side="left", padx=(2, 12))
        tk.Label(row0, text=f"{self.t('playlist_selected')}: ", bg=self.card_bg, fg=self.fg_dim, font=("Segoe UI", 9)).pack(side="left")
        tk.Label(row0, textvariable=self.playlist_selected_var, bg=self.card_bg, fg=self.fg_bright, font=("Segoe UI Semibold", 10)).pack(side="left", padx=(2, 12))
        tk.Label(row0, text=f"{self.t('playlist_total_size')}: ", bg=self.card_bg, fg=self.fg_dim, font=("Segoe UI", 9)).pack(side="left")
        tk.Label(row0, textvariable=self.playlist_total_size_var, bg=self.card_bg, fg=self.fg_bright, font=("Segoe UI Semibold", 10)).pack(side="left", padx=(2, 0))

        btns = tk.Frame(body, bg=self.card_bg)
        btns.grid(row=1, column=0, columnspan=3, sticky="w", pady=(6, 6))
        self._make_button(btns, self.t("fetch_list"), command=self.fetch_playlist_items, style="default").pack(side="left")
        self._make_button(btns, self.t("clear_list"), command=self.clear_playlist_items, style="default").pack(side="left", padx=(8, 0))
        self._make_button(btns, self.t("select_all"), command=self.select_all_playlist_items, style="default").pack(side="left", padx=(8, 0))
        self._make_button(btns, self.t("select_none"), command=self.deselect_all_playlist_items, style="default").pack(side="left", padx=(8, 0))
        self._make_button(btns, self.t("download_selected"), command=self.start_download_selected, style="accent").pack(side="left", padx=(8, 0))

        self.playlist_canvas = tk.Canvas(body, bg=self.entry_bg, highlightthickness=1, highlightbackground=self.entry_border, bd=0, height=240)
        self.playlist_canvas.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.playlist_scroll = ttk.Scrollbar(body, orient="vertical", command=self.playlist_canvas.yview, style="Vertical.TScrollbar")
        self.playlist_scroll.grid(row=2, column=2, sticky="ns")
        self.playlist_canvas.configure(yscrollcommand=self.playlist_scroll.set)

        self.playlist_container = tk.Frame(self.playlist_canvas, bg=self.entry_bg)
        self.playlist_window = self.playlist_canvas.create_window((0, 0), window=self.playlist_container, anchor="nw")
        self.playlist_container.bind("<Configure>", lambda _e: self.playlist_canvas.configure(scrollregion=self.playlist_canvas.bbox("all")))
        self.playlist_canvas.bind("<Configure>", lambda e: self.playlist_canvas.itemconfigure(self.playlist_window, width=e.width))
        self.playlist_canvas.bind("<MouseWheel>", self._on_playlist_mousewheel, add="+")
        self.playlist_canvas.bind("<Button-4>", self._on_playlist_mousewheel_linux, add="+")
        self.playlist_canvas.bind("<Button-5>", self._on_playlist_mousewheel_linux, add="+")
        self.playlist_container.bind("<MouseWheel>", self._on_playlist_mousewheel, add="+")
        self.playlist_container.bind("<Button-4>", self._on_playlist_mousewheel_linux, add="+")
        self.playlist_container.bind("<Button-5>", self._on_playlist_mousewheel_linux, add="+")

    def _on_playlist_mousewheel(self, event):
        if event.delta:
            self.playlist_canvas.yview_scroll(int(-event.delta / 120), "units")
        return "break"

    def _on_playlist_mousewheel_linux(self, event):
        if event.num == 4:
            self.playlist_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.playlist_canvas.yview_scroll(1, "units")
        return "break"

    def _build_options_card(self, parent):
        card = self._card(parent)
        body, _expanded = self._make_collapsible_header(card, self.t("download_mode"), default_expanded=False)
        body.grid_columnconfigure(0, weight=1, uniform="col")
        body.grid_columnconfigure(1, weight=1, uniform="col")
        body.grid_columnconfigure(2, weight=1, uniform="col")
        body.grid_rowconfigure(0, weight=1)

        # Row 0: Mode, Video, Audio
        mode_frame = tk.Frame(body, bg=self.card_bg)
        mode_frame.grid(row=0, column=0, sticky="nsew", padx=8)
        mode_frame.grid_rowconfigure(10, weight=1)
        tk.Label(mode_frame, text=self.t("download_mode"), bg=self.card_bg, fg=self.fg_dim, font=("Segoe UI", 9)).pack(anchor="w")
        ttk.Radiobutton(mode_frame, text=self.t("video_audio"), value="video", variable=self.download_mode_var, command=self._on_download_mode_changed).pack(anchor="w")
        ttk.Radiobutton(mode_frame, text=self.t("audio_only"), value="audio", variable=self.download_mode_var, command=self._on_download_mode_changed).pack(anchor="w")
        # spacer to fill remaining height
        tk.Frame(mode_frame, bg=self.card_bg).pack(expand=True)

        vframe = tk.Frame(body, bg=self.card_bg)
        vframe.grid(row=0, column=1, sticky="nsew", padx=8)
        vframe.grid_rowconfigure(10, weight=1)
        self.video_section_frame = vframe
        video_title = tk.Label(vframe, text=self.t("video_settings"), bg=self.card_bg, fg=self.fg_dim, font=("Segoe UI", 9))
        video_title.pack(anchor="w")
        video_format_label = tk.Label(vframe, text=self.t("video_format"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9))
        video_format_label.pack(anchor="w", pady=(4, 0))
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
        self.video_section_labels = [video_title, video_format_label]

        aframe = tk.Frame(body, bg=self.card_bg)
        aframe.grid(row=0, column=2, sticky="nsew", padx=8)
        aframe.grid_rowconfigure(10, weight=1)
        self.audio_section_frame = aframe
        audio_title = tk.Label(aframe, text=self.t("audio_settings"), bg=self.card_bg, fg=self.fg_dim, font=("Segoe UI", 9))
        audio_title.pack(anchor="w")
        audio_format_label = tk.Label(aframe, text=self.t("audio_format"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9))
        audio_format_label.pack(anchor="w", pady=(4, 0))
        self.audio_format_combo = self._make_combobox(aframe, self.audio_format_var, ["best", "mp3", "m4a", "aac", "flac", "opus", "vorbis", "wav"])
        self.audio_format_combo.pack(fill="x", pady=(2, 4))
        audio_quality_label = tk.Label(aframe, text=self.t("audio_quality"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9))
        audio_quality_label.pack(anchor="w")
        self.audio_quality_combo = self._make_combobox(aframe, self.audio_quality_var, ["0", "1", "2", "3", "4", "5", "7", "10", "96K", "128K", "160K", "192K", "256K", "320K"], width=10)
        self.audio_quality_combo.pack(anchor="w", pady=(2, 0))
        tk.Frame(aframe, bg=self.card_bg).pack(expand=True)
        self.audio_section_labels = [audio_title, audio_format_label, audio_quality_label]

        # Row 1: toggles
        toggles = tk.Frame(body, bg=self.card_bg)
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
        sub_frame = tk.Frame(body, bg=self.card_bg)
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
        body, _expanded = self._make_collapsible_header(card, self.t("advanced"), default_expanded=False)
        body.grid_columnconfigure(0, weight=1, uniform="col")
        body.grid_columnconfigure(1, weight=1, uniform="col")

        ttk.Checkbutton(body, text=self.t("use_proxy"), variable=self.proxy_enabled_var, command=self._sync_proxy_state).grid(row=0, column=0, columnspan=2, sticky="w", pady=(4, 2))

        # Pair 1: proxy address <-> cookies browser
        tk.Label(body, text=self.t("proxy_address"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(2, 0))
        tk.Label(body, text=self.t("cookies_browser"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(2, 0))

        self.proxy_entry = self._make_entry(body, self.proxy_var)
        self.proxy_entry.grid(row=2, column=0, sticky="ew", padx=(0, 8))
        self.proxy_entry.configure(highlightthickness=1, bd=0)
        cookie_browser_combo = self._make_combobox(body, self.cookies_browser_var, ["", "firefox", "chrome", "chromium", "edge", "opera", "brave", "vivaldi", "safari"])
        cookie_browser_combo.grid(row=2, column=1, sticky="ew", padx=(8, 0))
        cookie_browser_combo.bind("<<ComboboxSelected>>", self._on_cookies_browser_changed)

        # Pair 2: extra args <-> cookies file
        tk.Label(body, text=self.t("extra_args"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).grid(row=3, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        tk.Label(body, text=self.t("cookies_file"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).grid(row=3, column=1, sticky="w", padx=(8, 0), pady=(8, 0))

        extra_entry = self._make_entry(body, self.extra_args_var)
        extra_entry.grid(row=4, column=0, sticky="ew", padx=(0, 8))
        extra_entry.configure(highlightthickness=1, bd=0)

        cookie_file_frame = tk.Frame(body, bg=self.card_bg)
        cookie_file_frame.grid(row=4, column=1, sticky="ew", padx=(8, 0))
        cookie_file_entry = self._make_entry(cookie_file_frame, self.cookies_file_var)
        cookie_file_entry.pack(side="left", fill="x", expand=True)
        cookie_file_entry.configure(highlightthickness=1, bd=0)
        self._make_button(cookie_file_frame, "…", command=self._pick_cookie_file, style="default", padx=8, width=3).pack(side="right", padx=(6, 0))

    def _build_naming_card(self, parent):
        card = self._card(parent)
        body, _expanded = self._make_collapsible_header(card, self.t("naming"), default_expanded=False)
        body.grid_columnconfigure(0, weight=1, uniform="col")
        body.grid_columnconfigure(1, weight=1, uniform="col")

        tk.Label(body, text=self.t("template_preset"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", padx=(0, 8))
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
        self.filename_preset_combo = self._make_combobox(body, self.filename_preset_label_var, [label for _, label in preset_values])
        self.filename_preset_combo.grid(row=1, column=0, sticky="ew", padx=(0, 8))
        self.filename_preset_combo.bind("<<ComboboxSelected>>", self._on_template_preset_changed)
        self.library_folder_check = ttk.Checkbutton(
            body,
            text=self.t("library_folder_checkbox"),
            variable=self.library_folder_var,
            command=self._on_library_folder_toggled,
        )
        self.library_folder_check.grid(row=2, column=0, sticky="w", padx=(0, 8), pady=(6, 0))

        tk.Label(body, text=self.t("filename_template"), bg=self.card_bg, fg=self.fg, font=("Segoe UI", 9)).grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))
        template_entry = self._make_entry(body, self.filename_template_var)
        template_entry.grid(row=4, column=0, columnspan=2, sticky="ew")
        template_entry.configure(highlightthickness=1, bd=0)
        template_entry.bind("<KeyRelease>", self._on_template_manual_edit)

        tk.Label(body, text=self.t("template_preview"), bg=self.card_bg, fg=self.fg_dim, font=("Segoe UI", 9)).grid(row=5, column=0, columnspan=2, sticky="w", pady=(8, 0))
        preview = self._make_entry(body, self.template_preview_var)
        preview.grid(row=6, column=0, columnspan=2, sticky="ew")
        preview.configure(state="readonly", readonlybackground=self.entry_bg, disabledforeground=self.fg_dim, highlightthickness=1, bd=0)
        self._sync_template_with_preset()

    def _build_command_card(self, parent):
        card = self._card(parent)
        body, _expanded = self._make_collapsible_header(card, self.t("command_preview"), default_expanded=False)
        self.command_preview = tk.Text(
            body, height=3,
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
        tk.Label(top, textvariable=self.current_queue_label, bg=self.card_bg, fg=self.fg_dim, font=("Segoe UI", 9)).pack(side="left", padx=(10, 0))
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
            self.library_folder_var,
            self.download_playlist_var,
            self.embed_metadata_var,
            self.write_thumbnail_var,
            self.write_subs_var,
            self.write_auto_subs_var,
            self.restrict_filenames_var,
        ):
            var.trace_add("write", self._on_settings_changed)
        self.cookies_browser_var.trace_add("write", self._on_cookies_browser_changed)

    def _on_cookies_browser_changed(self, *_):
        browser = self.cookies_browser_var.get().strip()
        self.cookies_export_token += 1
        token = self.cookies_export_token
        if not browser:
            self.auto_cookies_file = ""
            return
        self.cookies_exporting = True
        self.log_queue.put(f"[gui] Exporting cookies from browser: {browser}\n")
        threading.Thread(
            target=self._export_browser_cookies_worker,
            args=(browser, token),
            daemon=True,
        ).start()

    def _cleanup_auto_cookies_file(self):
        if not self.auto_cookies_file:
            return
        try:
            Path(self.auto_cookies_file).unlink(missing_ok=True)
        except OSError:
            pass

    def _export_browser_cookies_worker(self, browser, token):
        tmp_path = ""
        try:
            fd, tmp_path = tempfile.mkstemp(prefix="yt_dlp_gui_cookies_", suffix=".txt")
            os.close(fd)
            cmd = list(self.base_command) + [
                "--skip-download",
                "--no-warnings",
                "--cookies-from-browser",
                browser,
                "--cookies",
                tmp_path,
                "https://www.youtube.com",
            ]
            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
            startup_info = None
            if os.name == "nt":
                startup_info = subprocess.STARTUPINFO()
                startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding=self.proc_encoding,
                errors="replace",
                check=False,
                creationflags=creation_flags,
                startupinfo=startup_info,
                timeout=60,
            )
            if token != self.cookies_export_token:
                try:
                    Path(tmp_path).unlink(missing_ok=True)
                except OSError:
                    pass
                return
            if result.returncode == 0 and Path(tmp_path).exists() and Path(tmp_path).stat().st_size > 0:
                self._cleanup_auto_cookies_file()
                self.auto_cookies_file = tmp_path
                self.log_queue.put(f"[gui] Browser cookies exported successfully: {tmp_path}\n")
            else:
                try:
                    Path(tmp_path).unlink(missing_ok=True)
                except OSError:
                    pass
                self.auto_cookies_file = ""
                self.log_queue.put("[gui] Browser cookies export failed. Will fallback to --cookies-from-browser.\n")
                if result.stderr:
                    self.log_queue.put(result.stderr if result.stderr.endswith("\n") else result.stderr + "\n")
        except Exception as exc:  # noqa: BLE001
            if tmp_path:
                try:
                    Path(tmp_path).unlink(missing_ok=True)
                except OSError:
                    pass
            self.auto_cookies_file = ""
            self.log_queue.put(f"[gui] Browser cookies export error: {exc!r}\n")
        finally:
            self.cookies_exporting = False

    def _bind_ctrl_shortcuts_layout_agnostic(self):
        self.bind_all("<Control-KeyPress>", self._on_ctrl_keypress, add="+")

    def _on_language_changed(self, _event):
        selected = self.lang_var.get()
        self.current_lang = self.lang_display_to_code.get(selected, "ru")
        self._build_ui()
        self._refresh_command()
        self.status_var.set(self.t("status_ready"))
        self._save_settings()

    def _on_template_preset_changed(self, _event):
        selected_label = self.filename_preset_label_var.get()
        selected_key = self.template_label_to_key.get(selected_label, "title_id")
        self.filename_preset_var.set(selected_key)
        self._apply_template_preset(selected_key)
        self._on_settings_changed()

    def _on_library_folder_toggled(self):
        template = self.filename_template_var.get().strip() or "%(title)s.%(ext)s"
        if self.library_folder_var.get():
            self.filename_template_var.set(self._folderize_template(template))
        else:
            self.filename_template_var.set(self._unfolderize_template(template))
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
            base = templates.get(preset_key, templates["title_id"])
            if self.library_folder_var.get():
                base = self._folderize_template(base)
            self.filename_template_var.set(base)
        self._update_template_preview()

    def _folderize_template(self, template):
        t = (template or "").strip()
        if not t:
            t = "%(title)s.%(ext)s"
        if "/" in t or "\\" in t:
            return t
        suffix = ".%(ext)s"
        stem = t[:-len(suffix)] if t.endswith(suffix) else t
        return f"{stem}/{t}"

    def _unfolderize_template(self, template):
        t = (template or "").strip()
        if "/" not in t:
            return t
        left, right = t.split("/", 1)
        suffix = ".%(ext)s"
        rstem = right[:-len(suffix)] if right.endswith(suffix) else right
        if left == rstem:
            return right
        return t

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
        active_bg = self.card_bg
        inactive_bg = self.bg2
        if mode == "audio":
            self.video_format_combo.configure(state="disabled")
            self.audio_format_combo.configure(state="readonly")
            self.audio_quality_combo.configure(state="readonly")
            self.video_section_frame.configure(bg=inactive_bg)
            self.audio_section_frame.configure(bg=active_bg)
            for label in self.video_section_labels:
                label.configure(bg=inactive_bg, fg=self.fg_dim)
            for label in self.audio_section_labels:
                label.configure(bg=active_bg, fg=self.fg if label is not self.audio_section_labels[0] else self.accent_hover)
        else:
            self.video_format_combo.configure(state="readonly")
            self.audio_format_combo.configure(state="disabled")
            self.audio_quality_combo.configure(state="disabled")
            self.video_section_frame.configure(bg=active_bg)
            self.audio_section_frame.configure(bg=inactive_bg)
            for label in self.video_section_labels:
                label.configure(bg=active_bg, fg=self.fg if label is not self.video_section_labels[0] else self.accent_hover)
            for label in self.audio_section_labels:
                label.configure(bg=inactive_bg, fg=self.fg_dim)

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

    def _format_duration(self, seconds):
        try:
            s = int(seconds or 0)
        except (TypeError, ValueError):
            return "--:--"
        h, rem = divmod(s, 3600)
        m, sec = divmod(rem, 60)
        if h:
            return f"{h:02d}:{m:02d}:{sec:02d}"
        return f"{m:02d}:{sec:02d}"

    def _format_size(self, size_bytes):
        try:
            size = float(size_bytes or 0)
        except (TypeError, ValueError):
            return "?"
        if size <= 0:
            return "?"
        units = ["B", "KB", "MB", "GB", "TB"]
        idx = 0
        while size >= 1024 and idx < len(units) - 1:
            size /= 1024.0
            idx += 1
        return f"{size:.1f} {units[idx]}"

    def _extract_entry_size(self, item):
        """Best effort: use exact size, approx size, then bitrate*duration estimate."""
        if not isinstance(item, dict):
            return None
        direct = item.get("filesize") or item.get("filesize_approx")
        if direct:
            return direct
        duration = item.get("duration")
        tbr = item.get("tbr")
        try:
            if duration and tbr:
                # tbr is in kbit/s in yt-dlp metadata.
                return float(duration) * (float(tbr) * 1000.0 / 8.0)
        except (TypeError, ValueError):
            return None
        return None

    def _build_thumbnail_opener(self):
        """Build a urllib opener that honours the GUI proxy (or system proxy)."""
        proxy = ""
        if self.proxy_enabled_var.get() and self.proxy_var.get().strip():
            proxy = self.proxy_var.get().strip()
            if "://" not in proxy:
                proxy = "http://" + proxy
        handlers = []
        if proxy:
            handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
        else:
            handlers.append(urllib.request.ProxyHandler())
        return urllib.request.build_opener(*handlers)

    def _download_thumbnail(self, url):
        if not url or Image is None:
            return None
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"
                    ),
                    "Accept": "image/avif,image/webp,image/*,*/*;q=0.8",
                },
            )
            opener = self._build_thumbnail_opener()
            with opener.open(req, timeout=15) as resp:
                raw = resp.read()
            img = Image.open(io.BytesIO(raw))
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")
            img.thumbnail((96, 54), Image.Resampling.LANCZOS)
            return img
        except Exception as exc:  # noqa: BLE001
            try:
                self.log_queue.put(f"[gui] thumb fail: {url} -> {exc!r}\n")
            except Exception:  # noqa: BLE001
                pass
            return None

    def _extract_entries_from_json(self, data):
        if isinstance(data, dict) and isinstance(data.get("entries"), list):
            return data.get("entries") or []
        if isinstance(data, dict):
            return [data]
        return []

    def fetch_playlist_items(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror(self.t("msg_missing_url_title"), self.t("msg_missing_url_text"))
            return
        if self.is_fetching:
            messagebox.showwarning(self.t("msg_already_running_title"), self.t("msg_already_running_fetch_text"))
            return
        self.is_fetching = True
        self.fetch_cancel_requested = False
        self.status_var.set(self.t("fetch_status_started"))
        self.speed_var.set(self.t("fetch_speed_initial"))
        self._start_fetch_indicator()
        self.log_queue.put(f"[gui] Fetch list: {url}\n")
        threading.Thread(target=self._fetch_playlist_worker, args=(url,), daemon=True).start()

    def _start_fetch_indicator(self):
        try:
            self.progress.configure(mode="indeterminate")
            self.progress.start(80)
        except tk.TclError:
            pass

    def _stop_fetch_indicator(self):
        try:
            self.progress.stop()
            self.progress.configure(mode="determinate")
            self.progress_var.set(0.0)
        except tk.TclError:
            pass

    def _finish_fetch(self, status_text, entries=None, expand_log_on_error=False):
        self.is_fetching = False
        self.fetch_proc = None
        self._stop_fetch_indicator()
        self.status_var.set(status_text)
        if entries is not None:
            self._populate_playlist_entries(entries)
            if entries:
                self.speed_var.set(self.tf("fetch_speed_done", count=len(entries)))
        if expand_log_on_error:
            self._expand_log()

    def _expand_log(self):
        if hasattr(self, "log_expanded") and not self.log_expanded.get():
            try:
                self.log_text.pack(fill="both", expand=True, pady=(6, 0))
                self.log_toggle_btn.configure(text="▼")
                self.log_expanded.set(True)
            except tk.TclError:
                pass

    def _fetch_playlist_worker(self, url):
        def build_fetch_cmd(include_browser_cookies=True):
            cmd_local = list(self.base_command) + [
                "--dump-json",
                "--skip-download",
                "--yes-playlist",
                "--no-warnings",
                "--ignore-errors",
                "--no-abort-on-error",
            ]
            if self.proxy_enabled_var.get() and self.proxy_var.get().strip():
                cmd_local.extend(["--proxy", self.proxy_var.get().strip()])
            ffmpeg_location_local = self._detect_ffmpeg_location()
            if ffmpeg_location_local:
                cmd_local.extend(["--ffmpeg-location", ffmpeg_location_local])
            manual_cookies = self.cookies_file_var.get().strip()
            auto_cookies = self.auto_cookies_file.strip()
            browser_cookies = self.cookies_browser_var.get().strip()
            if manual_cookies:
                cmd_local.extend(["--cookies", manual_cookies])
            elif auto_cookies:
                cmd_local.extend(["--cookies", auto_cookies])
            elif include_browser_cookies and browser_cookies:
                cmd_local.extend(["--cookies-from-browser", browser_cookies])
            extra_local = self.extra_args_var.get().strip()
            if extra_local:
                try:
                    cmd_local.extend(shlex.split(extra_local))
                except ValueError as exc:
                    self.log_queue.put(f"[gui] Extra args parse error in fetch: {exc}\n")
            cmd_local.append(url)
            return cmd_local

        def run_fetch_once(cmd):
            self.log_queue.put(f"[gui] $ {' '.join(shlex.quote(p) for p in cmd)}\n")
            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
            startup_info = None
            if os.name == "nt":
                startup_info = subprocess.STARTUPINFO()
                startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            try:
                proc_local = subprocess.Popen(
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
            except FileNotFoundError as exc:
                self.log_queue.put(f"[gui] yt-dlp not found: {exc}\n")
                self.after(0, lambda: self._finish_fetch(self.t("fetch_status_no_ytdlp"), expand_log_on_error=True))
                return None, [], False
            except Exception as exc:  # noqa: BLE001
                self.log_queue.put(f"[gui] Fetch error: {exc!r}\n")
                self.after(0, lambda: self._finish_fetch(self.tf("fetch_status_failed_code", code="?"), expand_log_on_error=True))
                return None, [], False

            self.fetch_proc = proc_local
            started = time.monotonic()
            entries_local = []
            cookie_copy_error_local = False

            if proc_local.stdout:
                for raw_line in proc_local.stdout:
                    if self.fetch_cancel_requested:
                        break
                    line = raw_line.strip()
                    if not line:
                        continue
                    if "Could not copy" in line and "cookie database" in line.lower():
                        cookie_copy_error_local = True
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        self.log_queue.put(raw_line if raw_line.endswith("\n") else raw_line + "\n")
                        continue

                    idx = len(entries_local) + 1
                    if not isinstance(item, dict):
                        continue
                    eurl = item.get("webpage_url") or item.get("url") or item.get("original_url")
                    if not eurl:
                        vid = item.get("id")
                        if vid:
                            eurl = f"https://www.youtube.com/watch?v={vid}"
                    if not eurl:
                        continue

                    thumb = item.get("thumbnail")
                    if not thumb:
                        thumbs = item.get("thumbnails")
                        if isinstance(thumbs, list) and thumbs:
                            last = thumbs[-1]
                            if isinstance(last, dict):
                                thumb = last.get("url")
                    if not thumb:
                        vid = item.get("id")
                        if vid:
                            thumb = f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg"

                    size_bytes = self._extract_entry_size(item)
                    entries_local.append({
                        "index": idx,
                        "title": item.get("title") or f"Item {idx}",
                        "url": eurl,
                        "duration": self._format_duration(item.get("duration")),
                        "size": self._format_size(size_bytes),
                        "size_bytes": float(size_bytes or 0) if size_bytes else 0.0,
                        "thumbnail": thumb or "",
                    })
                    elapsed = max(time.monotonic() - started, 0.001)
                    per_sec = len(entries_local) / elapsed
                    self.after(
                        0,
                        lambda count=len(entries_local), speed=per_sec: self.speed_var.set(self.tf("fetch_speed_progress", speed=speed, count=count)),
                    )
                    self.after(0, lambda count=len(entries_local): self.status_var.set(self.tf("fetch_status_progress", count=count)))

            code_local = proc_local.wait()
            return code_local, entries_local, cookie_copy_error_local

        code, entries, cookie_copy_error = run_fetch_once(build_fetch_cmd(include_browser_cookies=True))
        if code is None:
            return
        if code != 0 and not entries and cookie_copy_error and self.cookies_browser_var.get().strip():
            self.log_queue.put("[gui] Browser cookies failed; retrying fetch without --cookies-from-browser.\n")
            code, entries, _ = run_fetch_once(build_fetch_cmd(include_browser_cookies=False))
            if code is None:
                return

        if self.fetch_cancel_requested:
            self.log_queue.put("[gui] Fetch cancelled by user.\n")
            self.after(0, lambda: self._finish_fetch(self.t("fetch_status_cancelled")))
            return

        if code != 0 and not entries:
            self.after(0, lambda rc=code: self._finish_fetch(self.tf("fetch_status_failed_code", code=rc), expand_log_on_error=True))
            return

        for idx, item in enumerate(entries, start=1):
            if not isinstance(item, dict):
                continue
            item["index"] = idx

        self.log_queue.put(f"[gui] Parsed {len(entries)} item(s).\n")
        if not entries:
            self.after(0, lambda: self._finish_fetch(self.t("fetch_status_no_items"), expand_log_on_error=True))
            return
        self.after(0, lambda items=entries: self._finish_fetch(self.tf("fetch_status_loaded", count=len(items)), entries=items))

    def _populate_playlist_entries(self, entries):
        self.clear_playlist_items()
        self.playlist_render_id += 1
        render_id = self.playlist_render_id
        self.playlist_entries = entries
        self.playlist_images = []
        self.playlist_item_by_url = {}
        for row, item in enumerate(entries):
            item["selected"] = tk.BooleanVar(value=True)
            item["selected"].trace_add("write", lambda *_args, self=self: self._update_playlist_summary())
            row_frame = tk.Frame(self.playlist_container, bg=self.entry_bg, padx=6, pady=4)
            row_frame.grid(row=row, column=0, sticky="ew")
            row_frame.grid_columnconfigure(2, weight=1)

            chk = ttk.Checkbutton(row_frame, variable=item["selected"])
            chk.grid(row=0, column=0, rowspan=2, sticky="nw")
            chk.bind("<MouseWheel>", self._on_playlist_mousewheel, add="+")
            chk.bind("<Button-4>", self._on_playlist_mousewheel_linux, add="+")
            chk.bind("<Button-5>", self._on_playlist_mousewheel_linux, add="+")

            lbl_img = tk.Label(
                row_frame,
                text="...",
                bg="#232a3b",
                fg=self.fg_dim,
                anchor="center",
                compound="center",
                width=96, height=54,
                font=("Segoe UI", 8),
            )
            lbl_img.grid(row=0, column=1, rowspan=2, sticky="w", padx=(6, 10))
            lbl_img.bind("<MouseWheel>", self._on_playlist_mousewheel, add="+")
            lbl_img.bind("<Button-4>", self._on_playlist_mousewheel_linux, add="+")
            lbl_img.bind("<Button-5>", self._on_playlist_mousewheel_linux, add="+")
            thumb_url = item.get("thumbnail") or ""
            if thumb_url:
                threading.Thread(
                    target=self._load_thumbnail_async,
                    args=(thumb_url, lbl_img, render_id),
                    daemon=True,
                ).start()

            title_lbl = tk.Label(row_frame, text=item["title"], bg=self.entry_bg, fg=self.fg_bright, anchor="w", justify="left", wraplength=560, font=("Segoe UI", 9, "bold"))
            title_lbl.grid(row=0, column=2, sticky="w")
            title_lbl.bind("<MouseWheel>", self._on_playlist_mousewheel, add="+")
            title_lbl.bind("<Button-4>", self._on_playlist_mousewheel_linux, add="+")
            title_lbl.bind("<Button-5>", self._on_playlist_mousewheel_linux, add="+")
            meta = f"#{item['index']}  |  {item['duration']}  |  {self.t('size')}: {item['size']}"
            meta_lbl = tk.Label(row_frame, text=meta, bg=self.entry_bg, fg=self.fg_dim, anchor="w", font=("Segoe UI", 8))
            meta_lbl.grid(row=1, column=2, sticky="w")
            meta_lbl.bind("<MouseWheel>", self._on_playlist_mousewheel, add="+")
            meta_lbl.bind("<Button-4>", self._on_playlist_mousewheel_linux, add="+")
            meta_lbl.bind("<Button-5>", self._on_playlist_mousewheel_linux, add="+")

            # Per-item progress bar row (initially 0).
            item["progress_var"] = tk.DoubleVar(value=0.0)
            prog = ttk.Progressbar(row_frame, variable=item["progress_var"], maximum=100)
            prog.grid(row=2, column=2, sticky="ew", pady=(2, 0))
            item["progress_bar"] = prog
            item["meta_label"] = meta_lbl
            item["row_frame"] = row_frame
            self.playlist_item_by_url[item["url"]] = item

        self.playlist_count_var.set(str(len(entries)))
        self._update_playlist_summary()

    def _load_thumbnail_async(self, url, label, render_id):
        pil_img = self._download_thumbnail(url)
        if pil_img is None:
            return

        def apply_image():
            if render_id != self.playlist_render_id:
                return
            try:
                if not label.winfo_exists():
                    return
            except tk.TclError:
                return
            if ImageTk is None:
                return
            try:
                img = ImageTk.PhotoImage(pil_img)
            except Exception as exc:  # noqa: BLE001
                self.log_queue.put(f"[gui] thumb apply fail: {exc!r}\n")
                return
            label.configure(
                image=img,
                text="",
                width=img.width(),
                height=img.height(),
            )
            label.image = img
            self.playlist_images.append(img)

        self.after(0, apply_image)

    def clear_playlist_items(self):
        for w in self.playlist_container.winfo_children():
            w.destroy()
        self.playlist_entries = []
        self.playlist_images = []
        self.playlist_count_var.set("0")
        self.playlist_selected_var.set("0")
        self.playlist_total_size_var.set("?")

    def _update_playlist_summary(self):
        total = len(self.playlist_entries)
        selected = 0
        total_bytes = 0.0
        for item in self.playlist_entries:
            if item.get("selected") is not None and item["selected"].get():
                selected += 1
                try:
                    total_bytes += float(item.get("size_bytes", 0.0) or 0.0)
                except (TypeError, ValueError):
                    continue
        self.playlist_count_var.set(str(total))
        self.playlist_selected_var.set(str(selected))
        self.playlist_total_size_var.set(self._format_size(total_bytes) if total_bytes > 0 else "?")

    def select_all_playlist_items(self):
        for item in self.playlist_entries:
            item["selected"].set(True)

    def deselect_all_playlist_items(self):
        for item in self.playlist_entries:
            item["selected"].set(False)

    def start_download_selected(self):
        selected_urls = [item["url"] for item in self.playlist_entries if item["selected"].get()]
        if not selected_urls:
            messagebox.showwarning(self.t("msg_no_selection_title"), self.t("msg_no_selection_text"))
            return
        if self.is_downloading:
            messagebox.showwarning(self.t("msg_already_running_title"), self.t("msg_already_running_dl_text"))
            return
        self.queue_total = len(selected_urls) or 1
        self.queue_done = 0
        self.current_item_percent = 0.0
        self._sync_queue_label()
        self.pending_urls = selected_urls[:]
        self._start_next_pending()

    def _start_next_pending(self):
        if not self.pending_urls:
            self.status_var.set(self.t("status_completed"))
            self.progress_var.set(100.0)
            self.is_downloading = False
            self.queue_done = min(self.queue_done, self.queue_total)
            self._sync_queue_label()
            return
        next_url = self.pending_urls.pop(0)
        self.url_var.set(next_url)
        # reset per-item progress indicator for this URL if it comes from playlist
        item = getattr(self, "playlist_item_by_url", {}).get(next_url)
        if item and item.get("progress_var") is not None:
            item["progress_var"].set(0.0)
            # highlight active row
            try:
                item["row_frame"].configure(bg=self.card_bg)
            except Exception:  # noqa: BLE001
                pass
        self.start_download()

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

    def _set_app_user_model_id(self):
        if os.name != "nt":
            return
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "Electrolab.VideoDownloader.1"
            )
        except Exception:  # noqa: BLE001
            pass

    def _set_window_icon(self):
        """Set window icon the standard Tk way (Microsoft + Tk docs).

        - Windows: ``.ico`` with ``iconbitmap`` (multi-resolution .ico). App User Model ID
          is already set in ``__init__`` before ``Tk()`` so the taskbar is not tied to python.exe.
        - Other OS: ``iconphoto`` from ``.png`` if Pillow is available.
        """
        ico_path = None
        png_path = None
        for base in self._runtime_dirs():
            for rel in (Path("assets/logo-square.ico"), Path("logo-square.ico")):
                candidate = base / rel
                if candidate.exists():
                    ico_path = candidate.resolve()
                    break
            for rel_png in (Path("assets/logo-square.png"), Path("logo-square.png")):
                candidate = base / rel_png
                if candidate.exists():
                    png_path = candidate.resolve()
                    break
            if ico_path or png_path:
                break

        if os.name == "nt" and ico_path is not None:
            path = str(ico_path)
            try:
                self.iconbitmap(default=path)
            except tk.TclError:
                try:
                    self.iconbitmap(path)
                except tk.TclError:
                    pass
            return

        if png_path is not None and Image is not None and ImageTk is not None:
            try:
                self._icon_photo = ImageTk.PhotoImage(Image.open(png_path))
                self.iconphoto(True, self._icon_photo)
            except Exception:  # noqa: BLE001
                pass

    def _detect_yt_dlp_command(self):
        for base in self._runtime_dirs():
            for rel in (
                Path("portable-runtime/yt-dlp.exe"),
                Path("yt-dlp.exe"),
                Path("yt_dlp.exe"),
            ):
                candidate = base / rel
                if candidate.exists():
                    return [str(candidate.resolve())]
        which_path = shutil.which("yt-dlp")
        if which_path:
            return [which_path]
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
        legacy_media = str(data.get("media_profile", "standard"))
        self.library_folder_var.set(bool(data.get("library_folder", legacy_media == "plex_emby")))
        lang = str(data.get("language", "")).strip()
        if lang in self.i18n:
            self.current_lang = lang
            if hasattr(self, "lang_var"):
                self.lang_var.set(self.lang_code_to_display.get(lang, "Русский"))

    def _save_settings(self):
        data = {
            "proxy_address": self.proxy_var.get().strip(),
            "proxy_enabled": bool(self.proxy_enabled_var.get()),
            "filename_preset": self.filename_preset_var.get().strip() or "custom",
            "filename_template": self.filename_template_var.get().strip() or "%(title)s.%(ext)s",
            "library_folder": bool(self.library_folder_var.get()),
            "language": self.current_lang,
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

        if self.library_folder_var.get():
            # Keep metadata files next to each item for media servers.
            cmd.extend(["--write-info-json", "--write-description", "--write-thumbnail"])

        if self.restrict_filenames_var.get():
            cmd.append("--restrict-filenames")

        if self.proxy_enabled_var.get() and self.proxy_var.get().strip():
            cmd.extend(["--proxy", self.proxy_var.get().strip()])

        ffmpeg_location = self._detect_ffmpeg_location()
        if ffmpeg_location:
            cmd.extend(["--ffmpeg-location", ffmpeg_location])

        manual_cookies = self.cookies_file_var.get().strip()
        auto_cookies = self.auto_cookies_file.strip()
        browser_cookies = self.cookies_browser_var.get().strip()
        if manual_cookies:
            cmd.extend(["--cookies", manual_cookies])
        elif auto_cookies:
            cmd.extend(["--cookies", auto_cookies])
        elif browser_cookies:
            cmd.extend(["--cookies-from-browser", browser_cookies])

        extra = self.extra_args_var.get().strip()
        if extra:
            try:
                cmd.extend(shlex.split(extra))
            except ValueError as exc:
                self.status_var.set(self.tf("status_extra_args_parse_error", error=exc))

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
                # mark this item done
                self.queue_done = min(self.queue_done + 1, self.queue_total)
                self.current_item_percent = 0.0
                # mark current playlist item as completed
                cur_url = self.url_var.get().strip()
                item = getattr(self, "playlist_item_by_url", {}).get(cur_url)
                if item:
                    try:
                        if item.get("progress_var") is not None:
                            item["progress_var"].set(100.0)
                        if item.get("meta_label") is not None:
                            item["meta_label"].configure(fg=self.accent)
                    except Exception:  # noqa: BLE001
                        pass
                if self.pending_urls:
                    self.status_var.set(self.t("status_continuing_queue"))
                    self.progress_var.set((self.queue_done / max(self.queue_total, 1)) * 100.0)
                    self.is_downloading = False
                    self.proc = None
                    self._sync_queue_label()
                    self.after(100, self._start_next_pending)
                    return
                self.status_var.set(self.t("status_completed"))
                self.progress_var.set(100.0)
            else:
                self.status_var.set(self.tf("status_failed_code", code=code))
                self.pending_urls = []
            self.is_downloading = False
            self.proc = None
            self._sync_queue_label()

    def _parse_progress(self, line):
        match = re.search(r"(\d{1,3}\.\d)%", line)
        if match:
            value = max(0.0, min(100.0, float(match.group(1))))
            self.current_item_percent = value
            total = max(self.queue_total, 1)
            done = max(self.queue_done, 0)
            overall = ((done + (value / 100.0)) / total) * 100.0
            self.progress_var.set(max(0.0, min(100.0, overall)))
            self.status_var.set(self.tf("status_downloading", value=value))
            self._sync_queue_label()
            # update per-item progress bar in playlist (if this URL came from the list)
            cur_url = self.url_var.get().strip()
            item = getattr(self, "playlist_item_by_url", {}).get(cur_url)
            if item and item.get("progress_var") is not None:
                try:
                    item["progress_var"].set(value)
                except Exception:  # noqa: BLE001
                    pass
        speed_match = re.search(r"at\s+([\d.]+)\s*(MiB|KiB|GiB)/s", line)
        if speed_match:
            speed_val = float(speed_match.group(1))
            unit = speed_match.group(2)
            self.speed_var.set(f"{speed_val:.2f} {unit}/s")

    def _validate_start(self):
        if self.is_downloading:
            messagebox.showwarning(self.t("msg_already_running_title"), self.t("msg_already_running_dl_text"))
            return False

        if not self.url_var.get().strip():
            messagebox.showerror(self.t("msg_missing_url_title"), self.t("msg_missing_url_text"))
            return False

        if getattr(sys, "frozen", False) and self.base_command == [sys.executable, "-m", "yt_dlp"]:
            messagebox.showerror(
                self.t("msg_missing_runtime_title"),
                self.t("msg_missing_runtime_text"),
            )
            return False

        out_dir = self.output_path_var.get().strip()
        if not out_dir:
            messagebox.showerror(self.t("msg_missing_output_title"), self.t("msg_missing_output_text"))
            return False

        try:
            Path(out_dir).mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            messagebox.showerror(self.t("msg_invalid_output_title"), self.tf("msg_invalid_output_text", error=exc))
            return False
        return True

    def start_download(self):
        self._refresh_command()
        if not self._validate_start():
            return

        # If this is a single direct download (not via queue), reset the queue counters.
        if not getattr(self, "pending_urls", None):
            self.queue_total = 1
            self.queue_done = 0
        self.current_item_percent = 0.0
        self._sync_queue_label()

        cmd = self._build_command()
        self._append_log("\n" + "=" * 74 + "\n")
        self._append_log("Starting command:\n")
        self._append_log(" ".join(shlex.quote(part) for part in cmd) + "\n\n")

        self.status_var.set(self.t("status_starting"))
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
        acted = False
        if self.is_fetching and self.fetch_proc is not None:
            self.fetch_cancel_requested = True
            self.pending_urls = []
            self._kill_proc(self.fetch_proc)
            acted = True
        if self.proc and self.is_downloading:
            self.pending_urls = []
            self._kill_proc(self.proc)
            acted = True
        if acted:
            self.status_var.set(self.t("status_stopping"))
            self.log_queue.put("[gui] Termination requested by user.\n")
            self._sync_queue_label()

    def _kill_proc(self, proc):
        try:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                    capture_output=True, text=True, check=False,
                )
            else:
                proc.terminate()
        except Exception as exc:  # noqa: BLE001
            self.log_queue.put(f"[gui] Failed to kill PID {proc.pid}: {exc!r}\n")

    def check_url(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror(self.t("msg_missing_url_title"), self.t("msg_missing_url_text"))
            return
        cmd = self._build_command(for_check=True)
        self.log_queue.put("\n[gui] Checking URL metadata...\n")
        self.log_queue.put(" ".join(shlex.quote(part) for part in cmd) + "\n")
        self.status_var.set(self.t("status_url_check_started"))
        self._start_fetch_indicator()
        threading.Thread(target=self._check_url_worker, args=(cmd,), daemon=True).start()

    def _check_url_worker(self, cmd):
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
        startup_info = None
        if os.name == "nt":
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding=self.proc_encoding,
                errors="replace",
                check=False,
                creationflags=creation_flags,
                startupinfo=startup_info,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            self.log_queue.put("[gui] URL check timed out after 120s.\n")
            self.after(0, lambda: (self._stop_fetch_indicator(), self.status_var.set(self.tf("status_url_check_failed", code="timeout"))))
            return
        except Exception as exc:  # noqa: BLE001
            self.log_queue.put(f"[gui] URL check error: {exc!r}\n")
            self.after(0, lambda: (self._stop_fetch_indicator(), messagebox.showerror(self.t("msg_check_failed_title"), str(exc))))
            return

        if result.stdout:
            self.log_queue.put(result.stdout if result.stdout.endswith("\n") else result.stdout + "\n")
        if result.stderr:
            self.log_queue.put(result.stderr if result.stderr.endswith("\n") else result.stderr + "\n")
        rc = result.returncode

        def finish():
            self._stop_fetch_indicator()
            if rc == 0:
                self.status_var.set(self.t("status_url_check_ok"))
            else:
                self.status_var.set(self.tf("status_url_check_failed", code=rc))
                self._expand_log()

        self.after(0, finish)

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
        self.status_var.set(self.t("status_command_copied"))

    def _on_close(self):
        self._save_settings()
        self._cleanup_auto_cookies_file()
        if self.fetch_proc is not None:
            self.fetch_cancel_requested = True
            self._kill_proc(self.fetch_proc)
        if self.proc and self.is_downloading:
            self._kill_proc(self.proc)
        self.destroy()


def main():
    app = YtDlpGui()
    app.mainloop()


if __name__ == "__main__":
    main()
