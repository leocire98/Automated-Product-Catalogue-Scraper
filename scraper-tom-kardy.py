from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
from openpyxl import load_workbook
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = "https://tomkardy.com.ua/"
FIRST_PAGE_URL = "https://tomkardy.com.ua/ua/g44619880-originalnaya-upakovka-oae"
LAST_PAGE = 17
OUTPUT_FILE = Path("file.xlsx")
SHEET_NAME = "first-link"


def clean_price(price: str) -> str:
    cleaned = price.replace("\u00a0", "").replace("від", "").replace("₴", "").replace(" ", "").strip()
    return float(cleaned) if cleaned else 0.0

def scrape_page(driver: webdriver.Chrome, page_number: int) -> list[dict[str, str]]:
    page_url = FIRST_PAGE_URL if page_number == 1 else f"{FIRST_PAGE_URL}/page_{page_number}"
    driver.get(page_url)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.cs-goods-title"))
        )
    except TimeoutException:
        return []

    products = []
    for title_element in driver.find_elements(By.CSS_SELECTOR, "a.cs-goods-title"):
        card = title_element.find_element(
            By.XPATH, "ancestor::li[@data-qaid='product-block'][1]"
        )
        old_price = card.find_elements(By.CSS_SELECTOR, ".cs-goods-price__value_type_old")
        current_price = card.find_elements(By.CSS_SELECTOR, ".cs-goods-price__value_type_current")

        products.append(
            {
                "Product Title": title_element.text.strip(),
                "Url": urljoin(BASE_URL, title_element.get_attribute("href")),
                "Old Price": clean_price(old_price[0].text) if old_price else "",
                "Current Price": clean_price(current_price[0].text) if current_price else "",
            }
        )
    return products


def main() -> None:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")

    with webdriver.Chrome(options=options) as driver:
        all_products = []
        for page_number in range(1, LAST_PAGE + 1):
            products = scrape_page(driver, page_number)
            if not products:
                raise RuntimeError(f"Nessun prodotto trovato nella pagina {page_number}.")

            all_products.extend(products)
            print(f"Page {page_number}/{LAST_PAGE} completed")

    dataframe = pd.DataFrame(all_products).drop_duplicates(subset=["Url"])
    if OUTPUT_FILE.exists():
        with pd.ExcelWriter(
            OUTPUT_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace"
        ) as writer:
            dataframe.to_excel(writer, sheet_name=SHEET_NAME, index=False)
    else:
        dataframe.to_excel(OUTPUT_FILE, sheet_name=SHEET_NAME, index=False)

    workbook = load_workbook(OUTPUT_FILE)
    worksheet = workbook[SHEET_NAME]
    for row in range(2, worksheet.max_row + 1):
        cell = worksheet.cell(row=row, column=2)
        if cell.value:
            cell.hyperlink = str(cell.value)
            cell.style = "Hyperlink"
    workbook.save(OUTPUT_FILE)

    print(f"Saved {len(dataframe)} products in {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
