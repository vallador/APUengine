import pandas as pd

def inspect_referentes(file_path):
    print(f"Inspecting: {file_path}")
    xls = pd.ExcelFile(file_path)
    for sheet_name in xls.sheet_names:
        print(f"\n--- Sheet: {sheet_name} ---")
        df = pd.read_excel(xls, sheet_name=sheet_name)
        print("Headers:", df.columns.tolist())
        print("Sample Data (10 rows):")
        print(df.head(10).to_string())

if __name__ == "__main__":
    inspect_referentes("REFERENTES_DESCRIPCIONES_ESTANDARIZADAS.xlsx")
