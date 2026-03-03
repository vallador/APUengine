from app.core.apu_calculator import APUCalculator
from app.core.description_generator import DescriptionGenerator
from app.database.db_manager import engine_db

def verify_phase3():
    print("Verifying Phase 3 - Modular Infrastructure...")
    try:
        # Test 1: Fetch Variant
        res_v = engine_db.fetch_one("SELECT id FROM variantes_proceso LIMIT 1")
        if not res_v:
            print("Error: No variants found. Seed database first.")
            return
        v_id = res_v[0]
        
        res_c = engine_db.fetch_one("SELECT id FROM cuadrillas LIMIT 1")
        c_id = res_c[0] if res_c else None
        
        # Test 2: Calculate Cost
        cost = APUCalculator.calculate_technical_cost(v_id, crew_id=c_id)
        print(f"Cost with Crew ({c_id}): ${cost:,.2f}")
        
        # Test 3: Generate Procedural Description
        desc = DescriptionGenerator.generate_technical_description(v_id, crew_id=c_id, location="Alturas")
        print(f"Procedural Description: {desc}")
        
        if "en alturas" in desc or "ejecutado por" in desc:
            print("Verification Successful!")
        else:
            print("Verification detail missing in description.")
    except Exception as e:
        print(f"Verification Error: {e}")

if __name__ == "__main__":
    verify_phase3()
