from tkinter import ttk

class Sidebar:
    def __init__(self, parent, on_change):
        self.on_change = on_change
        self.buttons = {}

        self.frame = ttk.Frame(parent, style="Panel.TFrame", padding=12)
        self.frame.configure(width=220)

        ttk.Label(
            self.frame,
            text="Modules",
            style="ContentTitle.TLabel"
        ).pack(anchor="w", pady=(0, 12))

        self._add_button("Logins", "logins")
        self._add_button("AI Analysis", "ai")
        self._add_button("Image Forensics", "imageforensics")
        self._add_button("Timeline", "timeline")
        self._add_button("Charts", "charts")
        self._add_button("Messages", "messages")
        self._add_button("Message Forensics", "msgfx")
        self._add_button("Message charts", "msgcharts")
        self._add_button("Map", "map")

    def _add_button(self, text, value):
        btn = ttk.Button(
            self.frame,
            text=text,
            style="Sidebar.TButton",
            command=lambda v=value: self.on_change(v)
        )
        btn.pack(fill="x", pady=4)

        self.buttons[value] = btn

    def set_active(self, active_value):
        for value, btn in self.buttons.items():
            if value == active_value:
                btn.configure(style="ActiveSidebar.TButton")
            else:
                btn.configure(style="Sidebar.TButton")