# Automated-Product-Catalogue-Scraper

THE REQUEST \n
Create a Python script to extract product information from an e-commerce website (TomKardy), specifically from two categories containing original and tester UAE packaging products. The goal was to collect product titles, URLs, original prices, and current prices across all pages and organize the extracted data into an Excel spreadsheet.

THE APPROACH
I developed an automated web scraping script using Selenium to navigate through all the pages of the selected product category. The script identifies individual product cards using CSS selectors and XPath, extracts product titles, URLs, original prices, and current prices, and cleans the extracted price values by removing unnecessary characters such as currency symbols and whitespace. It also converts relative URLs into absolute URLs, removes duplicate products based on their URLs, and handles page loading timeouts to ensure reliable data extraction.

LANGUAGE AND LIBRARIES
Programming Language: Python
Libraries: Selenium, OpenPyXL, Pandas, Pathlib, Urllib.parse 
