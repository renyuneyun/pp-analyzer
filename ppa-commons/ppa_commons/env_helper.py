import csv


_entity_category_hierarchy = {}


def get_entity_category_hierarchy(entity_category_hierarchy_file):
    '''
    The entity category hierarchy contains multiple lines, each representing one category; the number of indents (`\t`) at the beginning of a line indicates the level of the category.
    There will be no cycles. One category may belong to multiple parental-categories.
    This function returns the category hierarchy as a nested dictionary, where the key is the category name, and the value is a list of subcategories.
    '''
    global _entity_category_hierarchy
    if entity_category_hierarchy_file in _entity_category_hierarchy:
        return _entity_category_hierarchy[entity_category_hierarchy_file]
    with open(entity_category_hierarchy_file) as f:
        lines = f.readlines()
    lines = [line.rstrip() for line in lines]
    res = {}
    stack = []
    for line in lines:
        level = line.count('\t')
        name = line.strip()
        if level > len(stack):
            raise ValueError("Invalid hierarchy with exceptional indentation")
        l = res
        for i in range(level):
            l = l[stack[i]]
        l[name] = {}
        stack = stack[:level] + [name]
    _entity_category_hierarchy[entity_category_hierarchy_file] = res
    return _entity_category_hierarchy[entity_category_hierarchy_file]


def get_entity_category_definitions(entity_category_definition_file):
    '''
    The entity category definition is a CSV file with two columns: category, definition.
    This function returns the category definitions as a dictionary, where the key is the category name, and the value is the definition.
    '''
    with open(entity_category_definition_file) as f:
        reader = csv.reader(f)
        next(reader)
        return {line[0]: line[1] for line in reader}
