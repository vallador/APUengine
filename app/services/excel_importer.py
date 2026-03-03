import pandas as pd
from app.database.db_manager import engine_db
from app.services.smart_processor import SmartProcessor

class ExcelImporter:
    @staticmethod
    def import_standard_descriptions(file_path):
        print(f"Starting Smart Import from {file_path}")
        try:
            df = pd.read_excel(file_path)
            desc_col = 'Descripcion_Estandarizada'
            orig_col = 'Descripcion_Original'
            
            if desc_col not in df.columns or orig_col not in df.columns:
                print(f"Error: Missing expected columns in {file_path}")
                return False
                
            # 1. Clear old references to avoid junk
            engine_db.execute_query("DELETE FROM referentes_descripciones", commit=True)
            
            # 2. Create activities (Procesos/Variantes) from Excel
            cp, cv = SmartProcessor.create_entities_from_excel(df)
            print(f"Created {cp} processes and {cv} variants.")
            
            # 3. Import Proceduralized Templates
            count = 0
            for _, row in df.iterrows():
                original = str(row[orig_col]).strip()
                standard = str(row[desc_col]).strip()
                
                # Proceduralize!
                template_content = SmartProcessor.proceduralize_description(standard)
                activity_name = SmartProcessor.extract_activity_name(original)
                
                # Check for duplicates again (title + content)
                exists = engine_db.fetch_one("SELECT id FROM referentes_descripciones WHERE titulo = ? AND contenido_estandar = ?", (activity_name, template_content))
                if not exists:
                    engine_db.execute_query("INSERT INTO referentes_descripciones (titulo, contenido_estandar, categoria) VALUES (?, ?, ?)", 
                                         (activity_name, template_content, "Smart-Procdural"), commit=True)
                    count += 1
            
            print(f"Smart Import finished. {count} templates added.")
            return True
        except Exception as e:
            print(f"Import Error: {e}")
            return False

if __name__ == "__main__":
    ExcelImporter.import_standard_descriptions("REFERENTES_DESCRIPCIONES_ESTANDARIZADAS.xlsx")
