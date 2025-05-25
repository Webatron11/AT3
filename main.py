from json import load

class Item:
    def __init__(self, name: str, order: str, group: str, subgroup: str, translated_name: str):
        self.name = name
        self.order = order
        self.group = group
        self.subgroup = subgroup
        self.translated_name = translated_name

class Recipe(Item):
    def __init__(self, ingredients: list, products: list, *args, **kwargs):
        super.__init__(*args, **kwargs)
        self.ingredients = ingredients
        self.products = products


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
        if 'effect_receiver' in entities[entity]:
            entities[entity].pop('effect_receiver')
        if 'drain' in entities[entity]:
            entities[entity].pop('drain')
        if 'allowed_effects' in entities[entity]:
            entities[entity].pop('allowed_effects')

    for fluid in fluids:
        if fluid.contains('parameter') or fluid.contains('fluid-unknown'):
            fluids.pop(fluid)
        fluids[fluid].pop('group')
        fluids[fluid].pop('subgroup')
        fluids[fluid].pop('fuel_value')
