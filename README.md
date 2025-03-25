# C++ Source File Obfuscator

This script obfuscates C++ source files by automatically finding and loading WinAPI functions dynamically, renaming function calls, and inserting necessary code to handle dynamic loading.

### Dependencies

- `clang.cindex`: For parsing and traversing C++ source files.
- `pandas`: For handling and manipulating the function database.
- `selenium`: For navigating and interacting with web pages.
- `beautifulsoup4`: For parsing HTML content.

### Setup

1. **Install the required libraries**:
    ```bash
    pip install clang pandas selenium
    ```

2. **Download the appropriate WebDriver for your browser (Microsoft Edge in this case)**.

### Script Components

#### Extracting Function Calls `extract_function_calls()`

- **Purpose**: Extracts all function calls from a given C++ source file.
- **Parameters**: 
  - `filename` (str): Path to the C++ source file.
- **Returns**: 
  - `function_calls` (list): List of function calls found in the source file.

#### Finding Main Function Locations `find_main_function_locations()`

- **Purpose**: Finds the location of the `main` function and the start of its body.
- **Parameters**: 
  - `filename` (str): Path to the C++ source file.
- **Returns**: 
  - `locations` (dict): Dictionary containing the line and column locations of the `main` function and the start of its body.

#### Inserting Code `insert_code()`

- **Purpose**: Inserts code before the `main` function and at the start of the `main` function body.
- **Parameters**:
  - `input_file` (str): Path to the input C++ source file.
  - `output_file` (str): Path to the output C++ source file.
  - `before_main_code` (str): Code to insert before the `main` function.
  - `after_main_body_code` (str): Code to insert at the start of the `main` function body.

#### Renaming Functions `rename_functions()`

- **Purpose**: Renames specified functions in the C++ source file by prefixing them with `p`.
- **Parameters**:
  - `funcs` (list): List of function names to rename.
  - `filename` (str): Path to the C++ source file.

#### Generating Code `generate_code()`

- **Purpose**: Generates the code necessary to dynamically load WinAPI functions and creates the corresponding `typedef` declarations.
- **Parameters**:
  - `calls` (list): List of function calls extracted from the source file.
  - `database` (str): Path to the CSV file containing the function database.
- **Returns**:
  - `funcs` (list): List of function names found in the database.
  - `typedef_code` (str): Code for `typedef` declarations.
  - `dll_code` (str): Code for loading DLLs and getting function addresses.

### Example Usage

```bash
python code_parser -i input.cpp -o output.cpp -d database.csv
```
- **Command-Line Arguments**:
  - `-i` / `--input_file` (str): Path to the input C++ source file.
  - `-o` / `--output_file` (str): Path to the output C++ source file (default: `output.cpp`).
  - `-d` / `--database` (str): Path to the CSV file containing the function database (default: `database.csv`).

Below we have the definitions for the auxiliary modules used

## `find_function` from the `scraper.py`

The `find_function` function retrieves and parses the syntax and DLL information for a specified function from a given webpage using Selenium and BeautifulSoup.

### Parameters

- `func_name` (str): The name of the function to find.
- `uri` (str): The URL of the webpage to parse.
- `driver` (selenium.webdriver): The Selenium WebDriver instance used to navigate the webpage.

### Returns

- `list`: A list containing the function name, DLL name, and function syntax if found.
- `bool`: Returns `False` if the function or required information is not found.

### Detailed Explanation

1. **Navigating to the Webpage**:
    - The function starts by navigating to the specified `uri` using the Selenium WebDriver.

2. **Parsing the Webpage**:
    - The `BeautifulSoup` library is used to parse the page source into a manageable format.

3. **Finding the DLL Information**:
    - The function looks for the section of the webpage with the heading "requirements" (`<h2 id="requirements">`).
    - It navigates to the parent `div` and then to its sibling `div` which contains the table with the DLL information.
    - The function iterates over the table rows to find the row where the first cell text is "DLL".
    - It extracts the DLL name from the second cell text, removing the ".dll" suffix.

4. **Finding the Syntax Information**:
    - After finding the DLL information, the function searches for the section of the webpage with the heading "syntax" (`<h2 id="syntax">`).
    - It navigates to the parent `div` and then to its sibling `pre` element which contains the function syntax.
    - The function retrieves the syntax text and parses it using the `syntax_parser` function from the `function_parser` module.

5. **Returning the Results**:
    - If both the DLL and syntax information are found, the function returns a list containing the function name, DLL name, and parsed syntax.
    - If any of the required information is not found, the function returns `False`.


## `syntax_parser` from the `function_parser.py`

The `syntax_parser` function parses a function signature string to create a `typedef` declaration for a function pointer in C/C++.

### Parameters

- `function_signature` (str): The function signature as a string.

### Returns

- `str`: The `typedef` declaration for a function pointer.

### Detailed Explanation

1. **Splitting the Function Signature**:
    - The function signature is split into individual lines using the newline character (`\n`).


2. **Parsing the Function Signatures**:
    - The first line is split to extract the `return_type` and `func_name`.
    - The parameters are processed line by line, starting from the second line which results in the `params` list.
    - Extra whitespace is removed, and trailing commas are stripped along with other unwanted characters such as [ ].
    - The `typedef` declaration is constructed with the following format 
```cpp
typedef return_type(WINAPI *func_name_t)(params);
```


## PDF Link Extractor and Function Information Scraper from the `pdf_parser.py`

This script extracts function names and their associated links from a PDF file (get the pdf file from the WinAPI documentation [PDF database](https://learn.microsoft.com/pdf?url=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fwindows%2Fwin32%2Fapiindex%2Ftoc.json)) and retrieves detailed information about these functions from specified URLs using Selenium and BeautifulSoup.

### Purpose
 Extracts function names and associated links from a PDF, then retrieves and stores detailed information about these functions.
### Parameters
  - `pdf_path` (str): Path to the PDF file.
### Workflow
  - Opens the PDF file using `pymupdf`.
  - Iterates through pages (from page 5 to 5616) and prints the current page number.
  - Retrieves all links on the current page.
  - For each link that contains a URI, checks if it starts with the specified URL pattern.
  - Extracts the text associated with the link (function name) and retrieves detailed information using `find_function`.
  - Stores the retrieved information in a DataFrame.





