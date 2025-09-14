# Tokopedia Scraper

A simple web scraper for extracting product data from [Tokopedia](https://www.tokopedia.com/) search results using **Selenium** and **BeautifulSoup**.  
This project allows you to perform keyword-based searches directly on Tokopedia, scroll through the results gradually, and save the collected product information into a CSV file.

---

## ✨ Features
- Search products on Tokopedia by keyword (simulates typing in the search bar and pressing **ENTER**).
- Gradual scrolling to ensure products load properly.
- Extracts key product details:
  - Product name
  - Price & original price (if discounted)
  - Promo information
  - Sales count
  - Rating
  - Seller name & location
  - Product link
  - Product image
- Handles duplicate products to avoid redundant entries.
- Save the scraped data into a **CSV file**.

---

## 🛠️ Tech Stack
- [Python 3.12+](https://www.python.org/)
- [Selenium](https://selenium.dev/)
- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)
- [webdriver-manager](https://pypi.org/project/webdriver-manager/)

---

## 🚀 Installation
Clone the repository and install dependencies:

```bash
git clone https://github.com/afrzlfaiz/Tokopedia-Scraper.git
cd Tokopedia-Scraper
pip install -r requirements.txt
