import pymupdf  # PyMuPDF
import pandas as pd
from scraper import find_function
from selenium import webdriver
from selenium.webdriver.edge.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("--log-level=3")
driver = webdriver.Edge(options=options)

def extract_links_with_text(pdf_path):
    # Open the PDF file
    document = pymupdf.open(pdf_path)

    # Iterate through each page
    for page_num in range(5, 10):
        page = document[page_num]
        print(page_num)

        # Get all links on the page
        links = page.get_links()

        for link in links:
            # Check if the link contains a URI
            if "uri" in link:
                uri = link["uri"]
                if uri.startswith(
                    "https://learn.microsoft.com/en-us/windows/win32/api/"
                ):
                    # Extract the text associated with the link
                    rect = pymupdf.Rect(link["from"])
                    func_name = page.get_text("text", clip=rect).strip()
                    item = find_function(func_name, uri, driver)
                    if item:
                        df.loc[len(df.index)] = item


# Example usage
df = pd.DataFrame(columns=["function_name", "dll","typedef"])
pdf_path = "win32api.pdf"
extract_links_with_text(pdf_path)
unique_df = df.drop_duplicates(subset=["function_name"])
unique_df.to_csv("function_database.csv", index=False)
