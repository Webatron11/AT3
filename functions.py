from json import load

from classes import *

recipes = []
entities = []
fluids = []
items = []
groups = {"logistics": [], "production": [], "intermediate-products": [], "combat": [], 'other': []}
choices = []
buffs = []
total_ingredients = []


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
                   ingredients=recipe['ingredients'], energy=recipe['energy'], category=recipe['category']))


def ingestItems(itemsJson):
    for item in itemsJson:
        item = itemsJson[item]
        if "item" not in item['type']:
            continue

        items.append(Item(name=item['name'], order=item['order'], group=item['group'], subgroup=item['subgroup'],
                          translated_name=item['translated_name']))


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
        itemsJson = json['items']

    ingestRecipes(recipesJson)

    ingestEntities(entitiesJson)

    ingestFluids(fluidsJson)

    ingestItems(itemsJson)

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


def chooseBuilding(buildings: list):
    while True:
        try:
            choice = int(input("".join([f"{i + 1}) {x} \n" for i, x in enumerate(buildings)]) + "Input your choice: "))
        except ValueError:
            print("Invalid entry, please try again. Make sure you are entering a number.")
            continue

        if (len(buildings) + 1) >= choice >= 1:
            buffs.append(buildings[choice - 1].lower().strip().replace(" ", "-"))
            break


def chooseResearch():
    while True:
        try:
            choice = int(input("How many levels of mining productivity research have you done? "))
        except ValueError:
            print("Invalid entry, please try again. Make sure you are entering a number.")
            continue

        if choice >= 0:
            buffs.append(choice * 0.1)
            break
        else:
            print("Invalid entry, please try again. Must be a positive integer.")
            continue


def chooseBuffs():
    # TODO Make these draw from entities[]
    assembler = ["Assembly Machine 1", "Assembly Machine 2", "Assembly Machine 3"]
    miner = ["Burner Mining Drill", "Electric Mining Drill"]
    furnace = ["Stone Furnace", "Steel Furnace", "Electric Furnace"]
    fuels = ["Wood", "Coal", "Solid Fuel", "Rocket Fuel", "Nuclear Fuel"]

    while True:
        try:
            choice = int(input("1) Assembly Machine \n"
                               "2) Miner \n"
                               "3) Furnace \n"
                               "Input your choice:  "))
        except ValueError:
            print("Invalid entry, please try again. Make sure you are entering a number.")
            continue

        match choice:
            case 1:
                chooseBuilding(assembler)
            case 2:
                chooseBuilding(miner)
                chooseResearch()
            case 3:
                chooseBuilding(furnace)
                chooseBuilding(fuels)
            case _:
                print("Invalid choice. Try again with a valid choice (1-4)")

        if "assembly" in buffs and "mining" in buffs and "furnace" in buffs:
            break


def calculate(recipe: Recipe):
    for ingredient in recipe.ingredients:
        if ingredient['type'] == 'fluid':
            total_ingredients.append(
                Ingredient(recipe=fluids[fluids.index(ingredient['name'])], amount=ingredient['amount'], parent=recipe))
            continue
        if items[items.index(ingredient['name'])].subgroup != "raw-resource":
            total_ingredients.append(
                Ingredient(recipe=recipes[recipes.index(ingredient['name'])], amount=ingredient['amount'],
                           parent=recipe))
            calculate(recipes[recipes.index(ingredient['name'])])
        else:
            total_ingredients.append(
                Ingredient(recipe=items[items.index(ingredient['name'])], amount=ingredient['amount'], parent=recipe))
