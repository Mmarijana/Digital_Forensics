import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import Counter
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from risk_engine import RiskEngine
from ml_engine import MLAnomalyDetector
from timeline_engine import TimelineEngine
from archive_loader import FBArchiveLoader
from report_generator import ReportGenerator
from messages_engine import MessageForensicsEngine
from map_engine import MapEngine

from ui.sidebar import Sidebar
from ui.login_view import LoginView
from ui.account_cards import AccountCards
import shutil
import tkintermapview

from ui.html_report_generator import HTMLReportGenerator
import webbrowser
from image_forensics_engine import ImageForensicsEngine
from ui.image_forensics_view import ImageForensicsView


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("FB - Forensics Viewer")
        self.root.geometry("1200x760")
        self.root.configure(bg="#1e2b45")

        # state
        self.current_profile = {}
        self.current_logins = []
        self.current_messages = {}
        self.current_scored = []
        self.current_total_score = 0
        self.current_account_level = "N/A"
        self.extract_path = None
        self.current_msg_forensics = {}

        self.risk_colors = {
            "LOW": "#22c55e",
            "MEDIUM": "#f59e0b",
            "HIGH": "#ef4444"
        }

        self._last_fig1 = None
        self._last_fig2 = None

        self._setup_style()
        self._build_layout()

        self.image_forensics_engine = ImageForensicsEngine()
        self.cached_image_paths = []
        self.loaded_archive_path = None
        self.image_forensics_view = None

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Main.TFrame", background="#1e2b45")
        style.configure("Panel.TFrame", background="#243552")
        style.configure("Card.TFrame", background="#2d4263")

        style.configure(
            "Title.TLabel",
            background="#1e2b45",
            foreground="white",
            font=("Segoe UI", 18, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            background="#1e2b45",
            foreground="#cfd8e3",
            font=("Segoe UI", 10)
        )

        style.configure(
            "ContentTitle.TLabel",
            background="#243552",
            foreground="white",
            font=("Segoe UI", 12, "bold")
        )

        style.configure(
            "Sidebar.TButton",
            font=("Segoe UI", 10),
            padding=10
        )

        style.configure(
            "Treeview",
            background="white",
            foreground="black",
            fieldbackground="white",
            rowheight=28,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold")
        )

        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 10),
            background="#3b82f6",
            foreground="white",
            borderwidth=0,
            relief="flat"
        )

        style.map(
            "Primary.TButton",
            background=[
                ("active", "#2563eb"),
                ("pressed", "#1d4ed8")
            ],
            foreground=[("disabled", "#cbd5e1")]
        )

        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10),
            padding=(14, 9),
            background="#334155",
            foreground="white",
            borderwidth=0,
            relief="flat"
        )

        style.map(
            "Secondary.TButton",
            background=[
                ("active", "#475569"),
                ("pressed", "#1e293b")
            ]
        )

        style.configure(
            "Success.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 9),
            background="#10b981",
            foreground="white",
            borderwidth=0,
            relief="flat"
        )

        style.map(
            "Success.TButton",
            background=[
                ("active", "#059669"),
                ("pressed", "#047857")
            ]
        )

        style.configure(
            "Sidebar.TButton",
            font=("Segoe UI", 10),
            padding=(14, 10),
            background="#334155",
            foreground="white",
            borderwidth=0,
            relief="flat"
        )

        style.map(
            "Sidebar.TButton",
            background=[
                ("active", "#475569"),
                ("pressed", "#1e293b")
            ]
        )

        style.configure(
            "ActiveSidebar.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 10),
            background="#3b82f6",
            foreground="white",
            borderwidth=0,
            relief="flat"
        )

        style.configure(
            "MsgCharts.TNotebook",
            background="#243552",
            borderwidth=0,
            tabmargins=(0, 0, 0, 0)
        )

        style.configure(
            "MsgCharts.TNotebook.Tab",
            background="#2f405e",
            foreground="#cbd5e1",
            padding=(14, 6),
            font=("Segoe UI", 10),
            borderwidth=0
        )

        style.map(
            "MsgCharts.TNotebook.Tab",
            background=[
                ("selected", "#334155"),
                ("active", "#3a4d6e")
            ],
            foreground=[
                ("selected", "#ffffff"),
                ("active", "#ffffff")
            ]
        )

        style.map(
            "ActiveSidebar.TButton",
            background=[
                ("active", "#2563eb"),
                ("pressed", "#1d4ed8")
            ]
        )

        style.configure(
            "SectionTitle.TLabel",
            background="#1e2b45",
            foreground="white",
            font=("Segoe UI", 14, "bold")
        )

        style.configure(
            "FieldLabel.TLabel",
            background="#1e2b45",
            foreground="#e5e7eb",
            font=("Segoe UI", 10, "bold")
        )

        style.configure("DarkCard.TFrame", background="#2d4263")
        style.configure(
            "CardTitle.TLabel",
            background="#2d4263",
            foreground="white",
            font=("Segoe UI", 11, "bold")
        )

        style.configure(
            "Custom.Vertical.TScrollbar",
            gripcount=0,
            background="#3b4b6b",
            darkcolor="#3b4b6b",
            lightcolor="#3b4b6b",
            troughcolor="#1e2b45",
            bordercolor="#1e2b45",
            arrowcolor="#3b4b6b"
        )

        style.configure(
            "Custom.Horizontal.TScrollbar",
            gripcount=0,
            background="#3b4b6b",
            darkcolor="#3b4b6b",
            lightcolor="#3b4b6b",
            troughcolor="#1e2b45",
            bordercolor="#1e2b45",
            arrowcolor="#3b4b6b"
        )

    def _build_layout(self):
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)

        self._build_header()
        self._build_cards()
        self._build_body()

    def _build_header(self):
        header = ttk.Frame(self.root, style="Main.TFrame", padding=(20, 15))
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        # ===== LEFT SIDE =====
        left = ttk.Frame(header, style="Main.TFrame")
        left.grid(row=0, column=0, sticky="w")

        ttk.Label(left, text="FB - Forensics Viewer", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            left,
            text="Digital forensic analysis of Facebook archive",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(4, 0))

        # ===== RIGHT SIDE =====
        right = ttk.Frame(header, style="Main.TFrame")
        right.grid(row=0, column=1, sticky="e")

        actions = ttk.Frame(right, style="Main.TFrame")
        actions.pack(anchor="e")

        # Primary button - Load Archive
        ttk.Button(
            actions,
            text="📂 Load Archive",
            command=self.load_zip,
            style="Primary.TButton",
            width=18
        ).pack(side="left", padx=(0, 10))

        # Export menu button
        self.export_menu_btn = ttk.Menubutton(
            actions,
            text="🧾 Export Report",
            style="Secondary.TButton",
            width=18
        )
        self.export_menu_btn.pack(side="left")
        self.export_menu_btn.state(["disabled"])

        export_menu = tk.Menu(self.export_menu_btn, tearoff=0)
        export_menu.add_command(label="Export as PDF", command=self.export_report_pdf)
        export_menu.add_command(label="Export as HTML", command=self.export_html_report)
        self.export_menu_btn["menu"] = export_menu

        # Status text
        self.status_var = tk.StringVar(value="❗ No archive loaded")
        self.loaded_file_var = tk.StringVar(value="")

        ttk.Label(
            right,
            textvariable=self.status_var,
            style="Subtitle.TLabel"
        ).pack(anchor="e", pady=(10, 2))

        self.loaded_file_label = ttk.Label(
            right,
            textvariable=self.loaded_file_var,
            style="Subtitle.TLabel"
        )
        self.loaded_file_label.pack(anchor="e")

    def _build_cards(self):
        self.cards = AccountCards(self.root)
        self.cards.frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))

    def _build_body(self):
        body = ttk.Frame(self.root, style="Main.TFrame", padding=(20, 0, 20, 20))
        body.grid(row=2, column=0, sticky="nsew")
        body.rowconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        self.sidebar = Sidebar(body, self.switch_view)
        self.sidebar.frame.grid(row=0, column=0, sticky="nsw", padx=(0, 15))

        self.content_wrapper = ttk.Frame(body, style="Panel.TFrame", padding=15)
        self.content_wrapper.grid(row=0, column=1, sticky="nsew")
        self.content_wrapper.rowconfigure(1, weight=1)
        self.content_wrapper.columnconfigure(0, weight=1)

        self.content_title = tk.StringVar(value="Logins")
        ttk.Label(
            self.content_wrapper,
            textvariable=self.content_title,
            style="ContentTitle.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.content_area = ttk.Frame(self.content_wrapper, style="Panel.TFrame")
        self.content_area.grid(row=1, column=0, sticky="nsew")
        self.content_area.rowconfigure(0, weight=1)
        self.content_area.columnconfigure(0, weight=1)

        self.current_view_name = "logins"
        self.switch_view("logins")

    def _clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def _make_scroll_text(self, parent, height=20):
        frame = tk.Frame(parent, bg="#243552")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        text = tk.Text(
            frame,
            wrap="word",
            height=height,
            bg="#263449",
            fg="#e5e7eb",
            insertbackground="white",
            relief="flat",
            borderwidth=1
        )
        scroll = tk.Scrollbar(frame, command=text.yview)
        text.configure(yscrollcommand=scroll.set)

        scroll.grid(row=0, column=1, sticky="ns")
        text.grid(row=0, column=0, sticky="nsew")

        return text

    def switch_view(self, view_name):
        self.current_view_name = view_name
        self.sidebar.set_active(view_name)
        self._clear_content()

        if view_name == "logins":
            self.content_title.set("Login analysis")
            self.render_logins_view()

        elif view_name == "ai":
            self.content_title.set("AI analysis")
            self.render_ai_view()

        elif view_name == "timeline":
            self.content_title.set("Timeline")
            self.render_timeline_view()

        elif view_name == "charts":
            self.content_title.set("Charts")
            self.render_charts_view()

        elif view_name == "messages":
            self.content_title.set("Messages")
            self.render_messages_view()

        elif view_name == "msgfx":
            self.content_title.set("Message forensics")
            self.render_msgfx_view()

        elif view_name == "msgcharts":
            self.content_title.set("Message charts")
            self.render_msgcharts_view()

        elif view_name == "map":
            self.content_title.set("Map")
            self.render_map_view()

        elif view_name == "imageforensics":
            self.content_title.set("Image forensics")
            self.render_image_forensics_view()

    # ---------------- LOAD ----------------

    def load_zip(self):
        file_path = filedialog.askopenfilename(
            title="Select Facebook ZIP archive",
            filetypes=[("ZIP files", "*.zip")]
        )
        if not file_path:
            return

        try:
            extract_path = os.path.join(os.getcwd(), "fb_extracted")
            self.extract_path = extract_path
            self.loaded_archive_path = extract_path
            self.cached_image_paths = []

            if os.path.exists(extract_path):
                shutil.rmtree(extract_path)

            os.makedirs(extract_path, exist_ok=True)

            FBArchiveLoader.extract_zip(file_path, extract_path)
            self.status_var.set(f"Archive successfully loaded ({os.path.basename(file_path)})")
            self.export_menu_btn.state(["!disabled"])

            json_path = FBArchiveLoader.find_account_activity(extract_path)
            if not json_path:
                messagebox.showerror("Error", "account_activity.json not found.")
                return

            self.display_data(json_path)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_data(self, json_path):
        data = FBArchiveLoader.load_json(json_path)

        self.current_profile = data.get("profile", {})
        self.current_logins = data.get("logins", [])
        self.current_messages = data.get("messages_summary", {})

        p = self.current_profile
        self.cards.update_data(
            name=p.get("name", "N/A"),
            email=p.get("email", "N/A", ),
            created=p.get("account_created", "N/A"),
            archive_status="Loaded"
        )

        scored, total_score, account_level = RiskEngine.calculate_risk_score(self.current_logins)
        self.current_scored = scored
        self.current_total_score = total_score
        self.current_account_level = account_level

        self.switch_view(self.current_view_name)

        self.cached_image_paths = []

    # ---------------- VIEWS ----------------

    def render_logins_view(self):
        view = LoginView(self.content_area)
        view.frame.grid(row=0, column=0, sticky="nsew")

        rows = []
        scored_map = {
            (s.get("date"), s.get("location"), s.get("ip")): s.get("level", "LOW")
            for s in self.current_scored
        }

        for login in self.current_logins:
            key = (
                login.get("date", "N/A"),
                login.get("location", "N/A"),
                login.get("ip", "N/A")
            )
            risk = scored_map.get(key, "LOW")
            rows.append((
                login.get("date", "N/A"),
                login.get("location", "N/A"),
                login.get("ip", "N/A"),
                risk
            ))

        view.set_data(rows)

    def render_ai_view(self):
        self.ai_text = self._make_scroll_text(self.content_area, 24)
        for tag, color in self.risk_colors.items():
            self.ai_text.tag_config(tag, foreground=color)

        self.render_ai_tab()

    def render_timeline_view(self):
        container = ttk.Frame(self.content_area, style="Panel.TFrame")
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        filter_frame = ttk.Frame(container, style="Panel.TFrame")
        filter_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        filter_frame.columnconfigure(4, weight=1)

        ttk.Label(
            filter_frame,
            text="Risk:",
            style="ContentTitle.TLabel"
        ).grid(row=0, column=0, padx=(0, 6), sticky="w")

        self.risk_filter = ttk.Combobox(
            filter_frame,
            values=["ALL", "LOW", "MEDIUM", "HIGH"],
            state="readonly",
            width=12
        )
        self.risk_filter.set("ALL")
        self.risk_filter.grid(row=0, column=1, padx=(0, 12), sticky="w")
        self.risk_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_timeline())

        self.group_by_day_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            filter_frame,
            text="Group by day",
            variable=self.group_by_day_var,
            command=self.refresh_timeline
        ).grid(row=0, column=2, padx=(0, 12), sticky="w")

        ttk.Label(
            filter_frame,
            text="Search:",
            style="ContentTitle.TLabel"
        ).grid(row=0, column=3, padx=(0, 6), sticky="w")

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            filter_frame,
            textvariable=self.search_var
        )
        search_entry.grid(row=0, column=4, padx=(0, 12), sticky="ew")
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_timeline())

        ttk.Button(
            filter_frame,
            text="Refresh",
            command=self.refresh_timeline,
            style="Secondary.TButton"
        ).grid(row=0, column=5, padx=(0, 8), sticky="w")

        ttk.Button(
            filter_frame,
            text="Export TXT",
            command=self.export_timeline_txt,
            style="Secondary.TButton"
        ).grid(row=0, column=6, sticky="e")

        timeline_container = ttk.Frame(container, style="Panel.TFrame")
        timeline_container.grid(row=1, column=0, sticky="nsew")
        timeline_container.rowconfigure(0, weight=1)
        timeline_container.columnconfigure(0, weight=1)

        self.timeline_text = self._make_scroll_text(timeline_container, 28)
        self.timeline_text.master.grid(row=0, column=0, sticky="nsew")

        for tag, color in self.risk_colors.items():
            self.timeline_text.tag_config(tag, foreground=color)

        self.refresh_timeline()

    def render_messages_view(self):

        self.messages_text = self._make_scroll_text(self.content_area, 20)
        m = self.current_messages

        self.messages_text.insert(tk.END, f"Total conversations: {m.get('total_conversations', 0)}\n")
        self.messages_text.insert(tk.END, f"Total messages: {m.get('total_messages', 0)}\n")

    def render_msgfx_view(self):
        self.msgfx_text = self._make_scroll_text(self.content_area, 28)
        for tag, color in self.risk_colors.items():
            self.msgfx_text.tag_config(tag, foreground=color)

        self.render_message_forensics()

    def render_map_view(self):
        self.map_frame = ttk.Frame(self.content_area, style="Panel.TFrame")
        self.map_frame.grid(row=0, column=0, sticky="nsew")
        self.map_frame.rowconfigure(1, weight=1)
        self.map_frame.columnconfigure(0, weight=1)

        toolbar = ttk.Frame(self.map_frame, style="Panel.TFrame")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        toolbar.columnconfigure(2, weight=1)

        ttk.Button(
            toolbar,
            text="Generate map",
            command=self.populate_map,
            style="Primary.TButton"
        ).grid(row=0, column=0, padx=(0, 8), sticky="w")

        ttk.Button(
            toolbar,
            text="Clear map",
            command=self.clear_map,
            style="Secondary.TButton"
        ).grid(row=0, column=1, padx=(0, 8), sticky="w")

        self.map_status_var = tk.StringVar(value="Map is ready.")
        ttk.Label(
            toolbar,
            textvariable=self.map_status_var,
            style="Subtitle.TLabel"
        ).grid(row=0, column=2, sticky="w")

        self.map_widget = tkintermapview.TkinterMapView(
            self.map_frame,
            corner_radius=0
        )
        self.map_widget.grid(row=1, column=0, sticky="nsew")

        # početni prikaz Balkana / Srbije
        self.map_widget.set_position(44.0165, 21.0059)
        self.map_widget.set_zoom(6)

        # odmah pokušaj da nacrtaš podatke ako već postoje
        if self.current_logins:
            self.populate_map()

    def clear_map(self):
        if hasattr(self, "map_widget"):
            self.map_widget.delete_all_marker()
            self.map_widget.delete_all_path()
            self.map_status_var.set("Map cleared.")

    def populate_map(self):
        if not hasattr(self, "map_widget"):
            return

        if not self.current_logins:
            messagebox.showinfo("Info", "No login data for the map.")
            return

        self.map_widget.delete_all_marker()
        self.map_widget.delete_all_path()

        points = MapEngine.get_grouped_login_points(self.current_logins)

        if not points:
            self.map_status_var.set("No coordinates available for map.")
            return

        path_positions = []

        for point in points:
            lat = point["lat"]
            lon = point["lon"]
            location = point["location"]
            count = point["count"]
            level = point["level"]

            marker = self.map_widget.set_marker(
                lat,
                lon,
                text=f"{location} ({count})"
            )

            marker.data = {
                "location": location,
                "count": count,
                "level": level,
                "details": point["details"]
            }
            marker.command = lambda m=marker: self.show_marker_info(m)

            path_positions.append((lat, lon))

        self.map_widget.set_position(points[0]["lat"], points[0]["lon"])
        self.map_widget.set_zoom(5)
        self.map_status_var.set(f"Displayed {len(points)} unique locations.")

    def render_charts_view(self):
        self.charts_frame = tk.Frame(self.content_area, bg="#243552")
        self.charts_frame.grid(row=0, column=0, sticky="nsew")
        self.draw_charts(self.current_logins)

    def center_window(self, window, width=600, height=400):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))

        window.geometry(f"{width}x{height}+{x}+{y}")

    def show_marker_info(self, marker):
        data = marker.data

        popup = tk.Toplevel(self.root)
        popup.title("Login details")
        self.center_window(popup, 560, 420)
        popup.configure(bg="#1e2b45")
        popup.transient(self.root)
        popup.grab_set()

        header = tk.Frame(popup, bg="#243552", height=54)
        header.pack(fill="x")

        tk.Label(
            header,
            text="📍 Login location details",
            bg="#243552",
            fg="white",
            font=("Segoe UI", 13, "bold")
        ).pack(side="left", padx=14, pady=12)

        content = tk.Frame(popup, bg="#1e2b45")
        content.pack(fill="both", expand=True, padx=14, pady=14)

        info_card = tk.Frame(content, bg="#2b3d5c", padx=14, pady=14)
        info_card.pack(fill="x", pady=(0, 12))

        tk.Label(
            info_card,
            text="Location",
            bg="#2b3d5c",
            fg="#cbd5e1",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")
        tk.Label(
            info_card,
            text=data.get("location", "N/A"),
            bg="#2b3d5c",
            fg="white",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(2, 10))

        stats_row = tk.Frame(info_card, bg="#2b3d5c")
        stats_row.pack(fill="x")

        tk.Label(
            stats_row,
            text=f"Total logins: {data.get('count', 0)}",
            bg="#2b3d5c",
            fg="#e5e7eb",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=(0, 16))

        risk = data.get("level", "LOW")
        risk_color = {
            "LOW": "#22c55e",
            "MEDIUM": "#f59e0b",
            "HIGH": "#ef4444"
        }.get(risk, "white")

        tk.Label(
            stats_row,
            text=f"Risk: {risk}",
            bg="#2b3d5c",
            fg=risk_color,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        details_card = tk.Frame(content, bg="#2b3d5c", padx=14, pady=14)
        details_card.pack(fill="both", expand=True)

        tk.Label(
            details_card,
            text="Login history",
            bg="#2b3d5c",
            fg="#cbd5e1",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(0, 8))

        text = tk.Text(
            details_card,
            wrap="word",
            bg="#263449",
            fg="#e5e7eb",
            insertbackground="white",
            relief="flat",
            borderwidth=0,
            font=("Consolas", 10)
        )
        text.pack(fill="both", expand=True)

        text.insert("1.0", data.get("details", ""))
        text.configure(state="disabled")

        footer = tk.Frame(popup, bg="#1e2b45")
        footer.pack(fill="x", padx=14, pady=(0, 14))

        ttk.Button(
            footer,
            text="Close",
            command=popup.destroy,
            style="Secondary.TButton"
        ).pack(side="right")

    def render_ai_tab(self):
        self.ai_text.delete("1.0", tk.END)
        logins = self.current_logins

        suspicious = RiskEngine.analyze_logins_ai(logins)
        self.ai_text.insert(tk.END, "=== AI DETECTION (heuristics) ===\n")
        self.ai_text.insert(tk.END, "-" * 45 + "\n")
        if suspicious:
            for item in suspicious:
                self.ai_text.insert(
                    tk.END,
                    f"⚠️ {item['date']} | {item['location']} | IP: {item['ip']}\n"
                    f"   Reason: {', '.join(item['reasons'])}\n\n"
                )
        else:
            self.ai_text.insert(tk.END, "No suspicious activity.\n")

        scored, total_score, account_level = RiskEngine.calculate_risk_score(logins)
        self.current_scored = scored
        self.current_total_score = total_score
        self.current_account_level = account_level

        self.ai_text.insert(tk.END, "\n=== RISK SCORE ===\n")
        self.ai_text.insert(tk.END, "-" * 45 + "\n")
        self.ai_text.insert(tk.END, f"Total account score: {total_score}\n")
        self.ai_text.insert(tk.END, f"Risk level of the profile: {account_level}\n\n")

        for s in scored:
            self.ai_text.insert(tk.END, "[")
            self.ai_text.insert(tk.END, s["level"], s["level"])
            self.ai_text.insert(tk.END, f"] ({s['score']}) {s['date']} | {s['location']} | IP:{s['ip']}\n")
            self.ai_text.insert(tk.END, f"  Reasons: {', '.join(s['reasons'])}\n\n")

        self.ai_text.insert(tk.END, "\n=== ML ANOMALY DETECTION ===\n")
        self.ai_text.insert(tk.END, "-" * 45 + "\n")

        ml_results = MLAnomalyDetector.detect(logins)
        if not ml_results:
            self.ai_text.insert(tk.END, "Not enough data for ML model or no anomalies.\n")
        else:
            anomalies = [r for r in ml_results if r["ml_pred"] == -1]
            self.ai_text.insert(tk.END, f"Anomalies detected: {len(anomalies)} / {len(ml_results)}\n\n")
            for r in anomalies:
                self.ai_text.insert(
                    tk.END,
                    f"🧠⚠️ ML ANOMALY | {r['date']} | {r['location']} | IP:{r['ip']} | score:{r['ml_score']:.4f}\n"
                )

    def refresh_timeline(self):
        if not hasattr(self, "timeline_text"):
            return

        self.timeline_text.delete("1.0", tk.END)

        events = TimelineEngine.build_events(
            self.current_logins,
            self.current_messages,
            RiskEngine,
            MLAnomalyDetector
        )

        events = TimelineEngine.filter_events(
            events,
            risk_filter=self.risk_filter.get(),
            query=self.search_var.get()
        )

        if self.group_by_day_var.get():
            keys, grouped = TimelineEngine.group_by_day(events)
            for day in keys:
                self.timeline_text.insert(tk.END, f"\n=== {day} ===\n")
                for e in grouped[day]:
                    tag = e.get("level")
                    if tag in self.risk_colors:
                        self.timeline_text.insert(tk.END, e["text"] + "\n", tag)
                    else:
                        self.timeline_text.insert(tk.END, e["text"] + "\n")
        else:
            for e in events:
                tag = e.get("level")
                if tag in self.risk_colors:
                    self.timeline_text.insert(tk.END, e["text"] + "\n", tag)
                else:
                    self.timeline_text.insert(tk.END, e["text"] + "\n")

        if not events:
            self.timeline_text.insert(tk.END, "No events for timeline.\n")

    def export_timeline_txt(self):
        if not hasattr(self, "timeline_text"):
            messagebox.showinfo("Info", "Open Timeline view first.")
            return

        content = self.timeline_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo("Info", "Timeline is empty.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt")]
        )
        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            f.write(content + "\n")
        messagebox.showinfo("OK", f"Saved: {path}")

    def draw_charts(self, logins):
        for w in self.charts_frame.winfo_children():
            w.destroy()

        self._last_fig1 = None
        self._last_fig2 = None

        self.charts_frame.configure(bg="#243552")

        if not logins:
            tk.Label(
                self.charts_frame,
                text="No data for charts.",
                bg="#243552",
                fg="white",
                font=("Segoe UI", 11, "bold")
            ).pack(pady=20)
            return

        def style_axes(ax, title, xlabel="", ylabel=""):
            ax.set_title(title, fontsize=14, fontweight="bold", color="#e5e7eb", pad=12)
            ax.set_xlabel(xlabel, fontsize=10, color="#cbd5e1", labelpad=10)
            ax.set_ylabel(ylabel, fontsize=10, color="#cbd5e1", labelpad=10)

            ax.set_facecolor("#2b3d5c")
            ax.grid(True, axis="y", linestyle="--", alpha=0.22, color="#94a3b8")

            ax.tick_params(axis="x", colors="#e2e8f0", labelsize=9, rotation=20)
            ax.tick_params(axis="y", colors="#e2e8f0", labelsize=9)

            for spine in ax.spines.values():
                spine.set_color("#64748b")
                spine.set_linewidth(1)

        left_card = tk.Frame(self.charts_frame, bg="#243552", padx=10, pady=10)
        left_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), pady=8)

        right_card = tk.Frame(self.charts_frame, bg="#243552", padx=10, pady=10)
        right_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=8)

        # Chart 1: locations
        locations = [l.get("location", "N/A") for l in logins]
        counts = Counter(locations)

        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        labels = [item[0] for item in sorted_items]
        values = [item[1] for item in sorted_items]

        fig1 = plt.Figure(figsize=(5.8, 3.6), dpi=100, facecolor="#243552")
        ax1 = fig1.add_subplot(111)

        bars = ax1.bar(
            labels,
            values,
            color="#60a5fa",
            edgecolor="#93c5fd",
            linewidth=1.2
        )

        style_axes(ax1, "Logins by location", ylabel="Login count")

        for bar in bars:
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.03,
                f"{int(height)}",
                ha="center",
                va="bottom",
                fontsize=9,
                color="#e5e7eb"
            )

        fig1.tight_layout(pad=1.5)

        canvas1 = FigureCanvasTkAgg(fig1, master=left_card)
        canvas1.draw()
        canvas1.get_tk_widget().configure(bg="#243552", highlightthickness=0, bd=0)
        canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Chart 2: timeline
        parsed_dates = []
        for l in logins:
            d = l.get("date")
            if not d:
                continue
            try:
                parsed_dates.append(datetime.strptime(d, "%Y-%m-%d").date())
            except Exception:
                pass

        fig2 = None
        if parsed_dates:
            parsed_dates.sort()
            date_counts = Counter(parsed_dates)
            x = sorted(date_counts.keys())
            y = [date_counts[i] for i in x]

            fig2 = plt.Figure(figsize=(5.8, 3.6), dpi=100, facecolor="#243552")
            ax2 = fig2.add_subplot(111)

            ax2.plot(
                x,
                y,
                color="#34d399",
                linewidth=2.5,
                marker="o",
                markersize=7,
                markerfacecolor="#6ee7b7",
                markeredgecolor="#d1fae5"
            )

            ax2.fill_between(x, y, 0, color="#34d399", alpha=0.12)

            style_axes(ax2, "Logins over time", xlabel="Date", ylabel="Login count")

            for xi, yi in zip(x, y):
                ax2.annotate(
                    str(yi),
                    (xi, yi),
                    textcoords="offset points",
                    xytext=(0, 8),
                    ha="center",
                    fontsize=9,
                    color="#e5e7eb"
                )

            fig2.tight_layout(pad=1.5)

            canvas2 = FigureCanvasTkAgg(fig2, master=right_card)
            canvas2.draw()
            canvas2.get_tk_widget().configure(bg="#243552", highlightthickness=0, bd=0)
            canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            tk.Label(
                right_card,
                text="No valid dates for time chart.",
                bg="#243552",
                fg="white",
                font=("Segoe UI", 10, "bold")
            ).pack(pady=20)

        self._last_fig1 = fig1
        self._last_fig2 = fig2

    def export_report_pdf(self):
        if not ReportGenerator.is_available():
            messagebox.showerror("Error", "reportlab is not installed.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF file", "*.pdf")]
        )
        if not path:
            return

        try:
            import tempfile

            # 1) Message forensics
            if not getattr(self, "current_msg_forensics", None) and self.extract_path:
                self.current_msg_forensics = MessageForensicsEngine.analyze_from_archive(self.extract_path)

            # 2) Risk score / scored logins
            if not getattr(self, "current_scored", None) and self.current_logins:
                scored, total_score, account_level = RiskEngine.calculate_risk_score(self.current_logins)
                self.current_scored = scored
                self.current_total_score = total_score
                self.current_account_level = account_level

            events = TimelineEngine.build_events(
                self.current_logins,
                self.current_messages,
                RiskEngine,
                MLAnomalyDetector
            )
            timeline_lines = [e.get("text", "") for e in events[:50]]

            # 4) Login summary
            scored = self.current_scored or []
            suspicious_logins = sorted(
                [s for s in scored if s.get("level") in ("HIGH", "MEDIUM")],
                key=lambda x: x.get("score", 0),
                reverse=True
            )[:10]

            login_summary = {
                "total_logins": len(self.current_logins or []),
                "unique_locations": len({
                    l.get("location") for l in (self.current_logins or []) if l.get("location")
                }),
                "unique_ips": len({
                    l.get("ip") for l in (self.current_logins or []) if l.get("ip")
                }),
                "top_suspicious": suspicious_logins
            }

            # 5) Image forensics summary
            image_results = []
            if hasattr(self, "image_forensics_view") and self.image_forensics_view:
                image_results = getattr(self.image_forensics_view, "results", []) or []

            image_summary = {
                "total_images": len(image_results),
                "flagged_images": len([
                    r for r in image_results
                    if r.get("prediction") == "Potentially AI-generated"
                ]),
                "top_results": image_results[:10]
            }

            # 6) Charts
            with tempfile.TemporaryDirectory() as tmpdir:
                chart_paths = []

                if self._last_fig1 is not None:
                    img1 = os.path.join(tmpdir, "chart_locations.png")
                    self._last_fig1.savefig(img1, bbox_inches="tight", dpi=150)
                    chart_paths.append(img1)

                if self._last_fig2 is not None:
                    img2 = os.path.join(tmpdir, "chart_timeline.png")
                    self._last_fig2.savefig(img2, bbox_inches="tight", dpi=150)
                    chart_paths.append(img2)

                ReportGenerator.generate_pdf(
                    path=path,
                    profile=self.current_profile,
                    logins=self.current_logins,
                    messages=self.current_messages,
                    total_score=self.current_total_score,
                    account_level=self.current_account_level,
                    timeline_lines=timeline_lines,
                    chart_paths=chart_paths,
                    title="FB - Forensics Viewer Report",
                    message_summary=self.current_msg_forensics,
                    login_summary=login_summary,
                    image_summary=image_summary
                )

            messagebox.showinfo("OK", f"PDF report saved: {path}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_map(self):
        if not self.current_logins:
            messagebox.showinfo("Info", "No login data for the map.")
            return

        scored, _, _ = RiskEngine.calculate_risk_score(self.current_logins)
        scored_sorted = sorted(scored, key=lambda x: x.get("date", ""))

        ml_results = MLAnomalyDetector.detect(self.current_logins)

        out_path = os.path.join(os.getcwd(), "reports", "fb_login_map.html")

        html_path = MapEngine.generate_login_map_html(
            logins=scored_sorted,
            out_html_path=out_path,
            risk_colors=self.risk_colors,
            ml_results=ml_results
        )

        if hasattr(self, "map_status_var"):
            self.map_status_var.set(f"Map generated: {html_path}")

        import webbrowser
        webbrowser.open_new_tab(f"file:///{html_path.replace(os.sep, '/')}")

    def render_message_forensics(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.content_area, style="Panel.TFrame")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        if not self.extract_path:
            tk.Label(
                frame,
                text="Archive is not loaded.",
                bg="#243552",
                fg="white",
                font=("Segoe UI", 11, "bold")
            ).grid(row=0, column=0, padx=12, pady=12, sticky="w")
            return

        fx = MessageForensicsEngine.analyze_from_archive(self.extract_path)
        self.current_msg_forensics = fx

        # top bar: search
        top_bar = ttk.Frame(frame, style="Panel.TFrame")
        top_bar.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 8))
        top_bar.columnconfigure(4, weight=1)

        self.msg_search_var = tk.StringVar()

        ttk.Label(top_bar, text="Search:", style="ContentTitle.TLabel").grid(row=0, column=0, padx=(0, 6), sticky="w")

        self.msg_search_entry = ttk.Entry(top_bar, textvariable=self.msg_search_var, width=30)
        self.msg_search_entry.grid(row=0, column=1, padx=(0, 6), sticky="w")
        self.msg_search_entry.bind("<Return>", lambda e: self.apply_msg_search())

        ttk.Button(
            top_bar,
            text="Apply",
            command=self.apply_msg_search,
            style="Secondary.TButton"
        ).grid(row=0, column=2, padx=(0, 6), sticky="w")

        ttk.Button(
            top_bar,
            text="Reset",
            command=self.render_message_forensics,
            style="Secondary.TButton"
        ).grid(row=0, column=3, sticky="w")

        # text area + scrollbar
        text_wrap = tk.Frame(frame, bg="#243552")
        text_wrap.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        text_wrap.rowconfigure(0, weight=1)
        text_wrap.columnconfigure(0, weight=1)

        self.msgfx_text = tk.Text(
            text_wrap,
            wrap="word",
            bg="#243552",
            fg="#EAF2FF",
            insertbackground="white",
            font=("Consolas", 12),
            relief="flat",
            padx=14,
            pady=14
        )
        self.msgfx_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(text_wrap, orient="vertical", command=self.msgfx_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.msgfx_text.configure(yscrollcommand=scrollbar.set)

        # tags
        self.msgfx_text.tag_configure("HIGH", foreground="#FF6B6B", font=("Consolas", 12, "bold"))
        self.msgfx_text.tag_configure("MEDIUM", foreground="#F7B731", font=("Consolas", 12, "bold"))
        self.msgfx_text.tag_configure("LOW", foreground="#2ECC71", font=("Consolas", 12, "bold"))
        self.msgfx_text.tag_configure("highlight", background="#3A6EA5", foreground="white")

        # content
        self.msgfx_text.insert(tk.END, "=== MESSAGE FORENSICS ===\n")
        self.msgfx_text.insert(tk.END, "-" * 55 + "\n")
        self.msgfx_text.insert(tk.END, f"Mode: {fx.get('mode', 'N/A')}\n")
        self.msgfx_text.insert(tk.END, f"Threads: {fx.get('threads', 0)}\n")
        self.msgfx_text.insert(tk.END, f"Total messages parsed: {fx.get('total_messages', 0)}\n\n")

        mr = fx.get("message_risk")
        if mr:
            self.msgfx_text.insert(tk.END, "=== MESSAGE RISK ===\n")
            self.msgfx_text.insert(tk.END, f"Score: {mr.get('score', 0)}\n")
            self.msgfx_text.insert(tk.END, "Level: ")
            lvl = mr.get("level", "LOW")
            self.msgfx_text.insert(tk.END, lvl, lvl if lvl in ["LOW", "MEDIUM", "HIGH"] else "")
            self.msgfx_text.insert(tk.END, "\n")
            for r in mr.get("reasons", []):
                self.msgfx_text.insert(tk.END, f"- {r}\n")
            self.msgfx_text.insert(tk.END, "\n")

        self.msgfx_text.insert(tk.END, "=== TOP CONTACTS (Top 10) ===\n")
        top_contacts = fx.get("top_contacts", [])
        if top_contacts:
            for name, cnt in top_contacts:
                self.msgfx_text.insert(tk.END, f"- {name} ({cnt} messages)\n")
        else:
            self.msgfx_text.insert(tk.END, "No contacts found.\n")
        self.msgfx_text.insert(tk.END, "\n")

        self.msgfx_text.insert(tk.END, "=== SUSPICIOUS LINKS ===\n")
        links = fx.get("suspicious_links", [])
        if not links:
            self.msgfx_text.insert(tk.END, "No suspicious links detected.\n\n")
        else:
            for item in links:
                kind = "SHORTENER" if item.get("is_shortener") else "URL"
                self.msgfx_text.insert(
                    tk.END,
                    f"- [{kind}] {item.get('url')} | {item.get('sender')} | {item.get('timestamp')}\n"
                )
            self.msgfx_text.insert(tk.END, "\n")

        self.msgfx_text.insert(tk.END, "=== BURST EVENTS ===\n")
        bursts = fx.get("burst_events", [])
        if not bursts:
            self.msgfx_text.insert(tk.END, "No burst activity detected.\n\n")
        else:
            for b in bursts:
                self.msgfx_text.insert(
                    tk.END,
                    f"- {b.get('count')} messages between {b.get('start')} and {b.get('end')}\n"
                )
            self.msgfx_text.insert(tk.END, "\n")

        ai = fx.get("ai_analysis", {})
        if ai:
            self.msgfx_text.insert(tk.END, "=== AI MESSAGE ANALYSIS ===\n")
            self.msgfx_text.insert(tk.END, "-" * 55 + "\n")

            self.msgfx_text.insert(tk.END, "Summary:\n")
            self.msgfx_text.insert(tk.END, f"{ai.get('summary', 'No summary available.')}\n\n")

            self.msgfx_text.insert(tk.END, f"AI Risk Score: {ai.get('score', 0)}\n")
            self.msgfx_text.insert(tk.END, "AI Risk Level: ")
            ai_level = ai.get("risk", "LOW")
            self.msgfx_text.insert(
                tk.END,
                ai_level,
                ai_level if ai_level in ["LOW", "MEDIUM", "HIGH"] else ""
            )
            self.msgfx_text.insert(tk.END, "\n\n")

            categories = ai.get("categories", [])
            self.msgfx_text.insert(tk.END, "Detected categories:\n")
            if categories:
                for cat in categories:
                    self.msgfx_text.insert(tk.END, f"- {cat}\n")
            else:
                self.msgfx_text.insert(tk.END, "No suspicious semantic categories detected.\n")
            self.msgfx_text.insert(tk.END, "\n")

            reasons = ai.get("reasons", [])
            self.msgfx_text.insert(tk.END, "AI reasons:\n")
            if reasons:
                for reason in reasons:
                    self.msgfx_text.insert(tk.END, f"- {reason}\n")
            else:
                self.msgfx_text.insert(tk.END, "No elevated AI indicators found.\n")
            self.msgfx_text.insert(tk.END, "\n")

            flagged = ai.get("flagged_messages", [])
            self.msgfx_text.insert(tk.END, "Flagged messages (AI):\n")
            if flagged:
                for item in flagged[:8]:
                    sender = item.get("sender", "Unknown")
                    text = item.get("text", "")
                    cats = ", ".join(item.get("categories", []))
                    short = text[:140] + "..." if len(text) > 140 else text

                    self.msgfx_text.insert(tk.END, f"- Sender: {sender}\n")
                    self.msgfx_text.insert(tk.END, f"  Categories: {cats}\n")
                    self.msgfx_text.insert(tk.END, f"  Text: {short}\n\n")
            else:
                self.msgfx_text.insert(tk.END, "No AI-flagged messages.\n\n")

        notes = fx.get("notes", [])
        if notes:
            self.msgfx_text.insert(tk.END, "=== NOTES ===\n")
            for note in notes:
                self.msgfx_text.insert(tk.END, f"- {note}\n")

        self.full_msgfx_text = self.msgfx_text.get("1.0", tk.END)

    def draw_message_hour_chart(self, parent, fx):
        for w in parent.winfo_children():
            w.destroy()

        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)

        filter_frame = ttk.Frame(parent, style="Panel.TFrame")
        filter_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        filter_frame.columnconfigure(5, weight=1)

        ttk.Label(
            filter_frame,
            text="From:",
            style="ContentTitle.TLabel"
        ).grid(row=0, column=0, padx=(0, 6), pady=(0, 8), sticky="w")

        self.msg_from_var = tk.StringVar()
        from_entry = ttk.Entry(filter_frame, textvariable=self.msg_from_var, width=14)
        from_entry.grid(row=0, column=1, padx=(0, 12), pady=(0, 8), sticky="w")

        ttk.Label(
            filter_frame,
            text="To:",
            style="ContentTitle.TLabel"
        ).grid(row=0, column=2, padx=(0, 6), pady=(0, 8), sticky="w")

        self.msg_to_var = tk.StringVar()
        to_entry = ttk.Entry(filter_frame, textvariable=self.msg_to_var, width=14)
        to_entry.grid(row=0, column=3, padx=(0, 12), pady=(0, 8), sticky="w")

        refresh_cb = lambda e=None: self.refresh_message_hour_chart(fx)

        from_entry.bind("<Return>", refresh_cb)
        from_entry.bind("<FocusOut>", refresh_cb)

        to_entry.bind("<Return>", refresh_cb)
        to_entry.bind("<FocusOut>", refresh_cb)

        ttk.Label(
            filter_frame,
            text="Format: YYYY-MM-DD",
            style="Subtitle.TLabel"
        ).grid(row=0, column=5, sticky="e", pady=(0, 8))

        ttk.Label(
            filter_frame,
            text="Contact:",
            style="ContentTitle.TLabel"
        ).grid(row=1, column=0, padx=(0, 6), sticky="w")

        all_contacts = sorted({
            m.get("contact", "Unknown")
            for m in fx.get("all_messages", [])
            if m.get("contact")
        })
        contact_values = ["All contacts"] + all_contacts

        self.msg_contact_var = tk.StringVar(value="All contacts")
        contact_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.msg_contact_var,
            values=contact_values,
            state="readonly",
            width=22
        )
        contact_combo.grid(row=1, column=1, columnspan=2, padx=(0, 12), sticky="w")

        ttk.Button(
            filter_frame,
            text="Apply filters",
            command=lambda: self.refresh_message_hour_chart(fx),
            style="Secondary.TButton"
        ).grid(row=1, column=3, sticky="w")

        chart_container = tk.Frame(
            parent,
            bg="#243552",
            padx=10,
            pady=10,
            bd=0,
            highlightthickness=0,
            relief="flat"
        )
        chart_container.grid(row=1, column=0, sticky="nsew")
        chart_container.rowconfigure(0, weight=1)
        chart_container.columnconfigure(0, weight=1)

        self.msg_hour_chart_container = chart_container

        valid_dates = [
            m.get("datetime").date()
            for m in fx.get("all_messages", [])
            if m.get("datetime")
        ]
        if valid_dates:
            self.msg_from_var.set(min(valid_dates).strftime("%Y-%m-%d"))
            self.msg_to_var.set(max(valid_dates).strftime("%Y-%m-%d"))

        self.refresh_message_hour_chart(fx)

    def apply_msg_search(self):
        query = self.msg_search_var.get().strip()

        self.msgfx_text.tag_remove("highlight", "1.0", tk.END)

        if not query:
            return

        start = "1.0"
        found_any = False

        while True:
            start = self.msgfx_text.search(query, start, stopindex=tk.END, nocase=True)
            if not start:
                break
            end = f"{start}+{len(query)}c"
            self.msgfx_text.tag_add("highlight", start, end)
            self.msgfx_text.see(start)
            start = end
            found_any = True

        if not found_any:
            messagebox.showinfo("Search", f"No results found for: {query}")

    def draw_message_contacts_chart(self, parent, fx):
        for w in parent.winfo_children():
            w.destroy()

        container = tk.Frame(parent, bg="#243552", padx=10, pady=10)
        container.grid(row=0, column=0, sticky="nsew")

        contacts = fx.get("top_contacts", [])[:8]

        if not contacts:
            tk.Label(
                container,
                text="No contact statistics available.",
                bg="#243552",
                fg="white",
                font=("Segoe UI", 11, "bold")
            ).pack(pady=20)
            return

        def shorten_name(name, max_len=22):
            return name if len(name) <= max_len else name[:max_len - 3] + "..."

        names = [shorten_name(name) for name, _ in contacts]
        values = [count for _, count in contacts]

        fig_height = max(4.2, len(names) * 0.55)
        fig = plt.Figure(figsize=(8, fig_height), dpi=100, facecolor="#243552")
        ax = fig.add_subplot(111)

        bars = ax.barh(
            names,
            values,
            color="#34d399",
            edgecolor="#6ee7b7",
            linewidth=1.0
        )

        ax.set_title("Top contacts", fontsize=14, fontweight="bold", color="#e5e7eb", pad=12)
        ax.set_xlabel("Messages", fontsize=10, color="#cbd5e1", labelpad=10)

        ax.set_facecolor("#2b3d5c")
        ax.grid(True, axis="x", linestyle="--", alpha=0.22, color="#94a3b8")

        ax.tick_params(axis="x", colors="#e2e8f0", labelsize=9)
        ax.tick_params(axis="y", colors="#e2e8f0", labelsize=10)

        for spine in ax.spines.values():
            spine.set_color("#64748b")
            spine.set_linewidth(1)

        ax.invert_yaxis()

        for bar in bars:
            w = bar.get_width()
            ax.text(
                w + 0.05,
                bar.get_y() + bar.get_height() / 2,
                f"{int(w)}",
                va="center",
                fontsize=9,
                color="#e5e7eb"
            )

        fig.subplots_adjust(left=0.25, right=0.96, top=0.88, bottom=0.12)

        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.configure(bg="#243552", highlightthickness=0, bd=0, relief="flat")
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.get_tk_widget().configure(bg="#243552", highlightthickness=0, bd=0)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def render_msgcharts_view(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.content_area, style="Panel.TFrame")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        if not self.current_msg_forensics and self.extract_path:
            self.current_msg_forensics = MessageForensicsEngine.analyze_from_archive(self.extract_path)

        fx = self.current_msg_forensics or {}

        if not fx or fx.get("total_messages", 0) == 0:
            tk.Label(
                frame,
                text="No message analytics available.",
                bg="#243552",
                fg="white",
                font=("Segoe UI", 11, "bold")
            ).grid(row=0, column=0, pady=20)
            return

        notebook = ttk.Notebook(frame, style="MsgCharts.TNotebook")
        notebook.grid(row=0, column=0, sticky="nsew")

        tab_hour = ttk.Frame(notebook, style="Panel.TFrame")
        tab_contacts = ttk.Frame(notebook, style="Panel.TFrame")

        notebook.add(tab_hour, text="By hour")
        notebook.add(tab_contacts, text="Top contacts")

        tab_hour.rowconfigure(0, weight=1)
        tab_hour.columnconfigure(0, weight=1)

        tab_contacts.rowconfigure(0, weight=1)
        tab_contacts.columnconfigure(0, weight=1)

        self.draw_message_hour_chart(tab_hour, fx)
        self.draw_message_contacts_chart(tab_contacts, fx)

    def refresh_message_hour_chart(self, fx):
        if not hasattr(self, "msg_hour_chart_container"):
            return

        for w in self.msg_hour_chart_container.winfo_children():
            w.destroy()

        messages = fx.get("all_messages", [])

        from_text = self.msg_from_var.get().strip()
        to_text = self.msg_to_var.get().strip()
        selected_contact = self.msg_contact_var.get().strip()

        from_date = None
        to_date = None

        try:
            if from_text:
                from_date = datetime.strptime(from_text, "%Y-%m-%d").date()
        except ValueError:
            tk.Label(
                self.msg_hour_chart_container,
                text="Invalid From date. Use YYYY-MM-DD.",
                bg="#243552",
                fg="#ef4444",
                font=("Segoe UI", 11, "bold")
            ).pack(pady=20)
            return

        try:
            if to_text:
                to_date = datetime.strptime(to_text, "%Y-%m-%d").date()
        except ValueError:
            tk.Label(
                self.msg_hour_chart_container,
                text="Invalid To date. Use YYYY-MM-DD.",
                bg="#243552",
                fg="#ef4444",
                font=("Segoe UI", 11, "bold")
            ).pack(pady=20)
            return

        filtered = []
        for msg in messages:
            dt = msg.get("datetime")
            if not dt:
                continue

            msg_date = dt.date()
            msg_contact = msg.get("contact", "Unknown")

            if from_date and msg_date < from_date:
                continue
            if to_date and msg_date > to_date:
                continue
            if selected_contact != "All contacts" and msg_contact != selected_contact:
                continue

            filtered.append(msg)

        hour_counts = Counter()
        for msg in filtered:
            dt = msg.get("datetime")
            if dt:
                hour_counts[dt.hour] += 1

        xs = list(range(24))
        ys = [hour_counts.get(h, 0) for h in xs]

        fig = plt.Figure(figsize=(8, 4.2), dpi=100, facecolor="#243552")
        ax = fig.add_subplot(111)

        bars = ax.bar(
            xs,
            ys,
            color="#60a5fa",
            edgecolor="#93c5fd",
            linewidth=1.0
        )

        title = "Messages by hour"
        if selected_contact != "All contacts":
            title += f" — {selected_contact}"

        ax.set_title(title, fontsize=10, fontweight="bold", color="#e5e7eb", pad=10)
        ax.set_xlabel("Hour of day", fontsize=10, color="#cbd5e1", labelpad=10)
        ax.set_ylabel("Messages", fontsize=10, color="#cbd5e1", labelpad=10)

        ax.set_facecolor("#2b3d5c")
        ax.grid(True, axis="y", linestyle="--", alpha=0.22, color="#94a3b8")
        ax.set_xticks(xs)

        ax.tick_params(axis="x", colors="#e2e8f0", labelsize=9)
        ax.tick_params(axis="y", colors="#e2e8f0", labelsize=9)

        for spine in ax.spines.values():
            spine.set_color("#64748b")
            spine.set_linewidth(1)

        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    h + 0.05,
                    f"{int(h)}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    color="#e5e7eb"
                )

        if not filtered:
            ax.text(
                0.5, 0.5,
                "No messages for selected filters",
                transform=ax.transAxes,
                ha="center",
                va="center",
                fontsize=12,
                color="#cbd5e1"
            )

        fig.tight_layout(pad=1.4)

        canvas = FigureCanvasTkAgg(fig, master=self.msg_hour_chart_container)
        canvas.draw()
        canvas.get_tk_widget().configure(bg="#243552", highlightthickness=0, bd=0)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def export_html_report(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML file", "*.html")]
        )
        if not path:
            return

        try:
            chart_paths = []
            if self._last_fig1 is not None:
                img1 = os.path.join(os.getcwd(), "chart_locations.png")
                self._last_fig1.savefig(img1, bbox_inches="tight")
                chart_paths.append(img1)

            if self._last_fig2 is not None:
                img2 = os.path.join(os.getcwd(), "chart_timeline.png")
                self._last_fig2.savefig(img2, bbox_inches="tight")
                chart_paths.append(img2)

            if not getattr(self, "current_msg_forensics", None) and self.extract_path:
                self.current_msg_forensics = MessageForensicsEngine.analyze_from_archive(self.extract_path)

            timeline_lines = getattr(self, "current_timeline_lines", []) or []

            HTMLReportGenerator.generate_report(
                output_path=path,
                profile=self.current_profile,
                logins=self.current_logins,
                messages=self.current_messages,
                message_summary=self.current_msg_forensics or {},
                total_score=self.current_total_score,
                account_level=self.current_account_level,
                timeline_lines=timeline_lines,
                chart_paths=chart_paths,
                title="Facebook Forensics Report",
                source_file="Loaded archive"
            )

            webbrowser.open_new_tab(f"file:///{path.replace(os.sep, '/')}")
            messagebox.showinfo("OK", f"HTML report saved: {path}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_loaded_archive_path(self):
        return self.loaded_archive_path or self.extract_path

    def render_image_forensics_view(self):
        self.image_forensics_view = ImageForensicsView(self.content_area, self)
        self.image_forensics_view.grid(row=0, column=0, sticky="nsew")