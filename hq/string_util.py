

def truncate_string(s, length=50, one_line=True, suffix='...'):
    if len(s) <= length:
        result = s
    else:
        result = s[:length].rsplit(' ', 1)[0] + suffix
    if one_line:
        result = result.replace('\n', '\\n')
    return result
