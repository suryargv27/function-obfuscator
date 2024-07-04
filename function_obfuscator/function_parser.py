import re


def syntax_parser(function_signature):
    lines = function_signature.split("\n")
    n = len(lines)
    if n == 1:
        first = lines[0].split()
        return_type = first[:-1]
        return_type = [s for s in return_type if not s.endswith("API")]
        func_name = first[-1].rstrip("();")
        return_type = " ".join(return_type)

        typedef = f"typedef {return_type}(WINAPI *{func_name}_t)();"
        return typedef

    first = lines[0].split()
    return_type = first[:-1]
    return_type = [s for s in return_type if not s.endswith("API")]
    func_name = first[-1].rstrip("(")
    return_type = " ".join(return_type)

    params = []

    for i in range(1, n - 1):
        result = re.sub(r"\[.*?\]", "", lines[i]).strip().rstrip(",")
        result = re.sub(r"\s+", " ", result)
        params.append(result)
    params = ", ".join(params)

    typedef = f"typedef {return_type}(WINAPI *{func_name}_t)({params});"
    return typedef
