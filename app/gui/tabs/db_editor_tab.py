import tkinter as tk
from tkinter import ttk, messagebox
from app.database.db_manager import engine_db

class DBEditorTab:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        frame = tk.Frame(self.parent, padx=10, pady=10)
        frame.pack(fill="both", expand=True)
        
        search_frame = tk.LabelFrame(frame, text=" Búsqueda y Filtros de Base de Datos ", padx=10, pady=5)
        search_frame.pack(fill="x", pady=5)
        
        tk.Label(search_frame, text="Tabla:").pack(side="left")
        self.cb_tables = ttk.Combobox(search_frame, values=["insumos", "procesos", "variantes_proceso", "cuadrillas", "config_mano_de_obra"], state="readonly")
        self.cb_tables.set("procesos")
        self.cb_tables.pack(side="left", padx=5)
        self.cb_tables.bind("<<ComboboxSelected>>", lambda e: self.load_data())
        
        tk.Label(search_frame, text="Buscar:").pack(side="left", padx=10)
        self.ent_search = tk.Entry(search_frame, width=40)
        self.ent_search.pack(side="left", padx=5)
        self.ent_search.bind("<KeyRelease>", lambda e: self.load_data())
        
        tk.Button(search_frame, text="🔄 Recargar", command=self.load_data).pack(side="right", padx=5)

        self.tree = ttk.Treeview(frame, show="headings", height=15)
        self.tree.pack(fill="both", expand=True, pady=10)
        
        crud_btn_frame = tk.Frame(frame)
        crud_btn_frame.pack(fill="x")
        
        tk.Button(crud_btn_frame, text="➕ Nuevo", bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"), 
                  command=self.add_record).pack(side="left", padx=5)
        tk.Button(crud_btn_frame, text="📝 Editar", bg="#2980b9", fg="white", font=("Segoe UI", 9, "bold"), 
                  command=self.edit_record).pack(side="left", padx=5)
        tk.Button(crud_btn_frame, text="🗑️ Eliminar", bg="#c0392b", fg="white", font=("Segoe UI", 9, "bold"), 
                  command=self.delete_record).pack(side="left", padx=5)

    def load_data(self, event=None):
        table = self.cb_tables.get()
        if not table: return
        search = self.ent_search.get().strip()
        
        # Determine query
        q = f"SELECT * FROM {table}"
        params = ()
        if search:
            if table == "procesos":
                q += " WHERE nombre LIKE ? OR categoria LIKE ?"
                params = (f"%{search}%", f"%{search}%")
            elif table == "insumos":
                q += " WHERE nombre LIKE ? OR tipo_item LIKE ?"
                params = (f"%{search}%", f"%{search}%")
        
        data = engine_db.execute_query(q, params)
        
        # Cols
        cursor = engine_db._get_connection().cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [c[1] for c in cursor.fetchall()]
        
        self.tree["columns"] = cols
        for c in cols: 
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=120)
        
        for i in self.tree.get_children(): self.tree.delete(i)
        if data:
            for r in data: self.tree.insert("", "end", values=r)

    def add_record(self): self.open_dialog(mode="ADD")
    def edit_record(self):
        sel = self.tree.selection()
        if sel: self.open_dialog(mode="EDIT", initial=self.tree.item(sel[0])['values'])

    def delete_record(self):
        sel = self.tree.selection()
        if not sel: return
        if messagebox.askyesno("Confirmar", "¿Eliminar registro?"):
            table = self.cb_tables.get()
            val_id = self.tree.item(sel[0])['values'][0]
            engine_db.execute_query(f"DELETE FROM {table} WHERE id=?", (val_id,), commit=True)
            self.load_data()
            if hasattr(self.controller, 'refresh_all'): self.controller.refresh_all()

    def open_dialog(self, mode="ADD", initial=None):
        table = self.cb_tables.get()
        dlg = tk.Toplevel(self.controller.root); dlg.title(f"{mode} {table}")
        
        cursor = engine_db._get_connection().cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [c[1] for c in cursor.fetchall()]
        
        entries = {}
        for i, col in enumerate(cols):
            tk.Label(dlg, text=col).grid(row=i, column=0, padx=10, pady=5)
            e = tk.Entry(dlg); e.grid(row=i, column=1, padx=10, pady=5)
            if mode=="EDIT" and initial:
                e.insert(0, initial[i])
                if i==0: e.config(state="disabled")
            entries[col] = e
            
        def save():
            vals = {k: v.get() for k, v in entries.items()}
            try:
                if mode == "ADD":
                    cols_str = ", ".join(vals.keys())
                    p_str = ", ".join(["?"] * len(vals))
                    engine_db.execute_query(f"INSERT INTO {table} ({cols_str}) VALUES ({p_str})", list(vals.values()), commit=True)
                else:
                    id_col = cols[0]
                    set_str = ", ".join([f"{k}=?" for k in vals.keys() if k != id_col])
                    params = [v for k, v in vals.items() if k != id_col] + [vals[id_col]]
                    engine_db.execute_query(f"UPDATE {table} SET {set_str} WHERE {id_col}=?", params, commit=True)
                
                self.load_data()
                if hasattr(self.controller, 'refresh_all'): self.controller.refresh_all()
                dlg.destroy()
            except Exception as e: messagebox.showerror("Error", f"Falla: {e}")

        tk.Button(dlg, text="Guardar", command=save, bg="#27ae60", fg="white").grid(row=len(cols), columnspan=2, pady=10)
