from json import load

recipes = []
entities = []
fluids = []
groups = {"logistics": [], "production": [], "intermediate-products": [], "combat": [], 'other': []}
global recipeChoice


class Item:
    def __init__(self, name: str, order: str, group: str, subgroup: str, translated_name: str):
        self.name = name
        self.order = order
        self.group = group
        self.subgroup = subgroup
        self.translated_name = translated_name

    def __str__(self):
        return self.translated_name


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


def ingestRecipes(recipesJson):
    for recipe in recipesJson:
        recipe = recipesJson[recipe]
        for ingredient in recipe['ingredients']:
            if 'probability' in ingredient:
                ingredient.pop('probability')

        for product in recipe['products']:
            product.pop('probability')

        recipe.pop('allowed_effects')
        recipe.pop('productivity_bonus')
        if "main_product" in recipe:
            recipe.pop('main_product')
        recipe.pop('maximum_productivity')
        recipes.append(
            Recipe(name=recipe['name'], order=recipe['order'], group=recipe['group'], subgroup=recipe['subgroup'],
                   translated_name=recipe['translated_name'], products=recipe['products'],
                   ingredients=recipe['ingredients'], energy=recipe['energy']))


def ingestEntities(entitiesJson):
    for entity in entitiesJson:
        entity = entitiesJson[entity]

        if 'parameter' in entity['name'] or 'recipe-unknown' in entity['name']:
            continue

        entity.pop('module_inventory_size')
        entity.pop('width')
        entity.pop('height')
        entity.pop('flags')
        if 'effect_receiver' in entity:
            entity.pop('effect_receiver')
        if 'drain' in entity:
            entity.pop('drain')
        if 'allowed_effects' in entity:
            entity.pop('allowed_effects')
        if "crafting_categories" in entity:
            entities.append(
                Entity(name=entity['name'], order=entity['order'], group=entity['group'], subgroup=entity['subgroup'],
                       translated_name=entity['translated_name'], crafting_categories=entity['crafting_categories'],
                       manufacturing_type=entity['type'], crafting_speed=entity['crafting_speed']))
        else:
            entities.append(
                Entity(name=entity['name'], order=entity['order'], group=entity['group'], subgroup=entity['subgroup'],
                       translated_name=entity['translated_name'], crafting_categories=[],
                       manufacturing_type=entity['type'], crafting_speed=0))


def ingestFluids(fluidsJson):
    for fluid in fluidsJson:
        fluid = fluidsJson[fluid]
        if 'parameter' in fluid['name'] or 'fluid-unknown' in fluid['name']:
            continue
        fluid.pop('group')
        fluid.pop('subgroup')
        fluid.pop('fuel_value')
        fluids.append(Item(name=fluid['name'], order=fluid['order'], group='fluids', subgroup='fluid',
                           translated_name=fluid['translated_name']))


def populateGroups():
    for recipe in recipes:
        groups[recipe.group].append(recipe)


def ingest():
    with open("recipes-og.json") as file:
        json = load(file)
        recipesJson = json['recipes']
        entitiesJson = json['entities']
        fluidsJson = json['fluids']

    ingestRecipes(recipesJson)

    ingestEntities(entitiesJson)

    ingestFluids(fluidsJson)

    populateGroups()


def printRecipes(group: list):
    for item in group:
        print(item)


def chooseRecipe():
    while True:
        choice = str(input("What is the name of the recipe you'd like?"))
        choice = choice.lower().strip()

        try:
            for recipe in recipes:
                if recipe.name == choice:
                    choice = recipe
        except KeyError:
            print("Invalid recipe name. Please try again.")
            continue
        else:
            break

    recipeChoice = choice


def haha_it_chooses():
    while True:  # Catch conversion errors e.g. not a valid entry
        choice = int(input("1. Choose a recipe \n"
                           "2. Return to category menu \n"
                           "Input a number: "))
        match choice:
            case 1:
                chooseRecipe()
                break
            case 2:
                displayCategories()
                break
            case _:
                print("Invalid choice. Try again with a valid choice (1 or 2)")
                continue


def displayCategories():
    for i, group in enumerate(groups):
        print(f"{i + 1}) {group.upper()}")

    while True:
        try:
            choice = int(input("Which category would you like to look at? (Enter a number): "))
        except ValueError:
            print("Invalid input. Please try again, with an integer.")
            continue
        else:
            if (len(groups) + 1) >= choice >= 1:
                printRecipes(groups[list(groups)[choice - 1]])
                break
            else:
                print("Invalid selection. Please try again.")
                continue
    haha_it_chooses()


ingest()
displayCategories()
