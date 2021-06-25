"""Utility module with helper functions that don't fit firmly in another module."""


def naive_url_path_join(first: str, second: str, *args) -> str:
    path = first.strip()
    second = second.strip()
    if second in ["/", ""]:
        return path
    if path[-1] != '/':
        path = path + '/'
    if second[0] == "/":
        path = path + second[1:]
    else:
        path = path + "/" + second

    for arg in args:
        arg = arg.strip()
        if arg in ["/", ""]:
            continue
        if arg[0] == "/":
            arg = arg[1:]
        if path[-1] == "/":
            path = path + arg
        else:
            path = path + "/" + arg

    return path
