from json import load

recipes = []
entities = []
fluids = []


class Item:
    def __init__(self, name: str, order: str, group: str, subgroup: str, translated_name: str):
        self.name = name
        self.order = order
        self.group = group
        self.subgroup = subgroup
        self.translated_name = translated_name


class Recipe(Item):
    def __init__(self, ingredients: list, products: list, energy: float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ingredients = ingredients
        self.products = products
        self.energy = energy


class Entity(Item):
    def __init__(self, crafting_categories: list, crafting_speed: float, manufacturing_type: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crafting_speed = crafting_speed
        self.manufacturing_type = manufacturing_type
        self.crafting_categories = crafting_categories


def ingest():
    with open("recipes-og.json") as file:
        json = load(file)
        recipesJson = json['recipes']
        entitiesJson = json['entities']
        fluidsJson = json['fluids']

    for recipe in recipesJson:
        recipe = recipesJson[recipe]
        for ingredient in recipe['ingredients']:
            if 'probability' in ingredient:
                ingredient.pop('probability')

        for product in recipe['products']:
            recipe[product].pop('probability')

        recipe.pop('allowed_effects')
        recipe.pop('productivity_bonus')
        recipe.pop('main_product')
        recipe.pop('maximum_productivity')
        recipes.append(
            Recipe(name=recipe['name'], order=recipe['order'], group=recipe['group'], subgroup=recipe['subgroup'],
                   translated_name=recipe['translated_name'], products=recipe['products'],
                   ingredients=recipe['ingredients'], energy=recipe['energy']))

    for entity in entitiesJson:
        entity = entitiesJson[entity]
        entity.pop('module_inventory_size')
        entity.pop('width')
        entity.pop('height')
        entity.pop('flags')
        if 'effect_receiver' in entity:
            entity.pop('effect_receiver')
        if 'drain' in entitiesJson[entity]:
            entity.pop('drain')
        if 'allowed_effects' in entitiesJson[entity]:
            entity.pop('allowed_effects')
        entity.append(
            Entity(name=entity['name'], order=entity['order'], group=entity['group'], subgroup=entity['subgroup'],
                   translated_name=entity['translated_name'], crafting_categories=entity['crafting_categories'],
                   manufacturing_type=entity['type'], crafting_speed=entity['crafting_speed']))

    for fluid in fluidsJson:
        fluid = fluidsJson[fluid]
        if fluid['name'].contains('parameter') or fluid['name'].contains('fluid-unknown'):
            fluidsJson.pop(fluid['name'])
        fluid.pop('group')
        fluid.pop('subgroup')
        fluid.pop('fuel_value')
        fluids.append(Item(name=fluid['name'], order=fluid['order'], group=fluid['group'], subgroup=fluid['subgroup'],
                           translated_name=fluid['translated_name']))

ingest()
print(fluids, entities, recipes)
