import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


class ImageForensicsView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="Main.TFrame")
        self.app = app
        self.results = []
        self.filtered_results = []
        self.preview_photo = None
        self.selected_image_path = None

        self.prediction_var = tk.StringVar(value="ALL")
        self.source_var = tk.StringVar(value="ALL")
        self.search_var = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self):
        title_frame = ttk.Frame(self, style="Main.TFrame")
        title_frame.pack(fill="x", padx=16, pady=(16, 8))

        ttk.Label(
            title_frame,
            text="Image forensic analysis",
            style="SectionTitle.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            title_frame,
            text="Preliminary AI-based check for potentially manipulated or AI-generated images.",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(4, 0))

        actions_frame = ttk.Frame(self, style="Main.TFrame")
        actions_frame.pack(fill="x", padx=16, pady=(0, 12))

        ttk.Button(
            actions_frame,
            text="Scan archive images",
            command=self.scan_archive_images,
            style="Secondary.TButton"
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            actions_frame,
            text="Analyze found images",
            command=self.analyze_found_images,
            style="Secondary.TButton"
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            actions_frame,
            text="Reset filters",
            command=self.reset_filters,
            style="Secondary.TButton"
        ).pack(side="right")

        filters_frame = ttk.Frame(self, style="Main.TFrame")
        filters_frame.pack(fill="x", padx=16, pady=(0, 12))

        ttk.Label(
            filters_frame,
            text="Prediction:",
            style="FieldLabel.TLabel"
        ).pack(side="left", padx=(0, 4))

        prediction_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.prediction_var,
            values=["ALL", "Likely authentic", "Potentially AI-generated", "Error"],
            state="readonly",
            width=24
        )
        prediction_combo.pack(side="left", padx=(0, 12))
        prediction_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        ttk.Label(
            filters_frame,
            text="Source:",
            style="FieldLabel.TLabel"
        ).pack(side="left", padx=(0, 4))

        source_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.source_var,
            values=["ALL", "Profile", "Messages", "Media", "Other", "Unknown"],
            state="readonly",
            width=14
        )
        source_combo.pack(side="left", padx=(0, 12))
        source_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        ttk.Label(
            filters_frame,
            text="Search:",
            style="FieldLabel.TLabel"
        ).pack(side="left", padx=(0, 4))

        search_entry = ttk.Entry(filters_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=(0, 12))
        search_entry.bind("<KeyRelease>", lambda e: self.apply_filters())

        main_area = ttk.Frame(self, style="Main.TFrame")
        main_area.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        main_area.columnconfigure(0, weight=3)
        main_area.columnconfigure(1, weight=2)
        main_area.rowconfigure(0, weight=1)

        # LEFT SIDE - TABLE
        table_frame = ttk.Frame(main_area, style="Main.TFrame")
        table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        columns = ("file_name", "source", "prediction", "confidence", "status")

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        self.tree.heading("file_name", text="File name")
        self.tree.heading("source", text="Source")
        self.tree.heading("prediction", text="Prediction")
        self.tree.heading("confidence", text="Confidence (%)")
        self.tree.heading("status", text="Status")

        self.tree.column("file_name", width=230)
        self.tree.column("source", width=110, anchor="center")
        self.tree.column("prediction", width=190, anchor="center")
        self.tree.column("confidence", width=120, anchor="center")
        self.tree.column("status", width=180)

        self.tree.tag_configure("even", background="#ffffff")
        self.tree.tag_configure("odd", background="#f3f4f6")

        self.table_scrollbar_y = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview,
            style="Custom.Vertical.TScrollbar"
        )
        self.table_scrollbar_x = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview,
            style="Custom.Horizontal.TScrollbar"
        )

        self.tree.configure(
            yscrollcommand=self.table_scrollbar_y.set,
            xscrollcommand=self.table_scrollbar_x.set
        )

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.table_scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.table_scrollbar_x.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<<TreeviewSelect>>", self.on_row_selected)

        # RIGHT SIDE - PREVIEW CARD ONLY
        right_panel = ttk.Frame(main_area, style="Main.TFrame")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)

        preview_card = ttk.Frame(right_panel, style="DarkCard.TFrame")
        preview_card.grid(row=0, column=0, sticky="nsew")
        preview_card.columnconfigure(0, weight=1)
        preview_card.rowconfigure(1, weight=1)

        preview_top_line = tk.Frame(preview_card, bg="#60a5fa", height=4)
        preview_top_line.grid(row=0, column=0, sticky="ew")

        preview_inner = ttk.Frame(preview_card, style="DarkCard.TFrame", padding=12)
        preview_inner.grid(row=1, column=0, sticky="nsew")
        preview_inner.columnconfigure(0, weight=1)
        preview_inner.rowconfigure(1, weight=1)

        ttk.Label(
            preview_inner,
            text="Image preview",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.preview_box = tk.Frame(
            preview_inner,
            bg="#243552",
            bd=0,
            highlightthickness=0
        )
        self.preview_box.grid(row=1, column=0, sticky="nsew", pady=(0, 12))
        self.preview_box.grid_propagate(False)

        self.image_label = tk.Label(
            self.preview_box,
            text="No image selected",
            bg="#243552",
            fg="#e5e7eb",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2"
        )
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")
        self.image_label.bind("<Button-1>", lambda e: self.open_image_popup())

        self.open_button = ttk.Button(
            preview_inner,
            text="Open original",
            command=self.open_selected_image,
            style="Secondary.TButton",
            width=16
        )
        self.open_button.grid(row=2, column=0, sticky="e")

    def scan_archive_images(self):
        archive_root = self.app.get_loaded_archive_path()
        if not archive_root:
            messagebox.showwarning("No archive", "Please load a Facebook archive first.")
            return

        try:
            image_paths = self.app.image_forensics_engine.find_images_in_archive(
                archive_root,
                limit=50
            )
            self.app.cached_image_paths = image_paths

            messagebox.showinfo(
                "Scan complete",
                f"Found {len(image_paths)} image(s) in the archive."
            )

            self.results = []
            self.filtered_results = []
            self.refresh_table()
            self.clear_preview()

        except Exception as ex:
            messagebox.showerror("Scan error", str(ex))

    def analyze_found_images(self):
        if not hasattr(self.app, "cached_image_paths") or not self.app.cached_image_paths:
            messagebox.showwarning("No images", "No images found. Please scan the archive first.")
            return

        try:
            self.results = self.app.image_forensics_engine.analyze_images(self.app.cached_image_paths)
            self.apply_filters()

            messagebox.showinfo(
                "Analysis complete",
                f"Analyzed {len(self.results)} image(s)."
            )

        except Exception as ex:
            messagebox.showerror("Analysis error", str(ex))

    def apply_filters(self):
        prediction_filter = self.prediction_var.get().strip()
        source_filter = self.source_var.get().strip()
        search_value = self.search_var.get().strip().lower()

        filtered = []

        for item in self.results:
            if prediction_filter != "ALL" and item.get("prediction") != prediction_filter:
                continue

            if source_filter != "ALL" and item.get("source") != source_filter:
                continue

            file_name = item.get("file_name", "").lower()
            path = item.get("path", "").lower()

            if search_value and search_value not in file_name and search_value not in path:
                continue

            filtered.append(item)

        self.filtered_results = filtered
        self.refresh_table()
        self.clear_preview()

    def reset_filters(self):
        self.prediction_var.set("ALL")
        self.source_var.set("ALL")
        self.search_var.set("")
        self.apply_filters()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = self.filtered_results if self.results else []

        for idx, item in enumerate(data):
            tag = "even" if idx % 2 == 0 else "odd"

            self.tree.insert(
                "",
                "end",
                iid=str(idx),
                values=(
                    item.get("file_name", ""),
                    item.get("source", ""),
                    item.get("prediction", ""),
                    item.get("confidence", ""),
                    item.get("status", "")
                ),
                tags=(tag,)
            )

    def clear_preview(self):
        self.selected_image_path = None
        self.preview_photo = None
        self.image_label.config(
            image="",
            text="No image selected",
            bg="#243552",
            fg="#e5e7eb"
        )

    def on_row_selected(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        idx = int(selection[0])
        if idx >= len(self.filtered_results):
            return

        item = self.filtered_results[idx]
        self.selected_image_path = item.get("path", "")
        self.show_image_preview(self.selected_image_path)

    def open_selected_image(self):
        if not self.selected_image_path or not os.path.exists(self.selected_image_path):
            messagebox.showwarning("No image", "No valid image selected.")
            return

        try:
            import webbrowser
            webbrowser.open(self.selected_image_path)
        except Exception as ex:
            messagebox.showerror("Open error", str(ex))

    def open_image_popup(self):
        if not self.selected_image_path or not os.path.exists(self.selected_image_path):
            return

        try:
            popup = tk.Toplevel(self)
            popup.title("Image preview")
            popup.configure(bg="#1e2b45")
            popup.geometry("900x700")
            popup.minsize(600, 450)

            container = tk.Frame(popup, bg="#1e2b45")
            container.pack(fill="both", expand=True, padx=12, pady=12)

            img = Image.open(self.selected_image_path).convert("RGB")
            max_width = 860
            max_height = 640
            img.thumbnail((max_width, max_height))

            popup.preview_photo = ImageTk.PhotoImage(img)

            lbl = tk.Label(
                container,
                image=popup.preview_photo,
                bg="#1e2b45",
                bd=0
            )
            lbl.pack(expand=True)

        except Exception as ex:
            messagebox.showerror("Preview error", str(ex))

    def show_image_preview(self, image_path):
        if not image_path or not os.path.exists(image_path):
            self.image_label.config(
                image="",
                text="Image not found",
                bg="#243552"
            )
            self.preview_photo = None
            return

        try:
            image = Image.open(image_path).convert("RGB")

            max_width = 520
            max_height = 320
            image.thumbnail((max_width, max_height))

            self.preview_photo = ImageTk.PhotoImage(image)

            self.image_label.config(
                image=self.preview_photo,
                text="",
                bg="#243552"
            )
        except Exception as ex:
            self.image_label.config(
                image="",
                text=f"Preview error:\n{str(ex)}",
                bg="#243552"
            )
            self.preview_photo = None