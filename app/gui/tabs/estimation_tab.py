import tkinter as tk
from tkinter import ttk, messagebox

class EstimationTab:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        # NEW: Estimation Overview before export
        self.frame = tk.Frame(self.parent, padx=10, pady=10)
        self.frame.pack(fill="both", expand=True)
        
        tk.Label(self.frame, text="Planilla de Estimación Presupuestal (Pre-Exportación)", 
                 font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        cols = ("ID", "Actividad", "Cantidad", "V_Tech", "V_Comm", "Total_Tech", "Total_Comm", "Margin")
        self.tree = ttk.Treeview(self.frame, columns=cols, show="headings")
        
        captions = {
            "ID": "ID", "Actividad": "Actividad", "Cantidad": "Cant.",
            "V_Tech": "V. Unit T.", "V_Comm": "V. Unit C.",
            "Total_Tech": "Total Real", "Total_Comm": "Total Venta", "Margin": "Ganancia"
        }
        
        for c in cols:
            self.tree.heading(c, text=captions[c])
            self.tree.column(c, width=100 if c != "Actividad" else 300, anchor="center")
            
        self.tree.pack(fill="both", expand=True)
        
        control_frame = tk.Frame(self.frame)
        control_frame.pack(fill="x", pady=10)
        tk.Label(control_frame, text="Cantidad:").pack(side="left")
        self.ent_qty = tk.Entry(control_frame, width=15)
        self.ent_qty.pack(side="left", padx=5)
        
        tk.Button(control_frame, text="Actualizar Cantidad", 
                  command=self.update_qty).pack(side="left", padx=10)
        
        tk.Button(control_frame, text="Eliminar del Presupuesto", 
                  bg="#c0392b", fg="white", 
                  command=self.remove_item).pack(side="left")
        
        # Project Info for Export
        project_frame = tk.LabelFrame(self.frame, text=" Información del Proyecto (Para Reportes) ", padx=10, pady=10)
        project_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(project_frame, text="Nombre Proyecto:").grid(row=0, column=0, sticky="w")
        self.ent_project_name = tk.Entry(project_frame, width=40)
        self.ent_project_name.insert(0, "PROYECTO INGENIERÍA")
        self.ent_project_name.grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(project_frame, text="NIT/ID:").grid(row=0, column=2, sticky="w", padx=(20, 0))
        self.ent_project_nit = tk.Entry(project_frame, width=20)
        self.ent_project_nit.insert(0, "900.XXX.XXX-X")
        self.ent_project_nit.grid(row=0, column=3, padx=5, pady=2)

        self.lbl_total = tk.Label(self.frame, text="PRESUPUESTO ESTIMADO TOTAL: $0.00", 
                                font=("Segoe UI", 16, "bold"), fg="#2c3e50")
        self.lbl_total.pack(pady=10)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        t_tech, t_comm = 0, 0
        for v in self.controller.estimation_list:
            sub_t = v['qty'] * v['tech_cost']
            sub_c = v['qty'] * v['comm_price']
            margin = sub_c - sub_t
            t_tech += sub_t
            t_comm += sub_c
            
            self.tree.insert("", "end", values=(
                v['id'], v['name'], v['qty'], 
                f"${v['tech_cost']:,.2f}", f"${v['comm_price']:,.2f}",
                f"${sub_t:,.2f}", f"${sub_c:,.2f}", f"${margin:,.2f}"
            ))
        
        margin_gen = t_comm - t_tech
        self.lbl_total.config(
            text=f"PRESUPUESTO: REAL ${t_tech:,.2f} | VENTA ${t_comm:,.2f} | GANANCIA ${margin_gen:,.2f}",
            fg=self.controller.colors['accent']
        )

    def update_qty(self):
        sel = self.tree.selection()
        if not sel: return
        try:
            qty = float(self.ent_qty.get())
            v_id = self.tree.item(sel[0])['values'][0]
            for v in self.controller.estimation_list:
                if v['id'] == v_id:
                    v['qty'] = qty
                    break
            self.refresh()
            if hasattr(self.controller, 'dashboard_tab'):
                self.controller.dashboard_tab.refresh()
        except ValueError:
            messagebox.showerror("Error", "Ingrese una cantidad válida")

    def remove_item(self):
        sel = self.tree.selection()
        if not sel: return
        v_id = self.tree.item(sel[0])['values'][0]
        self.controller.estimation_list = [v for v in self.controller.estimation_list if v['id'] != v_id]
        self.refresh()
        if hasattr(self.controller, 'dashboard_tab'):
            self.controller.dashboard_tab.refresh()
