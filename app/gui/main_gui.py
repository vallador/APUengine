import tkinter as tk
from tkinter import ttk, messagebox
from app.gui.theme_manager import ThemeManager
from app.gui.tabs.dashboard_tab import DashboardTab
from app.gui.tabs.builder_tab import BuilderTab
from app.gui.tabs.estimation_tab import EstimationTab
from app.gui.tabs.db_editor_tab import DBEditorTab
from app.core.config import VERSION, AUTHOR

class APUEngineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"APU Engine v{VERSION} – {AUTHOR}")
        self.root.geometry("1400x900")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.theme_manager = ThemeManager(self.root, self.style)
        self.colors = self.theme_manager.colors
        
        self.status_var = tk.StringVar(value="Sistema Listo")
        self.estimation_list = [] # Shared state: {id, name, qty, tech_cost, comm_price, unit}
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tabs
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_builder   = ttk.Frame(self.notebook)
        self.tab_estimation = ttk.Frame(self.notebook)
        self.tab_db_editor  = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_dashboard, text="📊 Dashboard")
        self.notebook.add(self.tab_builder, text="🏗️ Constructor")
        self.notebook.add(self.tab_estimation, text="📋 Estimación")
        self.notebook.add(self.tab_db_editor, text="⚙️ Base de Datos")
        
        # Components
        self.dashboard_tab = DashboardTab(self.tab_dashboard, self)
        self.builder_tab   = BuilderTab(self.tab_builder, self)
        self.estimation_tab = EstimationTab(self.tab_estimation, self)
        self.db_editor_tab  = DBEditorTab(self.tab_db_editor, self)
        
        self.theme_manager.apply_theme()
        
        # Footer
        footer = tk.Frame(self.root, bd=1, relief="sunken")
        footer.pack(fill="x", side="bottom")
        tk.Label(footer, textvariable=self.status_var, anchor="w", font=("Segoe UI", 9)).pack(side="left", fill="x")

    def toggle_dark_mode(self):
        self.theme_manager.toggle_theme()
        self.colors = self.theme_manager.colors
        self.status_var.set(f"Modo {'Oscuro' if self.theme_manager.dark_mode else 'Claro'} activado")

    def refresh_all(self):
        """Broadcast refresh to all tab components."""
        self.dashboard_tab.refresh()
        self.builder_tab.refresh_data()
        self.estimation_tab.refresh()
        self.db_editor_tab.load_data()

    # Proxies for specific tab data (needed by other tabs)
    @property
    def ent_project_name(self): return self.estimation_tab.ent_project_name
    @property
    def ent_project_nit(self): return self.estimation_tab.ent_project_nit

    # Placeholders for DB actions (linked from DBEditorTab buttons for now)
    def add_db_record(self): self.db_editor_tab.add_record()
    def edit_db_record(self): self.db_editor_tab.edit_record()
    def delete_db_record(self): self.db_editor_tab.delete_record()
