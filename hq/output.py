
def soup_objects_to_text(soup_objects):
    return '\n'.join(obj.prettify().rstrip(' \t\n') for obj in soup_objects)
