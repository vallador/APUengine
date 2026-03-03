import requests
from bs4 import BeautifulSoup
from app.database.db_manager import engine_db
from app.modules.pricing_module import PricingModule

class ScraperService:
    @staticmethod
    def scrape_price(insumo_id):
        query = "SELECT url, selector_css FROM scraper_config WHERE insumo_id = ?"
        config = engine_db.fetch_one(query, (insumo_id,))
        if not config or not config[0]: return None
        url, selector = config
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                element = soup.select_one(selector)
                if element:
                    price = float(element.text.strip().replace('$', '').replace('.', '').replace(',', '.'))
                    PricingModule.update_precio(insumo_id, price, url)
                    engine_db.execute_query("UPDATE scraper_config SET last_scraped_price = ?, status = 'Success' WHERE insumo_id = ?", (price, insumo_id), commit=True)
                    return price
        except: engine_db.execute_query("UPDATE scraper_config SET status = 'Error' WHERE insumo_id = ?", (insumo_id,), commit=True)
        return None

    @staticmethod
    def scrape_all():
        for (i_id,) in engine_db.execute_query("SELECT insumo_id FROM scraper_config"):
            ScraperService.scrape_price(i_id)
        return True
