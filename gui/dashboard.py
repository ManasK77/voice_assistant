# gui/dashboard.py
"""
VoiceAssist Dashboard — Dark-themed tkinter GUI.
"""

import sys
import threading
import time
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

import psutil

import config


class Dashboard:
    def __init__(self, voice_io_ref):
        self.voice = voice_io_ref

        # === Window Setup ===
        self.root = tk.Tk()
        self.root.title("VoiceAssist")
        self.root.geometry(f"{config.GUI_WIDTH}x{config.GUI_HEIGHT}")
        self.root.resizable(False, False)

        # Color scheme
        self.bg_color = "#1a1a2e"
        self.bg_secondary = "#16213e"
        self.accent_color = "#e94560"
        self.text_color = "#eaeaea"
        self.text_secondary = "#a0a0b0"
        self.success_color = "#0f3460"

        self.root.configure(bg=self.bg_color)

        # Wire up GUI callbacks on the VoiceIO instance
        self.voice.gui_log_callback = self.log
        self.voice.gui_status_callback = self.update_status

        self._build_ui()

    def _build_ui(self):
        """Build all UI widgets."""
        # === Header ===
        header_frame = tk.Frame(self.root, bg=self.bg_secondary, pady=10, padx=15)
        header_frame.pack(fill=tk.X)

        title_label = tk.Label(
            header_frame,
            text="🎙️  VoiceAssist",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg_secondary,
            fg=self.text_color,
            anchor="w",
        )
        title_label.pack(side=tk.LEFT)

        self.live_indicator = tk.Label(
            header_frame,
            text="● LIVE",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_secondary,
            fg="#00ff88",
        )
        self.live_indicator.pack(side=tk.RIGHT)

        # === Status Section ===
        status_frame = tk.Frame(self.root, bg=self.bg_color, pady=8, padx=15)
        status_frame.pack(fill=tk.X)

        self.status_label = tk.Label(
            status_frame,
            text="Status: Listening...",
            font=("Segoe UI", 11),
            bg=self.bg_color,
            fg=self.accent_color,
            anchor="w",
        )
        self.status_label.pack(fill=tk.X)

        self.last_command_label = tk.Label(
            status_frame,
            text='Last Command: —',
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg=self.text_secondary,
            anchor="w",
        )
        self.last_command_label.pack(fill=tk.X, pady=(4, 0))

        self.last_response_label = tk.Label(
            status_frame,
            text='Last Response: —',
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg=self.text_secondary,
            anchor="w",
            wraplength=380,
            justify="left",
        )
        self.last_response_label.pack(fill=tk.X, pady=(2, 0))

        # === Separator ===
        sep1 = tk.Frame(self.root, bg=self.bg_secondary, height=2)
        sep1.pack(fill=tk.X, padx=15, pady=5)

        # === Command Log Section ===
        log_header = tk.Label(
            self.root,
            text="📋 COMMAND LOG",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
            anchor="w",
            padx=15,
        )
        log_header.pack(fill=tk.X)

        log_frame = tk.Frame(self.root, bg=self.bg_color, padx=15, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 9),
            bg="#0d1117",
            fg=self.text_color,
            insertbackground=self.text_color,
            selectbackground=self.accent_color,
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief=tk.FLAT,
            borderwidth=0,
            padx=8,
            pady=8,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # === Separator ===
        sep2 = tk.Frame(self.root, bg=self.bg_secondary, height=2)
        sep2.pack(fill=tk.X, padx=15, pady=5)

        # === System Stats Section ===
        stats_frame = tk.Frame(self.root, bg=self.bg_color, pady=5, padx=15)
        stats_frame.pack(fill=tk.X)

        self.cpu_label = tk.Label(
            stats_frame,
            text="💻 CPU: --%",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg=self.text_color,
        )
        self.cpu_label.pack(side=tk.LEFT, padx=(0, 15))

        self.ram_label = tk.Label(
            stats_frame,
            text="🧠 RAM: --%",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg=self.text_color,
        )
        self.ram_label.pack(side=tk.LEFT, padx=(0, 15))

        self.disk_label = tk.Label(
            stats_frame,
            text="💾 Disk: --%",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg=self.text_color,
        )
        self.disk_label.pack(side=tk.LEFT)

        # === Separator ===
        sep3 = tk.Frame(self.root, bg=self.bg_secondary, height=2)
        sep3.pack(fill=tk.X, padx=15, pady=5)

        # === Stop Button ===
        button_frame = tk.Frame(self.root, bg=self.bg_color, pady=10)
        button_frame.pack(fill=tk.X)

        self.stop_button = tk.Button(
            button_frame,
            text="🔴 STOP",
            font=("Segoe UI", 12, "bold"),
            bg=self.accent_color,
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            relief=tk.FLAT,
            padx=30,
            pady=8,
            cursor="hand2",
            command=self._on_stop,
        )
        self.stop_button.pack()

    def log(self, message: str):
        """Thread-safe log append to the ScrolledText widget."""
        timestamp = datetime.now().strftime("%I:%M %p")
        formatted = f"[{timestamp}] {message}\n"

        def _append():
            self.log_text.configure(state=tk.NORMAL)
            self.log_text.insert(tk.END, formatted)
            # Limit to 200 lines
            line_count = int(self.log_text.index("end-1c").split(".")[0])
            if line_count > 200:
                self.log_text.delete("1.0", f"{line_count - 200}.0")
            self.log_text.see(tk.END)
            self.log_text.configure(state=tk.DISABLED)

            # Update last command / response labels
            if message.startswith("[YOU]"):
                cmd_text = message.replace("[YOU] ", "")
                self.last_command_label.configure(text=f'Last Command: "{cmd_text}"')
            elif message.startswith("[ASSISTANT]"):
                resp_text = message.replace("[ASSISTANT] ", "")
                self.last_response_label.configure(text=f'Last Response: "{resp_text}"')

        self.root.after(0, _append)

    def update_status(self, status: str):
        """Update the status label text (thread-safe)."""
        def _update():
            self.status_label.configure(text=f"Status: {status}")
        self.root.after(0, _update)

    def update_stats(self):
        """Update CPU, RAM, and Disk live stats."""
        try:
            cpu_pct = psutil.cpu_percent(interval=0)
            ram_pct = psutil.virtual_memory().percent
            disk_path = "C:\\" if psutil.WINDOWS else "/"
            disk_pct = psutil.disk_usage(disk_path).percent

            self.cpu_label.configure(text=f"💻 CPU: {cpu_pct}%")
            self.ram_label.configure(text=f"🧠 RAM: {ram_pct}%")
            self.disk_label.configure(text=f"💾 Disk: {disk_pct}%")
        except Exception:
            pass

        # Schedule next update after 2 seconds
        self.root.after(2000, self.update_stats)

    def _on_stop(self):
        """Handle the stop button click."""
        self.root.quit()
        self.root.destroy()
        sys.exit(0)

    def run(self):
        """Start the GUI main loop."""
        self.update_stats()
        try:
            self.root.mainloop()
        except Exception:
            pass
