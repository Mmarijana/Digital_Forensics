import tkinter as tk
from tkinter import ttk


class LoginView:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, style="Panel.TFrame")
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.all_rows = []

        self._build_filters()
        self._build_table()

    def _build_filters(self):
        filter_frame = ttk.Frame(self.frame, style="Panel.TFrame")
        filter_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        filter_frame.columnconfigure(6, weight=1)

        ttk.Label(filter_frame, text="Risk:", style="ContentTitle.TLabel").grid(row=0, column=0, padx=(0, 6), sticky="w")

        self.risk_var = tk.StringVar(value="ALL")
        self.risk_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.risk_var,
            values=["ALL", "LOW", "MEDIUM", "HIGH"],
            state="readonly",
            width=12
        )
        self.risk_combo.grid(row=0, column=1, padx=(0, 12), sticky="w")
        self.risk_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        ttk.Label(filter_frame, text="Location:", style="ContentTitle.TLabel").grid(row=0, column=2, padx=(0, 6), sticky="w")

        self.location_var = tk.StringVar(value="ALL")
        self.location_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.location_var,
            values=["ALL"],
            state="readonly",
            width=22
        )
        self.location_combo.grid(row=0, column=3, padx=(0, 12), sticky="w")
        self.location_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        ttk.Label(filter_frame, text="Search:", style="ContentTitle.TLabel").grid(row=0, column=4, padx=(0, 6), sticky="w")

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=24)
        self.search_entry.grid(row=0, column=5, padx=(0, 12), sticky="w")
        self.search_entry.bind("<KeyRelease>", lambda e: self.apply_filters())

        ttk.Button(filter_frame, text="Reset filters", command=self.reset_filters).grid(row=0, column=6, sticky="e")

    def _build_table(self):
        table_frame = ttk.Frame(self.frame, style="Panel.TFrame")
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        columns = ("date", "location", "ip", "risk")

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.heading("date", text="Date")
        self.tree.heading("location", text="Location")
        self.tree.heading("ip", text="IP Address")
        self.tree.heading("risk", text="Risk")

        self.tree.column("date", width=140)
        self.tree.column("location", width=260)
        self.tree.column("ip", width=180)
        self.tree.column("risk", width=110)

        self.tree.tag_configure("evenrow", background="#f3f4f6")
        self.tree.tag_configure("oddrow", background="#e5e7eb")
        self.tree.tag_configure("LOW", foreground="#16a34a")
        self.tree.tag_configure("MEDIUM", foreground="#d97706")
        self.tree.tag_configure("HIGH", foreground="#dc2626", background="#fee2e2")

    def set_data(self, rows):
        self.all_rows = list(rows)
        self._refresh_location_filter()
        self.apply_filters()

    def _refresh_location_filter(self):
        locations = sorted({row[1] for row in self.all_rows if len(row) > 1 and row[1]})
        self.location_combo["values"] = ["ALL"] + locations
        if self.location_var.get() not in self.location_combo["values"]:
            self.location_var.set("ALL")

    def apply_filters(self):
        risk_filter = self.risk_var.get().strip().upper()
        location_filter = self.location_var.get().strip()
        search_text = self.search_var.get().strip().lower()

        filtered = []

        for row in self.all_rows:
            date_val = str(row[0]) if len(row) > 0 else ""
            location_val = str(row[1]) if len(row) > 1 else ""
            ip_val = str(row[2]) if len(row) > 2 else ""
            risk_val = str(row[3]).upper() if len(row) > 3 else "LOW"

            if risk_filter != "ALL" and risk_val != risk_filter:
                continue

            if location_filter != "ALL" and location_val != location_filter:
                continue

            combined_text = f"{date_val} {location_val} {ip_val} {risk_val}".lower()
            if search_text and search_text not in combined_text:
                continue

            filtered.append(row)

        self._render_rows(filtered)

    def _render_rows(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, row in enumerate(rows):
            risk = str(row[3]).upper() if len(row) > 3 else "LOW"
            base_tag = "evenrow" if i % 2 == 0 else "oddrow"
            tags = [base_tag]

            if risk == "LOW":
                tags.append("LOW")
            elif risk == "MEDIUM":
                tags.append("MEDIUM")
            elif risk == "HIGH":
                tags = ["HIGH"]

            self.tree.insert("", "end", values=row, tags=tuple(tags))

    def reset_filters(self):
        self.risk_var.set("ALL")
        self.location_var.set("ALL")
        self.search_var.set("")
        self.apply_filters()