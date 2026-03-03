import tkinter as tk
from tkinter import ttk
from app.core.config import THEME_LIGHT, THEME_DARK

class ThemeManager:
    def __init__(self, root, style):
        self.root = root
        self.style = style
        self.dark_mode = False
        self.colors = THEME_LIGHT

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        return self.dark_mode

    def apply_theme(self):
        self.colors = THEME_DARK if self.dark_mode else THEME_LIGHT
        
        # Configure ttk Styles
        self.style.configure("TNotebook", background=self.colors['primary'] if self.dark_mode else '#dee2e6')
        self.style.configure("TNotebook.Tab", 
                            background=self.colors['secondary'] if self.dark_mode else '#e9ecef', 
                            foreground=self.colors['text'], 
                            padding=[15, 5], 
                            font=("Segoe UI", 10, "bold"))
        self.style.map("TNotebook.Tab", 
                      background=[("selected", self.colors['accent'])], 
                      foreground=[("selected", "white")])
        
        self.style.configure("Treeview", 
                            background=self.colors['tree_bg'], 
                            foreground=self.colors['tree_fg'], 
                            fieldbackground=self.colors['tree_bg'], 
                            font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", 
                            background=self.colors['secondary'] if self.dark_mode else '#f8f9fa', 
                            foreground=self.colors['tree_fg'] if self.dark_mode else self.colors['primary'], 
                            font=("Segoe UI", 10, "bold"))
        self.style.map("Treeview", background=[('selected', self.colors['accent'])])

        # Update root and recursive background for existing widgets
        self.root.configure(bg=self.colors['bg'])
        self._update_widget_colors(self.root)

    def _update_widget_colors(self, parent):
        for widget in parent.winfo_children():
            try:
                w_type = widget.winfo_class()
                
                if w_type in ("Frame", "Labelframe", "TFrame", "TLabelframe"):
                    widget.configure(bg=self.colors['bg'])
                    if w_type == "Labelframe": 
                        widget.configure(fg=self.colors['accent'])
                    self._update_widget_colors(widget)
                
                elif w_type == "Label":
                    if hasattr(widget, 'is_header') and widget.is_header:
                        widget.configure(bg=self.colors['accent'], fg="white")
                    else:
                        widget.configure(bg=widget.master.cget("bg"), fg=self.colors['text'])
                
                elif w_type == "Button":
                    if not (hasattr(widget, 'custom_bg') and widget.custom_bg):
                        widget.configure(bg=self.colors['secondary'], fg="white")
                
                elif w_type == "Entry":
                    widget.configure(bg=self.colors['tree_bg'], 
                                   fg=self.colors['tree_fg'], 
                                   insertbackground=self.colors['tree_fg'])
            except Exception:
                pass # Some widgets might not support these config options
