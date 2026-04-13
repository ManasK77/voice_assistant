# interfaces/gui_interface.py
"""
GUIInterface — Full-featured tkinter GUI for VoiceAssist.

Provides interactive controls for ALL 35+ assistant capabilities.
Designed against Nielsen's 10 Usability Heuristics:

  H1  Visibility of system status      → Status badge, timestamped log, live stats
  H2  Match system & real world        → Plain action-verb labels, realistic placeholders
  H3  User control & freedom           → Confirmation dialogs, response history
  H4  Consistency & standards          → Uniform styling per domain, Enter = submit
  H5  Error prevention                 → Disabled buttons when input empty, confirmations
  H6  Recognition over recall          → All actions visible as labeled buttons
  H7  Flexibility & efficiency         → Enter-to-submit, keyboard nav, resizable
  H8  Aesthetic & minimalist design    → Only active tab shown, clean dark theme
  H9  Help recognize/recover errors    → Errors in red with plain-language explanation
  H10 Help & documentation             → Per-tab help button, tooltips on controls
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime

import psutil

# Allow running this file directly
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

import config
from core import (
    info_ops,
    system_ops,
    file_ops,
    camera_skill,
    screenshot_ops,
    system_status,
    productivity,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Tooltip — Nielsen H10 (Help & Documentation)
# ═══════════════════════════════════════════════════════════════════════════════

class ToolTip:
    """Hover tooltip for any widget."""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event=None):
        if self.tip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, justify=tk.LEFT,
            background="#2d2d44", foreground="#eaeaea",
            relief=tk.SOLID, borderwidth=1,
            font=("Segoe UI", 9), padx=8, pady=4,
        )
        label.pack()

    def _hide(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


# ═══════════════════════════════════════════════════════════════════════════════
# Help text per domain — Nielsen H10
# ═══════════════════════════════════════════════════════════════════════════════

HELP_TEXT = {
    "Information": (
        "🌐 Information Commands\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "• Time — shows the current time\n"
        "• Date — shows today's date\n"
        "• Weather — fetches weather for a city\n"
        "   (requires API key in config.py)\n"
        "• Web Search — opens Google search\n"
        "   in your default browser"
    ),
    "System": (
        "🖥️ System Control Commands\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "• Volume +/− — adjust system volume by 10%\n"
        "• Mute — toggle system mute\n"
        "• Brightness +/− — adjust screen brightness\n"
        "• Launch App — open any application by name\n"
        "   (e.g. calculator, notepad, chrome)\n"
        "• Terminate App — kill a running process"
    ),
    "Files": (
        "📁 File Management Commands\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "• Create File — creates a .txt file in your\n"
        "   home directory\n"
        "• Read File — reads first 500 characters\n"
        "• Delete File — permanently deletes a file\n"
        "   (confirmation required)\n"
        "• List Files — shows up to 10 files in home dir\n"
        "• New Folder — creates a subdirectory"
    ),
    "Productivity": (
        "✅ Productivity Commands\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "• Calculator — evaluates math expressions\n"
        "   (e.g. 25 * 4, 144 / 12)\n"
        "• Add Task — appends to persistent to-do list\n"
        "• View Tasks — shows all saved tasks\n"
        "• Clear Tasks — removes all tasks\n"
        "   (confirmation required)\n"
        "• Set Reminder — fires a spoken reminder\n"
        "   after N minutes"
    ),
    "Camera": (
        "📷 Camera & Screen Commands\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "• Take Photo — captures from default webcam\n"
        "   (saved to photos/ folder)\n"
        "• Screenshot — captures full screen\n"
        "   (saved to data/screenshots/)\n"
        "• OCR Screen — extracts text from screen\n"
        "   (requires Tesseract OCR installed)"
    ),
    "Monitoring": (
        "📊 System Monitoring Commands\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "• CPU — current processor usage %\n"
        "• RAM — memory usage in GB\n"
        "• Disk — disk usage in GB\n"
        "• Full Status — combined summary\n"
        "• Task Manager — opens OS task manager\n\n"
        "Live stats auto-refresh every 2 seconds."
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# GUIInterface
# ═══════════════════════════════════════════════════════════════════════════════

class GUIInterface:
    """Full-feature GUI interface — mirrors ALL voice assistant capabilities."""

    # ── Color palette ────────────────────────────────────────────────────────
    BG_PRIMARY    = "#1a1a2e"
    BG_SECONDARY  = "#16213e"
    BG_SIDEBAR    = "#0f0f23"
    BG_INPUT      = "#0d1117"
    BG_CARD       = "#1e2a3a"
    ACCENT        = "#e94560"
    TEXT_PRIMARY   = "#eaeaea"
    TEXT_SECONDARY = "#a0a0b0"
    TEXT_DIM       = "#606070"
    SUCCESS       = "#00ff88"
    WARNING       = "#f39c12"
    BORDER        = "#2a2a4a"

    DOMAIN_COLORS = {
        "Information":  "#3498db",
        "System":       "#f39c12",
        "Files":        "#2ecc71",
        "Productivity": "#9b59b6",
        "Camera":       "#1abc9c",
        "Monitoring":   "#e74c3c",
    }

    TABS = [
        ("🌐", "Information"),
        ("🖥️", "System"),
        ("📁", "Files"),
        ("✅", "Productivity"),
        ("📷", "Camera"),
        ("📊", "Monitoring"),
    ]

    FONT        = ("Segoe UI", 10)
    FONT_BOLD   = ("Segoe UI", 10, "bold")
    FONT_HEADER = ("Segoe UI", 14, "bold")
    FONT_SMALL  = ("Segoe UI", 9)
    FONT_LOG    = ("Consolas", 9)

    # ── Constructor ──────────────────────────────────────────────────────────

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VoiceAssist — GUI Interface")
        self.root.geometry("1020x700")
        self.root.minsize(900, 620)
        self.root.configure(bg=self.BG_PRIMARY)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # State
        self.active_tab = None
        self.tab_frames = {}
        self.nav_buttons = {}
        self._last_action = ""

        # Build layout
        self._build_header()
        self._build_body()
        self._build_status_bar()

        # Show first tab
        self._show_tab("Information")

        # Start live stats refresh
        self._update_stats_loop()

    # ═════════════════════════════════════════════════════════════════════════
    # Layout Builders
    # ═════════════════════════════════════════════════════════════════════════

    def _build_header(self):
        """Top header bar with title, mode label, status badge, and help."""
        header = tk.Frame(self.root, bg=self.BG_SECONDARY, pady=10, padx=16)
        header.pack(fill=tk.X)

        # Title
        tk.Label(
            header, text="🎙️  VoiceAssist", font=self.FONT_HEADER,
            bg=self.BG_SECONDARY, fg=self.TEXT_PRIMARY,
        ).pack(side=tk.LEFT)

        # Mode badge
        tk.Label(
            header, text="  GUI Mode  ", font=self.FONT_SMALL,
            bg="#2d2d44", fg=self.TEXT_SECONDARY,
            relief=tk.FLAT, padx=8, pady=2,
        ).pack(side=tk.LEFT, padx=(12, 0))

        # Help button — Nielsen H10
        help_btn = tk.Button(
            header, text=" ? Help ", font=self.FONT_BOLD,
            bg="#2d2d44", fg=self.TEXT_PRIMARY,
            activebackground="#3d3d54", activeforeground="white",
            relief=tk.FLAT, cursor="hand2", padx=8,
            command=self._show_help,
        )
        help_btn.pack(side=tk.RIGHT, padx=(8, 0))
        ToolTip(help_btn, "Show help for the current tab")

        # Status badge — Nielsen H1
        self.status_badge = tk.Label(
            header, text="  🟢 Ready  ", font=self.FONT_SMALL,
            bg="#1a3a1a", fg=self.SUCCESS,
            relief=tk.FLAT, padx=8, pady=2,
        )
        self.status_badge.pack(side=tk.RIGHT)

    def _build_body(self):
        """Main body: sidebar (left) + content area (right)."""
        body = tk.Frame(self.root, bg=self.BG_PRIMARY)
        body.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self._build_sidebar(body)

        # Content area (task panel + response log)
        self._build_content_area(body)

    def _build_sidebar(self, parent):
        """Navigation sidebar with domain tabs."""
        sidebar = tk.Frame(parent, bg=self.BG_SIDEBAR, width=170)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Sidebar header
        tk.Label(
            sidebar, text="NAVIGATION", font=("Segoe UI", 8, "bold"),
            bg=self.BG_SIDEBAR, fg=self.TEXT_DIM, anchor="w", padx=16, pady=10,
        ).pack(fill=tk.X)

        # Tab buttons
        for emoji, name in self.TABS:
            color = self.DOMAIN_COLORS[name]
            btn = tk.Button(
                sidebar, text=f"  {emoji}  {name}",
                font=self.FONT, bg=self.BG_SIDEBAR, fg=self.TEXT_SECONDARY,
                activebackground=self.BG_SECONDARY,
                activeforeground=self.TEXT_PRIMARY,
                relief=tk.FLAT, anchor="w", padx=16, pady=10,
                cursor="hand2",
                command=lambda n=name: self._show_tab(n),
            )
            btn.pack(fill=tk.X)

            # Hover effect
            btn.bind("<Enter>", lambda e, b=btn, c=color: (
                b.configure(bg=self.BG_SECONDARY, fg=c)
                if b != self.nav_buttons.get(self.active_tab) else None
            ))
            btn.bind("<Leave>", lambda e, b=btn: (
                b.configure(bg=self.BG_SIDEBAR, fg=self.TEXT_SECONDARY)
                if b != self.nav_buttons.get(self.active_tab) else None
            ))

            self.nav_buttons[name] = btn

        # Bottom padding
        tk.Frame(sidebar, bg=self.BG_SIDEBAR).pack(fill=tk.BOTH, expand=True)

        # Version label at bottom
        tk.Label(
            sidebar, text="v1.0 — HCI Project",
            font=("Segoe UI", 8), bg=self.BG_SIDEBAR, fg=self.TEXT_DIM,
            padx=16, pady=8,
        ).pack(side=tk.BOTTOM, fill=tk.X)

    def _build_content_area(self, parent):
        """Right-side content: task panel (top) + response log (bottom)."""
        content = tk.Frame(parent, bg=self.BG_PRIMARY)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Task panel container — the active tab frame is packed here
        self.task_container = tk.Frame(content, bg=self.BG_PRIMARY)
        self.task_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(8, 4))

        # Create all tab frames (hidden initially)
        self._create_info_tab()
        self._create_system_tab()
        self._create_files_tab()
        self._create_productivity_tab()
        self._create_camera_tab()
        self._create_monitoring_tab()

        # Separator
        tk.Frame(content, bg=self.BORDER, height=1).pack(fill=tk.X, padx=12)

        # Response log — Nielsen H1 (visibility), H9 (error recovery)
        log_header = tk.Frame(content, bg=self.BG_PRIMARY, pady=4, padx=12)
        log_header.pack(fill=tk.X)
        tk.Label(
            log_header, text="📋  Response Log", font=self.FONT_BOLD,
            bg=self.BG_PRIMARY, fg=self.TEXT_PRIMARY, anchor="w",
        ).pack(side=tk.LEFT)

        log_frame = tk.Frame(content, bg=self.BG_PRIMARY, padx=12)
        log_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 8))

        self.response_log = scrolledtext.ScrolledText(
            log_frame, font=self.FONT_LOG, bg=self.BG_INPUT,
            fg=self.TEXT_PRIMARY, insertbackground=self.TEXT_PRIMARY,
            selectbackground=self.ACCENT, wrap=tk.WORD,
            state=tk.DISABLED, relief=tk.FLAT, borderwidth=0,
            padx=10, pady=8, height=10,
        )
        self.response_log.pack(fill=tk.BOTH, expand=True)

        # Configure log tags for coloring — Nielsen H9
        self.response_log.tag_configure("timestamp", foreground=self.TEXT_DIM)
        self.response_log.tag_configure("success", foreground=self.SUCCESS)
        self.response_log.tag_configure("error", foreground=self.ACCENT)
        self.response_log.tag_configure("info", foreground="#3498db")
        self.response_log.tag_configure("normal", foreground=self.TEXT_PRIMARY)

    def _build_status_bar(self):
        """Bottom status bar with last action, live stats, and status."""
        bar = tk.Frame(self.root, bg=self.BG_SECONDARY, pady=6, padx=16)
        bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Last action
        self.last_action_label = tk.Label(
            bar, text="Last: —", font=self.FONT_SMALL,
            bg=self.BG_SECONDARY, fg=self.TEXT_SECONDARY, anchor="w",
        )
        self.last_action_label.pack(side=tk.LEFT)

        # Ready indicator (right)
        self.bar_status_label = tk.Label(
            bar, text="🟢 Ready", font=self.FONT_SMALL,
            bg=self.BG_SECONDARY, fg=self.SUCCESS,
        )
        self.bar_status_label.pack(side=tk.RIGHT)

        # Live stats (center-right)
        self.bar_stats_label = tk.Label(
            bar, text="CPU: —   RAM: —   Disk: —", font=self.FONT_SMALL,
            bg=self.BG_SECONDARY, fg=self.TEXT_SECONDARY,
        )
        self.bar_stats_label.pack(side=tk.RIGHT, padx=(0, 20))

    # ═════════════════════════════════════════════════════════════════════════
    # Tab Frame Creation
    # ═════════════════════════════════════════════════════════════════════════

    def _create_info_tab(self):
        """Information tab: Time, Date, Weather, Web Search."""
        frame = tk.Frame(self.task_container, bg=self.BG_PRIMARY)
        self.tab_frames["Information"] = frame
        color = self.DOMAIN_COLORS["Information"]

        # Title
        self._make_tab_title(frame, "🌐  Information", color)

        # --- Quick Actions ---
        section1 = self._make_section(frame, "Quick Actions")
        btn_row = tk.Frame(section1, bg=self.BG_CARD)
        btn_row.pack(fill=tk.X, pady=(0, 4))

        time_btn = self._make_button(
            btn_row, "🕐  Time", lambda: self._execute("Time", info_ops.get_time),
            color=color, tooltip="Get the current time",
        )
        time_btn.pack(side=tk.LEFT, padx=(0, 8))

        date_btn = self._make_button(
            btn_row, "📅  Date", lambda: self._execute("Date", info_ops.get_date),
            color=color, tooltip="Get today's date",
        )
        date_btn.pack(side=tk.LEFT)

        # --- Weather ---
        section2 = self._make_section(frame, "Weather")
        weather_row = tk.Frame(section2, bg=self.BG_CARD)
        weather_row.pack(fill=tk.X, pady=(0, 4))

        self.weather_city_var = tk.StringVar(value=config.DEFAULT_CITY)
        tk.Label(
            weather_row, text="City:", font=self.FONT, bg=self.BG_CARD,
            fg=self.TEXT_SECONDARY, width=6, anchor="e",
        ).pack(side=tk.LEFT)
        weather_entry = self._make_entry(weather_row, self.weather_city_var, "e.g. Mumbai")
        weather_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)

        weather_btn = self._make_button(
            weather_row, "🌤  Weather",
            lambda: self._execute("Weather", info_ops.get_weather, self.weather_city_var.get().strip() or None),
            color=color, tooltip="Fetch weather from OpenWeatherMap",
        )
        weather_btn.pack(side=tk.RIGHT)
        weather_entry.bind("<Return>", lambda e: weather_btn.invoke())

        # --- Web Search ---
        section3 = self._make_section(frame, "Web Search")
        search_row = tk.Frame(section3, bg=self.BG_CARD)
        search_row.pack(fill=tk.X, pady=(0, 4))

        self.search_query_var = tk.StringVar()
        tk.Label(
            search_row, text="Query:", font=self.FONT, bg=self.BG_CARD,
            fg=self.TEXT_SECONDARY, width=6, anchor="e",
        ).pack(side=tk.LEFT)
        search_entry = self._make_entry(search_row, self.search_query_var, "e.g. Python programming")
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)

        search_btn = self._make_button(
            search_row, "🔍  Search",
            lambda: self._execute("Web Search", info_ops.web_search, self.search_query_var.get().strip()),
            color=color, tooltip="Search Google in your browser",
        )
        search_btn.pack(side=tk.RIGHT)
        search_entry.bind("<Return>", lambda e: search_btn.invoke())
        # Nielsen H5: disable when empty
        self._bind_entry_to_buttons(self.search_query_var, [search_btn])

    def _create_system_tab(self):
        """System tab: Volume, Brightness, App Launch/Kill."""
        frame = tk.Frame(self.task_container, bg=self.BG_PRIMARY)
        self.tab_frames["System"] = frame
        color = self.DOMAIN_COLORS["System"]

        self._make_tab_title(frame, "🖥️  System Control", color)

        # --- Audio Control ---
        section1 = self._make_section(frame, "Audio Control")
        audio_row = tk.Frame(section1, bg=self.BG_CARD)
        audio_row.pack(fill=tk.X, pady=(0, 4))

        self._make_button(
            audio_row, "🔊  Vol +", lambda: self._execute("Volume Up", system_ops.volume_up),
            color=color, tooltip="Increase volume by 10%",
        ).pack(side=tk.LEFT, padx=(0, 8))
        self._make_button(
            audio_row, "🔉  Vol −", lambda: self._execute("Volume Down", system_ops.volume_down),
            color=color, tooltip="Decrease volume by 10%",
        ).pack(side=tk.LEFT, padx=(0, 8))
        self._make_button(
            audio_row, "🔇  Mute", lambda: self._execute("Mute", system_ops.mute),
            color=color, tooltip="Toggle system mute",
        ).pack(side=tk.LEFT)

        # --- Display ---
        section2 = self._make_section(frame, "Display")
        display_row = tk.Frame(section2, bg=self.BG_CARD)
        display_row.pack(fill=tk.X, pady=(0, 4))

        self._make_button(
            display_row, "☀  Bright +", lambda: self._execute("Brightness Up", system_ops.brightness_up),
            color=color, tooltip="Increase brightness by 10%",
        ).pack(side=tk.LEFT, padx=(0, 8))
        self._make_button(
            display_row, "🌙  Bright −", lambda: self._execute("Brightness Down", system_ops.brightness_down),
            color=color, tooltip="Decrease brightness by 10%",
        ).pack(side=tk.LEFT)

        # --- Applications ---
        section3 = self._make_section(frame, "Applications")

        app_row = tk.Frame(section3, bg=self.BG_CARD)
        app_row.pack(fill=tk.X, pady=(0, 8))

        self.app_name_var = tk.StringVar()
        tk.Label(
            app_row, text="App:", font=self.FONT, bg=self.BG_CARD,
            fg=self.TEXT_SECONDARY, width=6, anchor="e",
        ).pack(side=tk.LEFT)
        app_entry = self._make_entry(app_row, self.app_name_var, "e.g. calculator, chrome")
        app_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)

        launch_btn = self._make_button(
            app_row, "▶  Launch",
            lambda: self._execute("Launch App", system_ops.open_app, self.app_name_var.get().strip()),
            color="#2ecc71", tooltip="Open the application",
        )
        launch_btn.pack(side=tk.LEFT, padx=(0, 6))

        kill_btn = self._make_button(
            app_row, "⏹  Terminate",
            lambda: self._execute("Terminate App", system_ops.close_app, self.app_name_var.get().strip()),
            color=self.ACCENT, tooltip="Kill the running process",
        )
        kill_btn.pack(side=tk.LEFT)

        app_entry.bind("<Return>", lambda e: launch_btn.invoke())
        self._bind_entry_to_buttons(self.app_name_var, [launch_btn, kill_btn])

    def _create_files_tab(self):
        """Files tab: Create, Read, Delete, List Files, Create Folder."""
        frame = tk.Frame(self.task_container, bg=self.BG_PRIMARY)
        self.tab_frames["Files"] = frame
        color = self.DOMAIN_COLORS["Files"]

        self._make_tab_title(frame, "📁  File Management", color)

        # --- File Operations ---
        section1 = self._make_section(frame, "File Operations")

        file_row = tk.Frame(section1, bg=self.BG_CARD)
        file_row.pack(fill=tk.X, pady=(0, 8))

        self.file_name_var = tk.StringVar()
        tk.Label(
            file_row, text="Filename:", font=self.FONT, bg=self.BG_CARD,
            fg=self.TEXT_SECONDARY, width=9, anchor="e",
        ).pack(side=tk.LEFT)
        file_entry = self._make_entry(file_row, self.file_name_var, "e.g. report.txt")
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)

        btn_row = tk.Frame(section1, bg=self.BG_CARD)
        btn_row.pack(fill=tk.X, pady=(0, 4))

        create_btn = self._make_button(
            btn_row, "📄  Create File",
            lambda: self._execute("Create File", file_ops.create_file, self.file_name_var.get().strip()),
            color=color, tooltip="Create a new .txt file in home directory",
        )
        create_btn.pack(side=tk.LEFT, padx=(0, 8))

        read_btn = self._make_button(
            btn_row, "📖  Read File",
            lambda: self._execute("Read File", file_ops.read_file, self.file_name_var.get().strip()),
            color=color, tooltip="Read the first 500 characters of a file",
        )
        read_btn.pack(side=tk.LEFT, padx=(0, 8))

        # Nielsen H3 & H5: Delete requires confirmation
        delete_btn = self._make_button(
            btn_row, "🗑  Delete File",
            lambda: self._delete_file_action(),
            color=self.ACCENT, tooltip="Delete a file (confirmation required)",
        )
        delete_btn.pack(side=tk.LEFT)

        file_entry.bind("<Return>", lambda e: read_btn.invoke())
        self._bind_entry_to_buttons(self.file_name_var, [create_btn, read_btn, delete_btn])

        # --- List Files ---
        section2 = self._make_section(frame, "Directory")
        dir_row = tk.Frame(section2, bg=self.BG_CARD)
        dir_row.pack(fill=tk.X, pady=(0, 8))

        self._make_button(
            dir_row, "📂  List Files",
            lambda: self._execute("List Files", file_ops.list_files),
            color=color, tooltip="List up to 10 files in home directory",
        ).pack(side=tk.LEFT, padx=(0, 8))

        # --- Folder Creation ---
        folder_row = tk.Frame(section2, bg=self.BG_CARD)
        folder_row.pack(fill=tk.X, pady=(0, 4))

        self.folder_name_var = tk.StringVar()
        tk.Label(
            folder_row, text="Folder:", font=self.FONT, bg=self.BG_CARD,
            fg=self.TEXT_SECONDARY, width=9, anchor="e",
        ).pack(side=tk.LEFT)
        folder_entry = self._make_entry(folder_row, self.folder_name_var, "e.g. projects")
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)

        folder_btn = self._make_button(
            folder_row, "📁  New Folder",
            lambda: self._execute("Create Folder", file_ops.create_folder, self.folder_name_var.get().strip()),
            color=color, tooltip="Create a new folder in home directory",
        )
        folder_btn.pack(side=tk.RIGHT)
        folder_entry.bind("<Return>", lambda e: folder_btn.invoke())
        self._bind_entry_to_buttons(self.folder_name_var, [folder_btn])

    def _create_productivity_tab(self):
        """Productivity tab: Calculator, Todos, Reminders."""
        frame = tk.Frame(self.task_container, bg=self.BG_PRIMARY)
        self.tab_frames["Productivity"] = frame
        color = self.DOMAIN_COLORS["Productivity"]

        self._make_tab_title(frame, "✅  Productivity", color)

        # --- Calculator ---
        section1 = self._make_section(frame, "Calculator")
        calc_row = tk.Frame(section1, bg=self.BG_CARD)
        calc_row.pack(fill=tk.X, pady=(0, 4))

        self.calc_expr_var = tk.StringVar()
        tk.Label(
            calc_row, text="Expr:", font=self.FONT, bg=self.BG_CARD,
            fg=self.TEXT_SECONDARY, width=6, anchor="e",
        ).pack(side=tk.LEFT)
        calc_entry = self._make_entry(calc_row, self.calc_expr_var, "e.g. 25 * 4 + 10")
        calc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)

        calc_btn = self._make_button(
            calc_row, "🔢  Calculate",
            lambda: self._execute("Calculate", productivity.calculate, self.calc_expr_var.get().strip()),
            color=color, tooltip="Evaluate a math expression",
        )
        calc_btn.pack(side=tk.RIGHT)
        calc_entry.bind("<Return>", lambda e: calc_btn.invoke())
        self._bind_entry_to_buttons(self.calc_expr_var, [calc_btn])

        # --- To-Do List ---
        section2 = self._make_section(frame, "To-Do List")

        todo_row = tk.Frame(section2, bg=self.BG_CARD)
        todo_row.pack(fill=tk.X, pady=(0, 8))

        self.todo_task_var = tk.StringVar()
        tk.Label(
            todo_row, text="Task:", font=self.FONT, bg=self.BG_CARD,
            fg=self.TEXT_SECONDARY, width=6, anchor="e",
        ).pack(side=tk.LEFT)
        todo_entry = self._make_entry(todo_row, self.todo_task_var, "e.g. Buy groceries")
        todo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)

        add_btn = self._make_button(
            todo_row, "➕  Add Task",
            lambda: self._execute("Add Task", productivity.add_todo, self.todo_task_var.get().strip()),
            color=color, tooltip="Add a task to your to-do list",
        )
        add_btn.pack(side=tk.RIGHT)
        todo_entry.bind("<Return>", lambda e: add_btn.invoke())
        self._bind_entry_to_buttons(self.todo_task_var, [add_btn])

        todo_btn_row = tk.Frame(section2, bg=self.BG_CARD)
        todo_btn_row.pack(fill=tk.X, pady=(0, 4))

        self._make_button(
            todo_btn_row, "📋  View Tasks",
            lambda: self._execute("View Tasks", productivity.show_todos),
            color=color, tooltip="Show all tasks in your to-do list",
        ).pack(side=tk.LEFT, padx=(0, 8))

        # Nielsen H3 & H5: Clear requires confirmation
        self._make_button(
            todo_btn_row, "🗑  Clear All",
            lambda: self._clear_todos_action(),
            color=self.ACCENT, tooltip="Clear all tasks (confirmation required)",
        ).pack(side=tk.LEFT)

        # --- Reminders ---
        section3 = self._make_section(frame, "Reminders")
        reminder_row = tk.Frame(section3, bg=self.BG_CARD)
        reminder_row.pack(fill=tk.X, pady=(0, 4))

        self.reminder_text_var = tk.StringVar()
        tk.Label(
            reminder_row, text="Text:", font=self.FONT, bg=self.BG_CARD,
            fg=self.TEXT_SECONDARY, width=6, anchor="e",
        ).pack(side=tk.LEFT)
        reminder_entry = self._make_entry(reminder_row, self.reminder_text_var, "e.g. Drink water")
        reminder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)

        tk.Label(
            reminder_row, text="Min:", font=self.FONT, bg=self.BG_CARD,
            fg=self.TEXT_SECONDARY,
        ).pack(side=tk.LEFT, padx=(0, 4))

        self.reminder_mins_var = tk.IntVar(value=5)
        mins_spinbox = tk.Spinbox(
            reminder_row, from_=1, to=120, textvariable=self.reminder_mins_var,
            font=self.FONT, bg=self.BG_INPUT, fg=self.TEXT_PRIMARY,
            buttonbackground=self.BG_SECONDARY, width=4,
            relief=tk.FLAT, highlightthickness=1,
            highlightcolor="#9b59b6", highlightbackground="#333",
        )
        mins_spinbox.pack(side=tk.LEFT, padx=(0, 8))

        reminder_btn = self._make_button(
            reminder_row, "⏰  Set",
            lambda: self._set_reminder_action(),
            color=color, tooltip="Set a spoken reminder", width=10,
        )
        reminder_btn.pack(side=tk.RIGHT)
        reminder_entry.bind("<Return>", lambda e: reminder_btn.invoke())
        self._bind_entry_to_buttons(self.reminder_text_var, [reminder_btn])

    def _create_camera_tab(self):
        """Camera tab: Photo, Screenshot, OCR."""
        frame = tk.Frame(self.task_container, bg=self.BG_PRIMARY)
        self.tab_frames["Camera"] = frame
        color = self.DOMAIN_COLORS["Camera"]

        self._make_tab_title(frame, "📷  Camera & Screen", color)

        # --- Webcam ---
        section1 = self._make_section(frame, "Webcam")
        cam_row = tk.Frame(section1, bg=self.BG_CARD)
        cam_row.pack(fill=tk.X, pady=(0, 4))

        self._make_button(
            cam_row, "📷  Take Photo",
            lambda: self._execute("Take Photo", camera_skill.capture_photo),
            color=color, tooltip="Capture photo from default webcam",
        ).pack(side=tk.LEFT)

        # --- Screen Capture ---
        section2 = self._make_section(frame, "Screen Capture")
        screen_row = tk.Frame(section2, bg=self.BG_CARD)
        screen_row.pack(fill=tk.X, pady=(0, 4))

        self._make_button(
            screen_row, "🖥  Screenshot",
            lambda: self._execute("Screenshot", screenshot_ops.take_screenshot),
            color=color, tooltip="Capture full-screen screenshot",
        ).pack(side=tk.LEFT, padx=(0, 8))

        self._make_button(
            screen_row, "📝  OCR Screen",
            lambda: self._execute("OCR Screen", screenshot_ops.read_screen_text),
            color=color, tooltip="Extract text from screen using OCR",
        ).pack(side=tk.LEFT)

    def _create_monitoring_tab(self):
        """Monitoring tab: CPU, RAM, Disk, Full Status, Task Manager, Live Stats."""
        frame = tk.Frame(self.task_container, bg=self.BG_PRIMARY)
        self.tab_frames["Monitoring"] = frame
        color = self.DOMAIN_COLORS["Monitoring"]

        self._make_tab_title(frame, "📊  System Monitoring", color)

        # --- Quick Check ---
        section1 = self._make_section(frame, "Quick Check")
        check_row = tk.Frame(section1, bg=self.BG_CARD)
        check_row.pack(fill=tk.X, pady=(0, 8))

        self._make_button(
            check_row, "💻  CPU",
            lambda: self._execute("CPU Usage", system_status.cpu_usage),
            color=color, tooltip="Get current CPU usage",
        ).pack(side=tk.LEFT, padx=(0, 8))

        self._make_button(
            check_row, "🧠  RAM",
            lambda: self._execute("RAM Usage", system_status.ram_usage),
            color=color, tooltip="Get current RAM usage",
        ).pack(side=tk.LEFT, padx=(0, 8))

        self._make_button(
            check_row, "💾  Disk",
            lambda: self._execute("Disk Usage", system_status.disk_usage),
            color=color, tooltip="Get current disk usage",
        ).pack(side=tk.LEFT)

        action_row = tk.Frame(section1, bg=self.BG_CARD)
        action_row.pack(fill=tk.X, pady=(0, 4))

        self._make_button(
            action_row, "📊  Full Status",
            lambda: self._execute("Full Status", system_status.full_status),
            color=color, tooltip="Combined CPU + RAM + Disk summary",
        ).pack(side=tk.LEFT, padx=(0, 8))

        self._make_button(
            action_row, "📋  Task Manager",
            lambda: self._execute("Task Manager", system_status.open_task_manager),
            color=color, tooltip="Open the OS task manager",
        ).pack(side=tk.LEFT)

        # --- Live Stats --- (auto-refreshing)
        section2 = self._make_section(frame, "Live Stats  (auto-refresh every 2s)")
        stats_panel = tk.Frame(section2, bg="#0d1117", padx=16, pady=12)
        stats_panel.pack(fill=tk.X, pady=(0, 4))

        self.live_cpu_label = tk.Label(
            stats_panel, text="💻  CPU:   —", font=("Consolas", 11),
            bg="#0d1117", fg=self.TEXT_PRIMARY, anchor="w",
        )
        self.live_cpu_label.pack(fill=tk.X, pady=2)

        self.live_ram_label = tk.Label(
            stats_panel, text="🧠  RAM:   —", font=("Consolas", 11),
            bg="#0d1117", fg=self.TEXT_PRIMARY, anchor="w",
        )
        self.live_ram_label.pack(fill=tk.X, pady=2)

        self.live_disk_label = tk.Label(
            stats_panel, text="💾  Disk:  —", font=("Consolas", 11),
            bg="#0d1117", fg=self.TEXT_PRIMARY, anchor="w",
        )
        self.live_disk_label.pack(fill=tk.X, pady=2)

    # ═════════════════════════════════════════════════════════════════════════
    # Tab Switching — Nielsen H8 (only active tab shown)
    # ═════════════════════════════════════════════════════════════════════════

    def _show_tab(self, name):
        """Show the selected tab and highlight its sidebar button."""
        if name == self.active_tab:
            return

        # Hide current tab
        if self.active_tab and self.active_tab in self.tab_frames:
            self.tab_frames[self.active_tab].pack_forget()

        # Reset previous button style
        if self.active_tab and self.active_tab in self.nav_buttons:
            self.nav_buttons[self.active_tab].configure(
                bg=self.BG_SIDEBAR, fg=self.TEXT_SECONDARY,
            )

        # Show new tab
        self.active_tab = name
        self.tab_frames[name].pack(fill=tk.BOTH, expand=True)

        # Highlight active button — Nielsen H6 (recognition)
        color = self.DOMAIN_COLORS.get(name, self.TEXT_PRIMARY)
        self.nav_buttons[name].configure(bg=self.BG_SECONDARY, fg=color)

    # ═════════════════════════════════════════════════════════════════════════
    # Execution Engine — Threaded + Status Updates
    # ═════════════════════════════════════════════════════════════════════════

    def _execute(self, description, func, *args):
        """Run a core function in a background thread, updating status/log."""
        self._set_status("🔄  Processing...", self.WARNING)

        def _run():
            try:
                result = func(*args)
                self.root.after(0, lambda: self._on_result(description, result))
            except Exception as e:
                self.root.after(0, lambda: self._on_result(description, str(e), is_error=True))

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def _on_result(self, description, result, is_error=False):
        """Handle the result of an executed command — update UI."""
        if is_error:
            self._set_status("❌  Error", self.ACCENT)
            self._log_response(f"[{description}] Error: {result}", "error")
        else:
            self._set_status("🟢  Ready", self.SUCCESS)
            self._log_response(f"[{description}] {result}", "success")

        # Update last action in status bar
        self._last_action = description
        self.last_action_label.configure(text=f"Last: {description}")

    # ═════════════════════════════════════════════════════════════════════════
    # Response Log — Nielsen H1, H9
    # ═════════════════════════════════════════════════════════════════════════

    def _log_response(self, message, tag="normal"):
        """Append a timestamped message to the response log."""
        timestamp = datetime.now().strftime("%I:%M:%S %p")

        self.response_log.configure(state=tk.NORMAL)
        self.response_log.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.response_log.insert(tk.END, f"{message}\n", tag)

        # Limit to 200 lines
        line_count = int(self.response_log.index("end-1c").split(".")[0])
        if line_count > 200:
            self.response_log.delete("1.0", f"{line_count - 200}.0")

        self.response_log.see(tk.END)
        self.response_log.configure(state=tk.DISABLED)

    # ═════════════════════════════════════════════════════════════════════════
    # Status Management — Nielsen H1
    # ═════════════════════════════════════════════════════════════════════════

    def _set_status(self, text, color):
        """Update both header badge and status bar indicator."""
        self.status_badge.configure(text=f"  {text}  ", fg=color)
        self.bar_status_label.configure(text=text, fg=color)

    def _update_stats_loop(self):
        """Periodically update live system stats."""
        try:
            cpu_pct = psutil.cpu_percent(interval=0)
            mem = psutil.virtual_memory()
            disk_path = "C:\\" if psutil.WINDOWS else "/"
            disk_pct = psutil.disk_usage(disk_path).percent
            ram_gb = mem.used / (1024 ** 3)
            ram_total = mem.total / (1024 ** 3)
            disk_used = psutil.disk_usage(disk_path).used / (1024 ** 3)
            disk_total = psutil.disk_usage(disk_path).total / (1024 ** 3)

            # Status bar (compact)
            self.bar_stats_label.configure(
                text=f"CPU: {cpu_pct}%   RAM: {mem.percent}%   Disk: {disk_pct}%"
            )

            # Live monitoring tab labels (detailed)
            if hasattr(self, "live_cpu_label"):
                color_cpu = self._stat_color(cpu_pct)
                color_ram = self._stat_color(mem.percent)
                color_disk = self._stat_color(disk_pct)

                self.live_cpu_label.configure(
                    text=f"💻  CPU:   {cpu_pct:5.1f}%", fg=color_cpu,
                )
                self.live_ram_label.configure(
                    text=f"🧠  RAM:   {mem.percent:5.1f}%   —   {ram_gb:.1f} / {ram_total:.1f} GB",
                    fg=color_ram,
                )
                self.live_disk_label.configure(
                    text=f"💾  Disk:  {disk_pct:5.1f}%   —   {disk_used:.0f} / {disk_total:.0f} GB",
                    fg=color_disk,
                )
        except Exception:
            pass

        self.root.after(2000, self._update_stats_loop)

    @staticmethod
    def _stat_color(percent):
        """Return a color based on usage percentage."""
        if percent < 50:
            return "#00ff88"
        elif percent < 80:
            return "#f39c12"
        else:
            return "#e94560"

    # ═════════════════════════════════════════════════════════════════════════
    # Help — Nielsen H10
    # ═════════════════════════════════════════════════════════════════════════

    def _show_help(self):
        """Show context-sensitive help for the active tab."""
        tab = self.active_tab or "Information"
        text = HELP_TEXT.get(tab, "No help available.")
        messagebox.showinfo(f"Help — {tab}", text)

    # ═════════════════════════════════════════════════════════════════════════
    # Destructive Action Handlers — Nielsen H3, H5
    # ═════════════════════════════════════════════════════════════════════════

    def _delete_file_action(self):
        """Delete file with confirmation dialog."""
        filename = self.file_name_var.get().strip()
        if not filename:
            return
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{filename}'?\n\nThis action cannot be undone.",
            icon="warning",
        ):
            self._execute("Delete File", file_ops.delete_file, filename)

    def _clear_todos_action(self):
        """Clear all todos with confirmation dialog."""
        if messagebox.askyesno(
            "Confirm Clear",
            "Are you sure you want to clear ALL tasks?\n\nThis action cannot be undone.",
            icon="warning",
        ):
            self._execute("Clear Tasks", productivity.clear_todos)

    def _set_reminder_action(self):
        """Set a reminder using text input and spinner value."""
        text = self.reminder_text_var.get().strip()
        if not text:
            return
        minutes = self.reminder_mins_var.get()
        self._execute(
            "Set Reminder",
            productivity.set_reminder,
            text, minutes,
        )

    # ═════════════════════════════════════════════════════════════════════════
    # Widget Helpers — Keeping style consistent (Nielsen H4)
    # ═════════════════════════════════════════════════════════════════════════

    def _make_tab_title(self, parent, text, color):
        """Create a styled tab title label."""
        tk.Label(
            parent, text=text, font=("Segoe UI", 13, "bold"),
            bg=self.BG_PRIMARY, fg=color, anchor="w",
        ).pack(fill=tk.X, pady=(4, 8))

    def _make_section(self, parent, title):
        """Create a card-style section with a header."""
        wrapper = tk.Frame(parent, bg=self.BG_PRIMARY, pady=4)
        wrapper.pack(fill=tk.X)

        tk.Label(
            wrapper, text=title.upper(), font=("Segoe UI", 8, "bold"),
            bg=self.BG_PRIMARY, fg=self.TEXT_DIM, anchor="w",
        ).pack(fill=tk.X, pady=(0, 4))

        card = tk.Frame(wrapper, bg=self.BG_CARD, padx=14, pady=12,
                        highlightbackground=self.BORDER, highlightthickness=1)
        card.pack(fill=tk.X)
        return card

    def _make_button(self, parent, text, command, color=None, tooltip=None, width=14, state=tk.NORMAL):
        """Create a styled button with hover effect."""
        bg = color or self.BG_SECONDARY
        btn = tk.Button(
            parent, text=text, command=command, font=self.FONT,
            bg=bg, fg="white",
            activebackground=self._lighten(bg, 25),
            activeforeground="white",
            disabledforeground="#555",
            relief=tk.FLAT, cursor="hand2",
            width=width, pady=6, state=state,
        )

        # Hover — Nielsen H4 consistency
        original_bg = bg
        btn.bind("<Enter>", lambda e: (
            btn.configure(bg=self._lighten(original_bg, 20))
            if str(btn["state"]) != "disabled" else None
        ))
        btn.bind("<Leave>", lambda e: (
            btn.configure(bg=original_bg)
            if str(btn["state"]) != "disabled" else None
        ))

        if tooltip:
            ToolTip(btn, tooltip)
        return btn

    def _make_entry(self, parent, variable, placeholder=""):
        """Create a styled text entry field."""
        entry = tk.Entry(
            parent, textvariable=variable, font=self.FONT,
            bg=self.BG_INPUT, fg=self.TEXT_PRIMARY,
            insertbackground=self.TEXT_PRIMARY,
            relief=tk.FLAT, highlightthickness=1,
            highlightcolor="#3498db", highlightbackground="#333",
        )
        # Placeholder behavior
        if placeholder:
            if not variable.get():
                entry.insert(0, placeholder)
                entry.configure(fg=self.TEXT_DIM)

            def on_focus_in(e):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.configure(fg=self.TEXT_PRIMARY)

            def on_focus_out(e):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.configure(fg=self.TEXT_DIM)

            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)

        return entry

    def _bind_entry_to_buttons(self, var, buttons):
        """Disable buttons when entry is empty — Nielsen H5."""
        def on_change(*_):
            val = var.get().strip()
            state = tk.NORMAL if val else tk.DISABLED
            for btn in buttons:
                btn.configure(state=state)
        var.trace_add("write", on_change)
        # Set initial state
        on_change()

    @staticmethod
    def _lighten(hex_color, amount=20):
        """Lighten a hex color by the given amount."""
        hex_color = hex_color.lstrip("#")
        r = min(255, int(hex_color[0:2], 16) + amount)
        g = min(255, int(hex_color[2:4], 16) + amount)
        b = min(255, int(hex_color[4:6], 16) + amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ═════════════════════════════════════════════════════════════════════════
    # Public API
    # ═════════════════════════════════════════════════════════════════════════

    def log_external(self, message, tag="info"):
        """Log a message from an external source (e.g. voice interface)."""
        self.root.after(0, lambda: self._log_response(message, tag))

    def _on_close(self):
        """Handle window close event."""
        self.root.quit()
        self.root.destroy()

    def run(self):
        """Start the GUI main loop."""
        self._log_response("VoiceAssist GUI started. Select a tab and use the controls.", "info")
        self.root.mainloop()


# ═════════════════════════════════════════════════════════════════════════════
# Standalone entry point
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = GUIInterface()
    app.run()
