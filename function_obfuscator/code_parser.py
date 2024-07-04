import clang.cindex
from scraper import find_function
import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.options import Options
import argparse


def extract_function_calls(filename):
    index = clang.cindex.Index.create()
    translation_unit = index.parse(filename)
    function_calls = []

    def traverse(cursor):
        if (
            cursor.kind == clang.cindex.CursorKind.CALL_EXPR
            and cursor.location.file.name == filename
        ):
            function_calls.append(cursor.spelling)
        for child in cursor.get_children():
            traverse(child)

    traverse(translation_unit.cursor)
    return function_calls


def find_main_function_locations(filename):
    index = clang.cindex.Index.create()
    translation_unit = index.parse(filename)
    locations = {}

    def traverse(node):
        if (
            node.kind == clang.cindex.CursorKind.FUNCTION_DECL
            and node.spelling == "main"
        ):
            locations["main_function"] = (node.location.line, node.location.column)
            for child in node.get_children():
                if child.kind == clang.cindex.CursorKind.COMPOUND_STMT:
                    locations["main_body_start"] = (
                        child.location.line,
                        child.location.column,
                    )
                    break
        for child in node.get_children():
            traverse(child)

    traverse(translation_unit.cursor)
    return locations


def insert_code(input_file, output_file, before_main_code, after_main_body_code):
    locations = find_main_function_locations(input_file)
    with open(input_file, "r") as file:
        lines = file.readlines()

    lines.insert(locations["main_body_start"][0], after_main_body_code + "\n")
    lines.insert(locations["main_function"][0] - 1, before_main_code + "\n")

    with open(output_file, "w") as file:
        file.writelines(lines)


def rename_functions(funcs, filename):
    index = clang.cindex.Index.create()
    translation_unit = index.parse(filename)
    function_calls = []

    def traverse(node):
        if node.kind == clang.cindex.CursorKind.CALL_EXPR:
            func_name = node.spelling
            if func_name in funcs:
                function_calls.append(
                    {
                        "name": func_name,
                        "line": node.location.line,
                        "column": node.location.column,
                        "new_name": f"p{func_name}",
                    }
                )
        for child in node.get_children():
            traverse(child)

    traverse(translation_unit.cursor)

    with open(filename, "r") as file:
        lines = file.readlines()

    for call in function_calls:
        line_index = call["line"] - 1
        col_index = call["column"] - 1
        lines[line_index] = (
            lines[line_index][:col_index]
            + call["new_name"]
            + lines[line_index][col_index + len(call["name"]) :]
        )

    with open(filename, "w") as file:
        file.writelines(lines)


def generate_code(calls, database):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--log-level=3")
    driver = webdriver.Edge(options=options)

    df = pd.read_csv(database)
    dlls, typedefs, funcs = set(), [], []
    get_proc_code = ""

    for func in calls:
        if func in df["function_name"].values:
            uri = df.loc[df["function_name"] == func, "uri"].values[0]
            item = find_function(func, uri, driver)
            if item:
                func_name, dll, typedef = item
                get_proc_code += f'{func_name}_t p{func_name} = ({func_name}_t)GetProcAddress(h{dll}, "{func_name}");\n'
                dlls.add(dll)
                typedefs.append(typedef)
                funcs.append(func_name)

    typedef_code = "\n".join(typedefs)
    dll_code = (
        "".join([f'HMODULE h{dll} = LoadLibraryA("{dll}.dll");\n' for dll in dlls])
        + get_proc_code
    )

    return funcs, typedef_code, dll_code


def main():
    parser = argparse.ArgumentParser(
        description="Obfuscate C++ source files by automatically finding and loading WinAPI functions dynamically."
    )
    parser.add_argument(
        "-i", "--input_file", help="The input C++ source file", required=True
    )
    parser.add_argument(
        "-o", "--output_file", help="The output C++ source file", default="output.cpp"
    )
    parser.add_argument(
        "-d",
        "--database",
        default="database.csv",
        help="The CSV file containing the function database",
    )
    args = parser.parse_args()

    calls = extract_function_calls(args.input_file)
    funcs, typedef_code, dll_code = generate_code(calls, args.database)
    insert_code(args.input_file, args.output_file, typedef_code, dll_code)
    rename_functions(funcs, args.output_file)


if __name__ == "__main__":
    main()
