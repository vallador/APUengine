import tkinter as tk
from tkinter import ttk, messagebox
from app.services.sync_service import SyncService
from app.services.excel_generator import ExcelGenerator

class DashboardTab:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.frame = tk.Frame(self.parent, bg=self.controller.colors['bg'])
        self.frame.pack(fill="both", expand=True)
        
        # Upper stats
        stats_frame = tk.Frame(self.frame, bg="#fff", pady=10, height=100)
        stats_frame.pack(fill="x", side="top", padx=10, pady=10)
        
        tk.Label(stats_frame, text="APU Engine - Resumen Ejecutivo", 
                 font=("Segoe UI", 14, "bold"), bg="#fff").pack(side="left", padx=20)
        
        btn_frame = tk.Frame(stats_frame, bg="#fff")
        btn_frame.pack(side="right", padx=20)
        
        tk.Button(btn_frame, text="Sincronizar Destino.db", 
                  bg=self.controller.colors['accent'], fg="white", 
                  font=("Segoe UI", 10, "bold"), command=self.sync_db, 
                  relief="flat", padx=15).pack(side="right", padx=10)
        
        tk.Button(btn_frame, text="Generar Informe Excel", 
                  bg="#2980b9", fg="white", 
                  font=("Segoe UI", 10, "bold"), command=self.generate_excel, 
                  relief="flat", padx=15).pack(side="right", padx=10)
        
        self.btn_theme = tk.Button(btn_frame, text="🌙 Modo Oscuro", 
                                  bg=self.controller.colors['secondary'], fg="white", 
                                  font=("Segoe UI", 10, "bold"), command=self.controller.toggle_dark_mode, 
                                  relief="flat", padx=15)
        self.btn_theme.pack(side="right")

        self.tree = ttk.Treeview(self.frame, 
                               columns=("ID", "Actividad", "Und", "Real", "Venta", "Margen", "Status"), 
                               show="headings", selectmode="extended")
        
        headings = [
            ("ID", "ID"), ("Actividad", "Actividad / Proceso"), ("Und", "Und"),
            ("Real", "Costo Técnico (Real)"), ("Venta", "Precio Venta"),
            ("Margen", "Ganancia"), ("Status", "Estado")
        ]
        
        for col, text in headings:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=100 if col != "Actividad" else 350, anchor="center" if col != "Actividad" else "w")
            
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for v in self.controller.estimation_list:
            margin = v['comm_price'] - v['tech_cost']
            self.tree.insert("", "end", values=(
                v['id'], v['name'], v['unit'], 
                f"${v['tech_cost']:,.2f}", f"${v['comm_price']:,.2f}", 
                f"${margin:,.2f}", "Seleccionado"
            ))

    def sync_db(self):
        self.controller.status_var.set("Sincronizando con Destino.db...")
        SyncService.update_destino_db()
        messagebox.showinfo("Sync OK", "Sincronización finalizada correctamente.")
        self.controller.status_var.set("Sincronización Exitosa")
        self.refresh()

    def generate_excel(self):
        try:
            selected_items = self.tree.selection()
            variant_ids = []
            for item in selected_items:
                variant_ids.append(self.tree.item(item)['values'][0])
            
            if not variant_ids:
                if self.controller.estimation_list:
                    variant_ids = [v['id'] for v in self.controller.estimation_list]
                else:
                    if not messagebox.askyesno("Exportar", "¿Desea exportar TODOS los procesos? (No hay selección)"):
                        return
                    variant_ids = None
            
            p_name = self.controller.ent_project_name.get() if hasattr(self.controller, 'ent_project_name') else "PROYECTO"
            p_nit  = self.controller.ent_project_nit.get() if hasattr(self.controller, 'ent_project_nit') else ""

            path = ExcelGenerator.generate_apu_report(
                variant_ids=variant_ids, 
                project_name=p_name, 
                project_nit=p_nit
            )
            messagebox.showinfo("Exportar", f"Informe generado en: {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Falla en generación de Excel: {e}")
