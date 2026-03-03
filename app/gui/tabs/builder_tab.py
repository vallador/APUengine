import tkinter as tk
from tkinter import ttk, messagebox
from app.database.db_manager import engine_db
from app.core.apu_calculator import APUCalculator
from app.core.description_generator import DescriptionGenerator
from app.modules.labor_module import LaborModule

class BuilderTab:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.parent, padx=5, pady=5)
        main_frame.pack(fill="both", expand=True)

        # ── LEFT: Process tree ────────────────────────────────────
        left_panel = tk.LabelFrame(main_frame, text=" 1. Selección de Proceso ", font=("Segoe UI", 10, "bold"))
        left_panel.pack(side="left", fill="both", padx=5)

        proc_search_frame = tk.Frame(left_panel)
        proc_search_frame.pack(fill="x", pady=(4, 0))
        tk.Label(proc_search_frame, text="🔍").pack(side="left")
        self.ent_proc_search = tk.Entry(proc_search_frame)
        self.ent_proc_search.pack(side="left", fill="x", expand=True, padx=4)
        self.ent_proc_search.bind("<KeyRelease>", lambda e: self.filter_tree())

        self.tree_proc = ttk.Treeview(left_panel, columns=("Nombre",), show="tree headings", height=20)
        self.tree_proc.heading("#0", text="Categoría")
        self.tree_proc.heading("Nombre", text="Proceso / Variante")
        self.tree_proc.column("#0", width=220, minwidth=150)
        self.tree_proc.column("Nombre", width=400, minwidth=250)
        
        # Scrollbars
        vsb = ttk.Scrollbar(left_panel, orient="vertical", command=self.tree_proc.yview)
        hsb = ttk.Scrollbar(left_panel, orient="horizontal", command=self.tree_proc.xview)
        self.tree_proc.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        hsb.pack(side="bottom", fill="x")
        vsb.pack(side="right", fill="y")
        self.tree_proc.pack(fill="both", expand=True)
        self.tree_proc.bind("<<TreeviewSelect>>", self.on_proc_select)

        # ── CENTRE: Matrix + Config ──────────────────────
        comp_panel = tk.LabelFrame(main_frame, text=" 2. Configuración del APU ", font=("Segoe UI", 10, "bold"))
        comp_panel.pack(side="left", fill="both", expand=True, padx=5)

        loc_frame = tk.LabelFrame(comp_panel, text="Sitio de Obra")
        loc_frame.pack(fill="x", padx=8, pady=4)
        self.loc_var = tk.StringVar(value="Normal")
        for lbl, val in [("Normal", "Normal"), ("Alturas", "Alturas"), ("Piso", "Piso"), ("Difícil Acceso", "Acceso")]:
            tk.Radiobutton(loc_frame, text=lbl, variable=self.loc_var, value=val,
                           command=self.update_preview).pack(side="left", padx=8)

        crew_frame = tk.LabelFrame(comp_panel, text="Mano de Obra / Cuadrilla")
        crew_frame.pack(fill="x", padx=8, pady=4)
        tk.Label(crew_frame, text="Cuadrilla:").grid(row=0, column=0, padx=6, pady=4, sticky="w")
        self.cb_crews = ttk.Combobox(crew_frame, state="readonly", width=28)
        self.cb_crews.grid(row=0, column=1, padx=4, pady=4)
        self.cb_crews.bind("<<ComboboxSelected>>", self.update_preview)
        
        tk.Label(crew_frame, text="Rend MO (Und/h):").grid(row=0, column=2, padx=6, sticky="w")
        self.ent_yield_mo = tk.Entry(crew_frame, width=9)
        self.ent_yield_mo.insert(0, "1.0")
        self.ent_yield_mo.grid(row=0, column=3, padx=4)
        self.ent_yield_mo.bind("<KeyRelease>", self.update_preview)
        
        tk.Button(crew_frame, text="⚡ Sincronizar DB", bg="#2980b9", fg="white",
                  font=("Segoe UI", 9, "bold"), command=self.controller.dashboard_tab.sync_db).grid(row=0, column=4, padx=5)
        
        tk.Button(crew_frame, text="⚡ Cargar en Matriz", bg=self.controller.colors['accent'], fg="white",
                  font=("Segoe UI", 9, "bold"), command=self.add_crew_members).grid(row=0, column=5, padx=5)

        search_frame = tk.Frame(comp_panel)
        search_frame.pack(fill="x", padx=8, pady=2)
        tk.Label(search_frame, text="Insumo:").pack(side="left")
        self.ent_mat_search = ttk.Combobox(search_frame, width=32)
        self.ent_mat_search.pack(side="left", padx=4)
        tk.Label(search_frame, text="Rend:").pack(side="left", padx=(8, 2))
        self.ent_mat_rend = tk.Entry(search_frame, width=7)
        self.ent_mat_rend.insert(0, "1.0")
        self.ent_mat_rend.pack(side="left")
        
        tk.Button(search_frame, text="➕", bg=self.controller.colors['accent'], fg="white",
                  font=("Segoe UI", 9, "bold"), command=self.add_mat).pack(side="left", padx=4)
        tk.Button(search_frame, text="🗑", bg="#c0392b", fg="white",
                  font=("Segoe UI", 9, "bold"), command=self.remove_mat).pack(side="left")

        mat_frame = tk.LabelFrame(comp_panel, text="Matriz de Insumos (doble-clic para editar)")
        mat_frame.pack(fill="both", expand=True, padx=8, pady=4)

        cols = ("Insumo", "Tipo", "Rend m²", "Desp %", "Cant/m²", "P.Venta", "P.Real", "V/m²")
        self.tree_mat = ttk.Treeview(mat_frame, columns=cols, show="headings", height=10)
        for c in cols:
            self.tree_mat.heading(c, text=c)
            self.tree_mat.column(c, width=80 if c != "Insumo" else 150, anchor="center")
        self.tree_mat.pack(fill="both", expand=True)
        self.tree_mat.bind("<<TreeviewSelect>>", self.update_preview)
        self.tree_mat.bind("<Double-1>", self.on_double_click)

        # Summary panel at the bottom of comp_panel
        summary_frame = tk.Frame(comp_panel, pady=10)
        summary_frame.pack(fill="x", side="bottom")

        self.lbl_direct = tk.Label(summary_frame, text="Costo Directo: $0.00", font=("Segoe UI", 11, "bold"))
        self.lbl_direct.pack()
        self.lbl_total = tk.Label(summary_frame, text="Precio Comercial: $0.00", 
                                font=("Segoe UI", 13, "bold"), fg=self.controller.colors['accent'])
        self.lbl_total.pack()

        tk.Button(summary_frame, text="📝 AÑADIR ACTIVIDAD AL PRESUPUESTO", 
                  bg=self.controller.colors['accent'], fg="white", 
                  font=("Segoe UI", 10, "bold"), command=self.add_to_estimation, 
                  relief="flat", pady=10).pack(fill="x", padx=20, pady=5)

        # ── RIGHT: Description preview ──────────────────────────
        right_panel = tk.LabelFrame(main_frame, text=" 3. Especificación Técnica ", font=("Segoe UI", 10, "bold"))
        right_panel.pack(side="left", fill="both", expand=True, padx=5)
        self.txt_desc = tk.Text(right_panel, wrap="word", font=("Segoe UI", 9))
        self.txt_desc.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.refresh_data()

    def refresh_data(self):
        for i in self.tree_proc.get_children(): self.tree_proc.delete(i)
        procs = engine_db.execute_query("SELECT id, categoria, nombre FROM procesos ORDER BY categoria, nombre")
        cats = {}
        for pid, cat, name in procs:
            if cat not in cats: cats[cat] = self.tree_proc.insert("", "end", text=cat, open=True)
            v_id_row = engine_db.fetch_one("SELECT id FROM variantes_proceso WHERE proceso_id = ?", (pid,))
            v_id = v_id_row[0] if v_id_row else ""
            self.tree_proc.insert(cats[cat], "end", values=(name, str(v_id)))
            
        mats = engine_db.execute_query("SELECT nombre FROM insumos ORDER BY nombre")
        self.ent_mat_search['values'] = [m[0] for m in mats]
        
        crews = engine_db.execute_query("SELECT nombre FROM cuadrillas ORDER BY nombre")
        self.cb_crews['values'] = [c[0] for c in crews]

    def on_proc_select(self, event):
        sel = self.tree_proc.selection()
        if sel:
            d = self.tree_proc.item(sel[0])['values']
            if d and len(d) > 1 and d[1] and str(d[1]).strip() and str(d[1]) != "": 
                self.load_variant(d[1])
            else:
                # Root category selected, clear matrix
                for i in self.tree_mat.get_children(): self.tree_mat.delete(i)
                self.update_preview()

    def load_variant(self, v_id):
        for i in self.tree_mat.get_children(): self.tree_mat.delete(i)
        query = """
            SELECT i.id, i.nombre, i.tipo_item, i.precio_venta, i.descuento_porcentaje, 
                   i.desperdicio_porcentaje, i.contenido_presentacion, m.rendimiento
            FROM matriz_apu m JOIN insumos i ON m.insumo_id = i.id WHERE m.variante_id = ?
        """
        matriz = engine_db.execute_query(query, (v_id,))
        for i_id, nom, tipo, p_v, dto, desp, cont, rend in matriz:
            rend = rend or 1.0; cont = cont or 1.0
            p_real = p_v * (1 - dto/100)
            if tipo == 'Material':
                cant = ((1.0/max(rend, 0.001)) * (1 + desp/100)) / max(cont, 0.001)
                desp_str = f"{desp:.1f}%"
            else:
                cant = 1.0/max(rend, 0.001); desp_str = "N/A"
            
            costo = p_v * cant
            self.tree_mat.insert("", "end", values=(nom, tipo, f"{rend:.2f}", desp_str, f"{cant:.5f}", 
                                                   f"{p_v:,.2f}", f"{p_real:,.2f}", f"{costo:,.2f}"))
        self.update_preview()

    def update_preview(self, event=None):
        costo_directo = 0.0
        has_manual_labor = False
        for rid in self.tree_mat.get_children():
            v = self.tree_mat.item(rid)['values']
            if v[1] == 'Mano de Obra': has_manual_labor = True
            try: costo_directo += float(str(v[7]).replace(',', ''))
            except: pass
            
        crew_name = self.cb_crews.get()
        if crew_name and not has_manual_labor:
            res = engine_db.fetch_one("SELECT id FROM cuadrillas WHERE nombre = ?", (crew_name,))
            if res:
                try: m_rend = float(self.ent_yield_mo.get())
                except: m_rend = 1.0
                items = engine_db.execute_query("SELECT nivel_mo, cantidad FROM cuadrilla_items WHERE cuadrilla_id = ?", (res[0],))
                cost_h = sum(LaborModule.get_labor_cost(n) * q for n, q in items)
                costo_directo += cost_h / max(m_rend, 0.01)

        aiu = APUCalculator.get_aiu_factors()
        total = costo_directo * (1 + sum(aiu.values()))
        self.lbl_direct.config(text=f"Costo Directo: ${costo_directo:,.2f}")
        self.lbl_total.config(text=f"Precio Comercial: ${total:,.2f}")
        
        sel = self.tree_proc.selection()
        if sel:
            data = self.tree_proc.item(sel[0])['values']
            if data and len(data)>1 and data[1] and str(data[1]).strip():
                desc = DescriptionGenerator.generate_technical_description(data[1], 
                                                                        crew_id=self.get_current_crew_id(),
                                                                        location=self.loc_var.get())
                self.txt_desc.delete("1.0", tk.END); self.txt_desc.insert(tk.END, desc)
            else:
                self.txt_desc.delete("1.0", tk.END)

    def get_current_crew_id(self):
        crew_name = self.cb_crews.get()
        if crew_name:
            res = engine_db.fetch_one("SELECT id FROM cuadrillas WHERE nombre = ?", (crew_name,))
            return res[0] if res else None
        return None

    def add_to_estimation(self):
        sel = self.tree_proc.selection()
        if not sel: return
        data = self.tree_proc.item(sel[0])['values']
        if not data or not data[1] or not str(data[1]).strip(): return
        v_id = data[1]
        
        crew_id = self.get_current_crew_id()
        try: m_yield = float(self.ent_yield_mo.get())
        except: m_yield = 1.0
        
        tech_cost = APUCalculator.calculate_technical_cost(v_id, crew_id=crew_id, manual_yield=m_yield)
        comm_price = APUCalculator.calculate_commercial_price(v_id, crew_id=crew_id, manual_yield=m_yield)
        
        res = engine_db.fetch_one("SELECT p.nombre, p.unidad_base FROM procesos p JOIN variantes_proceso v ON v.proceso_id=p.id WHERE v.id=?", (v_id,))
        if not res: return
        name, unit = res

        if any(v['id'] == v_id for v in self.controller.estimation_list):
            messagebox.showwarning("Aviso", "Esta actividad ya está en la estimación.")
            return

        self.controller.estimation_list.append({
            'id': v_id, 'name': name, 'unit': unit, 'qty': 1.0, 
            'tech_cost': tech_cost, 'comm_price': comm_price
        })
        self.controller.refresh_all()
        messagebox.showinfo("OK", f"'{name}' añadido al presupuesto.")

    def filter_tree(self):
        txt = self.ent_proc_search.get().lower()
        if not txt: return
        for i in self.tree_proc.get_children():
            for c in self.tree_proc.get_children(i):
                v = self.tree_proc.item(c)['values']
                if v and txt in v[0].lower():
                    self.tree_proc.see(c); self.tree_proc.selection_set(c); return

    def add_mat(self):
        name = self.ent_mat_search.get()
        if not name: return
        try: rend = float(self.ent_mat_rend.get())
        except: rend = 1.0
        res = engine_db.fetch_one("SELECT tipo_item, precio_venta, descuento_porcentaje, desperdicio_porcentaje, contenido_presentacion FROM insumos WHERE nombre =?", (name,))
        if res:
            tipo, p_v, dto, desp, cont = res
            p_real = p_v * (1 - dto/100)
            if tipo == 'Material':
                cant = ((1.0/max(rend, 0.001)) * (1 + desp/100)) / max(cont or 1.0, 0.001)
                desp_str = f"{desp:.1f}%"
            else:
                cant = 1.0/max(rend, 0.001); desp_str = "N/A"
            self.tree_mat.insert("", "end", values=(name, tipo, f"{rend:.2f}", desp_str, f"{cant:.5f}", f"{p_v:,.2f}", f"{p_real:,.2f}", f"{p_v*cant:,.2f}"))
            self.update_preview()

    def remove_mat(self):
        sel = self.tree_mat.selection()
        if sel: self.tree_mat.delete(sel[0]); self.update_preview()

    def add_crew_members(self):
        crew = self.cb_crews.get()
        if not crew: return
        try: rend = float(self.ent_yield_mo.get())
        except: rend = 1.0
        c_id = engine_db.fetch_one("SELECT id FROM cuadrillas WHERE nombre =?", (crew,))
        if c_id:
            items = engine_db.execute_query("SELECT nivel_mo, cantidad FROM cuadrilla_items WHERE cuadrilla_id = ?", (c_id[0],))
            for nivel, qty in items:
                res = engine_db.fetch_one("SELECT precio_venta, descuento_porcentaje FROM insumos WHERE nombre=? AND tipo_item='Mano de Obra'", (nivel,))
                if res:
                    p_v, dto = res; p_real = p_v * (1 - dto/100)
                    costo = (p_v * qty) / max(rend, 0.001)
                    self.tree_mat.insert("", "end", values=(nivel, "Mano de Obra", f"{rend:.2f}", "N/A", f"{qty/rend:.5f}", f"{p_v:,.2f}", f"{p_real:,.2f}", f"{costo:,.2f}"))
            self.update_preview()

    def on_double_click(self, event):
        item_id = self.tree_mat.identify_row(event.y)
        if not item_id: return
        vals = list(self.tree_mat.item(item_id)['values'])
        dlg = tk.Toplevel(self.controller.root); dlg.title(f"Ajustar: {vals[0]}"); dlg.geometry("400x250"); dlg.grab_set()

        def lrow(lbl, val, r):
            tk.Label(dlg, text=lbl).grid(row=r, column=0, padx=10, pady=5, sticky="w")
            e = tk.Entry(dlg); e.insert(0, str(val).replace(',', '')); e.grid(row=r, column=1, padx=10, pady=5); return e

        # Get metadata from DB
        res = engine_db.fetch_one("SELECT desperdicio_porcentaje, contenido_presentacion, precio_venta FROM insumos WHERE nombre=?", (vals[0],))
        desp = res[0] if res else 0.0; cont = res[1] if res else 1.0; p_v = res[2] if res else 0.0
        
        ent_rend = lrow("Rendimiento (m²/und):", vals[2], 1)
        ent_cant = lrow("Cantidad/m²:", vals[4], 2)

        def sync_cant(*_):
            try:
                rd = max(float(ent_rend.get()), 0.001)
                if vals[1] == 'Material': c = ((1.0/rd)*(1+desp/100))/max(cont, 0.001)
                else: c = 1.0/rd
                ent_cant.delete(0, tk.END); ent_cant.insert(0, f"{c:.5f}"); prev()
            except: pass

        def sync_rend(*_):
            try:
                c = max(float(ent_cant.get()), 0.00001)
                if vals[1] == 'Material': rd = (1+desp/100)/(c*max(cont, 0.001))
                else: rd = 1.0/c
                ent_rend.delete(0, tk.END); ent_rend.insert(0, f"{rd:.2f}"); prev()
            except: pass

        def prev(*_):
            try: 
                c = float(ent_cant.get()); lbl_p.config(text=f"V/m² = ${p_v*c:,.2f}")
            except: pass

        ent_rend.bind("<KeyRelease>", sync_cant); ent_cant.bind("<KeyRelease>", sync_rend)
        lbl_p = tk.Label(dlg, text="", font=("Segoe UI", 10, "bold"), fg="#2980b9"); lbl_p.grid(row=3, columnspan=2, pady=5)
        prev()

        def apply():
            vals[2] = f"{float(ent_rend.get()):.2f}"
            vals[4] = f"{float(ent_cant.get()):.5f}"
            vals[7] = f"{p_v * float(vals[4]):,.2f}"
            self.tree_mat.item(item_id, values=vals); dlg.destroy(); self.update_preview()

        tk.Button(dlg, text="Aplicar", command=apply, bg=self.controller.colors['accent'], fg="white").grid(row=4, columnspan=2, pady=10)
