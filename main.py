from json import load


def ingest():
    with open("recipes-og.json") as file:
        json = load(file)
        recipes = json['recipes']
        entities = json['entities']
        fluids = json['fluids']

    for recipe in recipes:
        for ingredient in recipes[recipe]['ingredients']:
            recipes[recipe][ingredient].pop('probability')

        for product in recipes[recipe]['products']:
            recipes[recipe][product].pop('probability')

        recipes[recipe].pop('allowed_effects')
        recipes[recipe].pop('productivity_bonus')
        recipes[recipe].pop('main_product')
        recipes[recipe].pop('maximum_productivity')

    for entity in entities:
        entities[entity].pop('module_inventory_size')
        entities[entity].pop('width')
        entities[entity].pop('height')
        entities[entity].pop('flags')

    for fluid in fluids:
        if fluid.contains('parameter') or fluid.contains('fluid-unknown'):
            fluids.pop(fluid)
        fluids[fluid].pop('group')
        fluids[fluid].pop('subgroup')
        fluids[fluid].pop('fuel_value')
