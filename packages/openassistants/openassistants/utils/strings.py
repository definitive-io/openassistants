def resolve_str_template(template: str, **dependencies) -> str:
    """Resolve a f-string with dataframe"""

    return eval('f"""' + template + '"""', {}, dependencies)
