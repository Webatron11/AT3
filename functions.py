from json import load

from classes import *

recipes = []
entities = []
fuels = []
items = []
groups = {}
subgroups = {}
choices = []
buffs = []
total_ingredients = []


def ingestRecipes(recipesJson, resourcesJson):
    for recipe in recipesJson:
        ingredients = [Ingredient(recipe=i['name'], required=i['amount'], parent=recipe['key']) for i in
                       recipe['ingredients']]
        group = [i for i in subgroups.keys() if recipe['subgroup'] in subgroups[i]][0]

        recipes.append(
            Recipe(name=recipe['key'], order=recipe['order'], group=group, subgroup=recipe['subgroup'],
                   translated_name=recipe['localized_name']['en'], products=recipe['results'],
                   ingredients=ingredients, energy=recipe['energy_required'], category=recipe['category']))

    for resource in resourcesJson:
        if "required_fluid" not in resource:
            recipes.append(
                Recipe(name=resource['key'], order='', group='', subgroup='',
                       translated_name=resource['localized_name']['en'],
                       energy=0,
                       category=resource['category'], products=resource['results'], ingredients=[]))
        else:
            recipes.append(
                Recipe(name=resource['key'], order='', group='', subgroup='',
                       translated_name=resource['localized_name']['en'],
                       energy=0,
                       category=resource['category'], products=resource['results'],
                       ingredients=[{"name": resource['required_fluid'], "amount": resource['fluid_amount']}]))


def ingestItems(itemsJson):
    for item in itemsJson:
        # if "item" not in item['type']:
        #     continue

        items.append(Item(name=item['key'], order=item['order'], group=item['group'], subgroup=item['subgroup'],
                          translated_name=item['localized_name']['en']))


def ingestEntities(craftingmachinesJson, miningdrillsJson):
    for entity in craftingmachinesJson:
        entities.append(
            Entity(name=entity['key'], translated_name=entity['localized_name']['en'], speed=entity['crafting_speed'],
                   categories=entity['crafting_categories']))
    for entity in miningdrillsJson:
        entities.append(
            Entity(name=entity['key'], translated_name=entity['localized_name']['en'], speed=entity['mining_speed'],
                   categories=entity['resource_categories']))


def ingestGroups(groupsJson):
    # Add all groups from groupsJson to groups as keys
    for group in groupsJson:
        groups.update({group: []})
        subgroups.update({group: [i for i in groupsJson[group]['subgroups'].keys()]})


def populateGroups():
    # Only the items have groups, so need to iterate through items instead of recipes
    for item in items:
        if item in recipes:
            groups[item.group].append(recipes[recipes.index(item)])

    # Remove any unnecessary groups
    pops = []
    for group in groups.keys():
        if not groups[group]:
            pops.append(group)

    for i in pops:
        groups.pop(i)


def ingestFuels(fuelJson):
    for fuel in fuelJson:
        if fuel['category'] == "chemical":
            name = fuel['item_key'].strip().title().replace('-', ' ')
            fuels.append(name)


def ingest():
    with open("vanilla-2.0.10.json") as file:
        json = load(file)
        recipesJson = json['recipes']
        craftingmachinesJson = json['crafting_machines']
        miningdrillsJson = json['mining_drills']
        itemsJson = json['items']
        resourcesJson = json['resources']
        groupsJson = json['groups']
        fuelJson = json['fuel']

    ingestItems(itemsJson)

    ingestGroups(groupsJson)

    ingestRecipes(recipesJson, resourcesJson)

    ingestEntities(craftingmachinesJson, miningdrillsJson)

    ingestFuels(fuelJson)

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
    assembler = [i.name for i in entities if "crafting" in i.categories]
    miner = [i.name for i in entities if "basic-solid" in i.categories]
    furnace = [i.name for i in entities if "smelting" in i.categories]

    chosenAssembler = False
    chosenMiner = False
    chosenFurnace = False

    while True:
        try:
            choice = int(input("1) Assembling Machine \n"
                               "2) Miner \n"
                               "3) Furnace \n"
                               "Input your choice:  "))
        except ValueError:
            print("Invalid entry, please try again. Make sure you are entering a number.")
            continue

        match choice:
            case 1:
                chooseBuilding(assembler)
                chosenAssembler = True
            case 2:
                chooseBuilding(miner)
                chooseResearch()
                chosenMiner = True
            case 3:
                chooseBuilding(furnace)
                if "electric-furnace" not in buffs:
                    chooseBuilding(fuels)
                chosenFurnace = True
            case _:
                print("Invalid choice. Try again with a valid choice (1-4)")

        if chosenAssembler and chosenMiner and chosenFurnace:
            break


def calculate(recipe: Recipe):
    for ingredient in recipe.ingredients:
        requiredAmount = ingredient.required * recipes[recipes.index(recipe)].products[0]['amount']
        ingredientItem = items[items.index(ingredient.recipe)]

        if ingredientItem.name == "petroleum-gas" or ingredientItem.name == "heavy-oil" or ingredientItem.name == "light-oil":
            total_ingredients.append(
                Ingredient(recipe=recipes[recipes.index('basic-oil-processing')], required=requiredAmount,
                           parent=recipe))
            calculate(recipes[recipes.index("basic-oil-processing")])
            continue
        elif ingredientItem.subgroup == "raw-resource":
            total_ingredients.append(Ingredient(recipe=recipes[recipes.index(ingredient.recipe)], parent=recipe))
        else:
            total_ingredients.append(Ingredient(recipe=recipes[recipes.index(ingredient.recipe)], parent=recipe))
        # TODO ADD ORE HANDLING
        calculate(recipes[recipes.index(ingredient.recipe)])
