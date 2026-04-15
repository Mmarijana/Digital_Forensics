import tkinter as tk
from tkinter import ttk


class AccountCards:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, style="Main.TFrame")

        self.name_var = tk.StringVar(value="No data")
        self.email_var = tk.StringVar(value="No data")
        self.created_var = tk.StringVar(value="No data")
        self.archive_var = tk.StringVar(value="Not loaded")

        self.frame.columnconfigure(0, weight=1)  # Name
        self.frame.columnconfigure(1, weight=2)  # Email - šira
        self.frame.columnconfigure(2, weight=1)  # Created
        self.frame.columnconfigure(3, weight=1)  # Archive

        self._create_card(0, "👤  Name", self.name_var, "#60a5fa")
        self._create_card(1, "✉  Email", self.email_var, "#a78bfa", wraplength=320)
        self._create_card(2, "📅  Account created", self.created_var, "#34d399")
        self._create_card(3, "📦  Archive status", self.archive_var, "#f59e0b")

    def _create_card(self, col, title, variable, accent_color, wraplength=220):
        outer = tk.Frame(
            self.frame,
            bg="#243552",
            bd=0,
            highlightthickness=0
        )
        outer.grid(row=0, column=col, padx=8, sticky="nsew")

        accent = tk.Frame(
            outer,
            bg=accent_color,
            height=4
        )
        accent.pack(fill="x", side="top")

        body = tk.Frame(
            outer,
            bg="#2b3d5c",
            padx=14,
            pady=14
        )
        body.pack(fill="both", expand=True)

        title_label = tk.Label(
            body,
            text=title,
            bg="#2b3d5c",
            fg="#cbd5e1",
            font=("Segoe UI", 9, "bold"),
            anchor="w"
        )
        title_label.pack(anchor="w")

        value_label = tk.Label(
            body,
            textvariable=variable,
            bg="#2b3d5c",
            fg="#ffffff",
            font=("Segoe UI", 13, "bold"),
            anchor="w",
            wraplength=wraplength,
            justify="left"
        )
        value_label.pack(anchor="w", pady=(8, 0))

    def update_data(self, name, email, created, archive_status):
        self.name_var.set(name)
        self.email_var.set(email)
        self.created_var.set(created)
        self.archive_var.set(archive_status)