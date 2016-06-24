"""
This module is full of little recursive functions that help with
converting dotted-path notations into nested dicts, and vice
versa. A dotted-path, or "flattened" dict might look like this:

    {'aperta.dev.service': 'vault:v1:asdfhjklkjhfdsa'}

The above example approximates how the data is stored in Dewey.

As an "expanded" or "nested" dict, the same data would be:

    {'aperta': {'dev': {'service': 'vault:v1:lkjhgfdsasdfghjkl'}}}

The latter format is consistent with the legacy YAML structure
PLOS has used in its file-based salt-secrets repositories.
"""


def add_keys(destdict, srclist, value=None):
    """
    nests keys from srclist into destdict, with optional
    value set on the final key
    """
    if len(srclist) > 1:
        destdict[srclist[0]] = {}
        destdict[srclist[0]] = destdict.get(srclist[0], {})
        add_keys(destdict[srclist[0]], srclist[1:], value)
    else:
        destdict[srclist[0]] = value


def expand_dotted_path(dotted_path, value=None):
    """
    expands a dotted path into a nested dict; if value is set, the
    final key in the path will be set to value
    """
    dot_list = dotted_path.split('.')
    nested_dict = {}
    add_keys(nested_dict, dot_list, value)
    return nested_dict


def find_keys(searchdict, searchvalue):
    """
    returns a list of all the parent keys for searchvalue in searchdict
    """
    for key, value in searchdict.items():
        if isinstance(value, dict):
            path = find_keys(value, searchvalue)
            if path:
                return [key] + path
        elif value == searchvalue:
            return [key]


def extract_string_values(searchdict, strings=[]):
    """
    returns a list of all string values extracted from (nested) searchdict
    """
    for key, value in searchdict.items():
        if isinstance(value, dict):
            extract_string_values(value)
        elif isinstance(value, str) and value not in strings:
            strings.append(value)
    return strings


def flatten_dict(nested):
    """
    converts a nested dict into a flattened dict, with keys in dotted path notation
    """
    flattened = {}
    strings = extract_string_values(nested)
    for string in strings:
        try:
            dotted_path = '.'.join(find_keys(nested, string))
            flattened[dotted_path] = string
        except TypeError:
            pass
    return flattened


def merge_dicts(source, destination):
    """
    performs a deep merge of two nested dicts
    """
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge_dicts(value, node)
        else:
            destination[key] = value
    return destination


def expand_flattened_dict(flattened):
    """
    expands a flattened dict into a nested dict - this expanded
    format provides direct compatibility with our legacy salt states
    """
    merged = {}
    for key, value in flattened.items():
        expanded = expand_dotted_path(key, value)
        merged = merge_dicts(merged, expanded)
    return merged

