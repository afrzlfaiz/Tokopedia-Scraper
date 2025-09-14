import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


class TokopediaScraper:
    def __init__(self, keywords="work jacket", max_scrolls=5, output_file="tokopedia_products.csv"):
        self.keywords = keywords
        self.max_scrolls = max_scrolls
        self.output_file = output_file
        self.driver = None
        self.products = []

    def setup_driver(self):
        """Setup Chrome driver"""
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(10)

    def search_keyword(self):
        """Kunjungi Tokopedia dan cari keyword"""
        print("Visiting Tokopedia homepage...")
        self.driver.get("https://www.tokopedia.com/")

        # Tunggu search box tersedia
        search_box = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="header-main-wrapper"]/div[2]/div[2]/div/div/div/div/input'))
        )

        print(f"Searching for: {self.keywords}")
        search_box.send_keys(self.keywords)
        search_box.send_keys(Keys.ENTER)

        # Tunggu produk muncul
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='divSRPContentProducts']"))
        )

    def parse_products(self):
        """Extract products from current page source"""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        products_container = soup.find('div', {'data-testid': 'divSRPContentProducts'})
        if not products_container:
            return []

        product_items = products_container.find_all('div', class_='css-5wh65g')
        products = []

        for item in product_items:
            product_data = {}

            # Link
            link_element = item.find('a')
            if link_element and link_element.get('href'):
                product_data['link'] = link_element['href']

            # Image
            img_element = item.find('img', alt='product-image')
            if img_element and img_element.get('src'):
                product_data['image'] = img_element['src']

            # Name
            name_element = item.find('span', class_='+tnoqZhn89+NHUA43BpiJg==')
            if name_element:
                product_data['name'] = name_element.text.strip()

            # Price
            price_element = item.find('div', class_='urMOIDHH7I0Iy1Dv2oFaNw==')
            if price_element and 'HJhoi0tEIlowsgSNDNWVXg==' in price_element.get('class', []):
                product_data['price'] = price_element.text.strip()

            # Original price
            original_price_element = item.find('span', class_='hC1B8wTAoPszbEZj80w6Qw==')
            if original_price_element:
                product_data['original_price'] = original_price_element.text.strip()

            # Promo
            promo_element = item.find('span', class_='_7UCYdN8MrOTwg0MKcGu8zg==')
            if promo_element:
                product_data['promo'] = promo_element.text.strip()

            # Sales
            sales_element = item.find('span', class_='u6SfjDD2WiBlNW7zHmzRhQ==')
            if sales_element:
                product_data['sales'] = sales_element.text.strip()

            # Rating
            rating_element = item.find('span', class_='_2NfJxPu4JC-55aCJ8bEsyw==')
            if rating_element:
                product_data['rating'] = rating_element.text.strip()

            # Seller
            seller_elements = item.find_all('span', class_='si3CNdiG8AR0EaXvf6bFbQ==')
            if seller_elements:
                product_data['seller'] = seller_elements[0].text.strip()

            # Location
            location_elements = item.find_all('span', class_='gxi+fsEljOjqhjSKqjE+sw==')
            if len(location_elements) >= 2:
                product_data['location'] = location_elements[1].text.strip()

            if 'name' in product_data and 'price' in product_data:
                products.append(product_data)

        return products

    def scroll_and_collect(self, step=1000, pause=2):
        """Scroll bertahap + simpan data tiap kali scroll"""
        scroll_count = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while scroll_count < self.max_scrolls:
            print(f"Scroll {scroll_count + 1}...")

            # Scroll bertahap per step pixel
            current_height = 0
            while current_height < last_height:
                current_height += step
                self.driver.execute_script(f"window.scrollTo(0, {current_height});")
                time.sleep(pause)  # jeda agar konten sempat load

            # Ambil produk setelah selesai scroll satu putaran
            new_products = self.parse_products()
            for p in new_products:
                if p not in self.products:
                    self.products.append(p)

            print(f"Collected {len(self.products)} unique products so far...")

            # Cek apakah ada perubahan tinggi halaman
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # tidak ada produk baru
            last_height = new_height
            scroll_count += 1

    def save_to_csv(self):
        """Save data ke CSV"""
        if not self.products:
            print("No products to save.")
            return

        keys = self.products[0].keys()
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.products)

        print(f"Data saved to {self.output_file}")

    def close_driver(self):
        if self.driver:
            self.driver.quit()


def scrape_tokopedia_search(keywords="work jacket"):
    scraper = TokopediaScraper(keywords, max_scrolls=20)
    try:
        scraper.setup_driver()
        scraper.search_keyword()
        scraper.scroll_and_collect()
        scraper.save_to_csv()
        return scraper.products
    finally:
        scraper.close_driver()


if __name__ == "__main__":
    print("Starting Tokopedia scraper...")
    products = scrape_tokopedia_search(keywords="work jacket")
    print(f"Total products collected: {len(products)}")
    if products:
        print("Sample product:")
        print(products[0])
