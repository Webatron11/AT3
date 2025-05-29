from json import load

recipes = []
entities = []
fluids = []
groups = {"logistics": [], "production": [], "intermediate-products": [], "combat": [], 'other': []}
choices = []
buffs = {}


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

    def __eq__(self, other):
        return self.name == other

    def printIngredients(self):
        print("---Ingredients---")
        for ingredient in self.ingredients:
            print(f"{ingredient['amount']}x {ingredient['name'].title().replace("-", " ")}")

    def printProducts(self):
        print("---Products---")
        for product in self.products:
            print(f"{product['amount']}x {product['name'].title().replace("-", " ")}")


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
        try:
            choice = str(input("What is the name of the recipe you'd like? "))
            choice = choice.lower().strip().replace(" ", "-")
        except ValueError:
            print("Invalid entry, please try again. Make sure you are entering text.")
            continue

        try:
            index = recipes.index(choice)
        except ValueError:
            print("Invalid recipe name. Please try again.")
            continue
        else:
            break

    recipes[index].printProducts()
    recipes[index].printIngredients()

    while True:
        try:
            choice = int(input("1) Choose this recipe \n"
                               "2) Choose another recipe \n"
                               "Input your choice:  "))
        except ValueError:
            print("Invalid entry, please try again. Make sure you are entering a number.")
            continue

        match choice:
            case 1:
                choices.append(recipes[index])
                break
            case 2:
                chooseRecipe()
                break
            case _:
                print("Invalid choice. Try again with a valid choice (1 or 2)")
                continue


def displayCategories():
    for i, group in enumerate(groups):
        print(f"{i + 1}) {group.title()}")

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

    while True:
        try:
            choice = int(input("1) Choose a recipe \n"
                               "2) Return to category menu \n"
                               "Input your choice:  "))
        except ValueError:
            print("Invalid entry, please try again. Make sure you are entering a number.")
            continue

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


def chooseBuilding(buildings: list, category: str):
    while True:
        try:
            choice = int(input("".join([f"{i + 1}) {x} \n" for i, x in enumerate(buildings)]) + "Input your choice: "))
        except ValueError:
            print("Invalid entry, please try again. Make sure you are entering a number.")
            continue

        if (len(buildings) + 1) >= choice >= 1:
            buffs.update({category: buildings[choice - 1].lower().strip().replace(" ", "-")})
            break


def chooseBuffs():
    # TODO Make these draw from entities[]
    assembler = ["Assembly Machine 1", "Assembly Machine 2", "Assembly Machine 3"]
    miner = ["Burner Mining Drill", "Electric Mining Drill"]
    furnace = ["Stone Furnace", "Steel Furnace", "Electric Furnace"]

    while True:
        try:
            choice = int(input("1) Assembly Machine \n"
                               "2) Miner \n" # TODO Add mining prod
                               "3) Furnace \n" # TODO Select fuel source
                               "Input your choice:  "))
        except ValueError:
            print("Invalid entry, please try again. Make sure you are entering a number.")
            continue

        match choice:
            case 1:
                chooseBuilding(assembler, "assembly")
            case 2:
                chooseBuilding(miner, "miner")
            case 3:
                chooseBuilding(furnace, "furnace")
            case _:
                print("Invalid choice. Try again with a valid choice (1-4)")


# ingest()
# displayCategories()
# print([str(i) for i in choices])

chooseBuilding(["Assembly Machine 1", "Assembly Machine 2", "Assembly Machine 3"], "")
