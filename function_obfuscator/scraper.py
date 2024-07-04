from bs4 import BeautifulSoup
from function_parser import syntax_parser


def find_function(func_name, uri, driver):

    driver.get(uri)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    ##### Find DLL
    h2_div = soup.find("h2", {"id": "requirements"})
    if h2_div:
        # Navigate to the parent div
        parent_div = h2_div.find_parent("div", {"class": "heading-wrapper"})
        if parent_div:
            next_div = parent_div.find_next_sibling("div", {"class": "has-inner-focus"})
            if next_div:
                table = next_div.find("table")
                if table:
                    # Iterate over the rows in the table
                    rows = table.find("tbody").find_all("tr")
                    for row in rows:
                        cells = row.find_all("td")
                        requirement = cells[0].get_text(strip=True)
                        dll = cells[1].get_text(strip=True).rstrip(".dll")

                        # Check if the requirement is 'DLL'
                        if requirement == "DLL":
                            h2_div = soup.find("h2", {"id": "syntax"})
                            if h2_div:
                                parent_div = h2_div.find_parent(
                                    "div",
                                    {"class": "heading-wrapper"},
                                )
                                if parent_div:
                                    next_div = parent_div.find_next_sibling("pre")
                                    if next_div:
                                        syntax = next_div.get_text(strip=True)

                                        typedef = syntax_parser(syntax)
                                        return [func_name, dll, typedef]
    return False
