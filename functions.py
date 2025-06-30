from json import load
from prettytable import PrettyTable
from math import log

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
rate = 0
ingredientsTotal = {}
ingredientsDict = {}
tableRows = []

invalidEntry = "Invalid entry, please try again. Make sure you are entering an integer."
invalidChoice = "Invalid choice. Try again with a valid choice "


def roundUp(number: float) -> float:
    rounded = round(number, 1)
    if rounded > number:
        return rounded
    elif rounded == number:
        return number
    else:
        return round(number + 0.05, 1)


def ingestRecipes(recipesJson, resourcesJson):
    global subgroups
    global recipes

    for recipe in recipesJson:
        ingredients = [Ingredient(recipe=i['name'], required=i['amount'], parent=recipe['key']) for i in
                       recipe['ingredients']]
        group = subgroups[recipe['subgroup']]

        recipes.append(
            Recipe(name=recipe['key'], order=recipe['order'], group=group, subgroup=recipe['subgroup'],
                   translated_name=recipe['localized_name']['en'], products=recipe['results'],
                   ingredients=ingredients, energy=recipe['energy_required'], category=recipe['category']))

    for resource in resourcesJson:
        if "required_fluid" not in resource:
            recipes.append(
                Recipe(name=resource['key'], order='', group='', subgroup='',
                       translated_name=resource['localized_name']['en'],
                       energy=resource['mining_time'],
                       category=resource['category'], products=resource['results'], ingredients=[]))
        else:
            recipes.append(
                Recipe(name=resource['key'], order='', group='', subgroup='',
                       translated_name=resource['localized_name']['en'],
                       energy=resource['mining_time'],
                       category=resource['category'], products=resource['results'],
                       ingredients=[Ingredient(required=resource['fluid_amount'], parent=resource['key'],
                                               recipe=resource['required_fluid'])]))


def ingestItems(itemsJson):
    global items

    for item in itemsJson:
        items.append(Item(name=item['key'], order=item['order'], group=item['group'], subgroup=item['subgroup'],
                          translated_name=item['localized_name']['en']))


def ingestEntities(craftingMachinesJson, miningDrillsJson):
    global entities

    for entity in craftingMachinesJson:
        entities.append(
            Entity(name=entity['key'], translated_name=entity['localized_name']['en'], speed=entity['crafting_speed'],
                   categories=entity['crafting_categories']))
    for entity in miningDrillsJson:
        entities.append(
            Entity(name=entity['key'], translated_name=entity['localized_name']['en'], speed=entity['mining_speed'],
                   categories=entity['resource_categories']))


def ingestGroups(groupsJson):
    global groups
    global subgroups

    # Add all groups from groupsJson to groups as keys
    keys = []
    for group in groupsJson:
        keys.append(group)

    groups.update({}.fromkeys(keys))

    # Add all subgroups to a dictionary with the subgroup name as key and group name as value
    for group in keys:
        for i in groupsJson[group]['subgroups']:
            subgroups.update({i: group})


def populateGroups():
    global groups
    global subgroups

    # Only the items have groups, so need to iterate through items instead of recipes
    for group in groups.keys():
        groups[group] = ([i for i in recipes if i.group == group])

    # Remove any unnecessary groups
    pops = []
    for group in groups.keys():
        if not groups[group]:
            pops.append(group)

    for i in pops:
        groups.pop(i)


def ingestFuels(fuelJson):
    global fuels

    for fuel in fuelJson:
        if fuel['category'] == "chemical":
            name = fuel['item_key'].strip().title().replace('-', ' ')
            fuels.append(name)


def ingest():
    with open("vanilla-2.0.10.json") as file:
        json = load(file)
        recipesJson = json['recipes']
        craftingMachinesJson = json['crafting_machines']
        miningDrillsJson = json['mining_drills']
        itemsJson = json['items']
        resourcesJson = json['resources']
        groupsJson = json['groups']
        fuelJson = json['fuel']

    ingestItems(itemsJson)

    ingestGroups(groupsJson)

    ingestRecipes(recipesJson, resourcesJson)

    ingestEntities(craftingMachinesJson, miningDrillsJson)

    ingestFuels(fuelJson)

    populateGroups()


def printRecipes(group: list):
    skip = 0
    for i, item in enumerate(group):
        if "1" in item.name:
            name = item.name[:-2]
        else:
            name = item.name
        if name[:-2] in group[i - 1].name and i <= skip:
            continue
        if i + 1 < len(group):
            if name in group[i + 1].name and "-2" in group[i + 1].name:
                print(name.title().replace('-', " ") + " (1-3)")
                skip = i + 2
                continue

        print(item.name.title().replace('-', " "))


def chooseRate():
    global rate

    print("\n-------------------- Rate of Production --------------------\n"
          "Select the unit of the rate at which you want your desired\n"
          "recipe to be produced. \n")

    while True:
        choice = input("1) Items Per Second \n"
                       "2) Items Per Minute \n"
                       "3) Items Per Hour \n"
                       "Input your choice: ")
        try:
            choice = int(choice)
        except ValueError:
            print(invalidEntry)
            continue

        if 1 <= choice <= 3:
            rate = 60 ** (choice - 1)
            break
        else:
            print(invalidChoice + "(1-3)")
            continue


def chooseAmount():
    global rate

    while True:
        try:
            choice = int(input(f"Input desired amount per {"second" if log(rate, 60) == 0 else "minute" if log(rate, 60) == 1 else "hour"}: "))
        except ValueError:
            print("Invalid input, please try again. Make sure you are inputting a number.")
            continue
        else:
            return choice


def chooseRecipe():
    global recipes
    global choices

    index = 0

    while True:
        choice = input("What is the name of the recipe you'd like? ")
        try:
            choice = str(choice)
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

    print()
    recipes[index].printProducts()
    recipes[index].printIngredients()
    print()

    while True:
        choice = input("1) Choose this recipe \n"
                       "2) Choose another recipe \n"
                       "3) Return to categories \n"
                       "Input your choice:  ")
        try:
            choice = int(choice)
        except ValueError:
            print("Invalid entry, please try again. Make sure you are entering a number.")
            continue

        match choice:
            case 1:
                choices.append([recipes[index], chooseAmount()])
                break
            case 2:
                chooseRecipe()
                break
            case 3:
                displayCategories()
                break
            case _:
                print("Invalid choice. Try again with a valid choice (1 or 2)")
                continue


def displayCategories():
    global groups

    print("\n------------------------- Categories -------------------------\n"
          "Pick a category to view the recipes within that category. Then\n"
          "you can select a recipe and the desired quantity.\n")

    for i, group in enumerate(groups):
        print(f"{i + 1}) {group.title().replace('-', " ")}")
    print(f"{len(groups) + 1}) Return home")

    while True:
        choice = input("Which category would you like to look at? (Enter a number): ")

        try:
            choice = int(choice)
        except ValueError:
            print(invalidEntry)
            continue
        else:
            if len(groups) >= choice >= 1:
                print("\n")
                printRecipes(groups[list(groups)[choice - 1]])
                break
            elif (len(groups) + 1) >= choice >= len(groups):
                mainMenu()
                break
            else:
                print(invalidChoice + f" (Between 1 and {len(groups) + 1})")
                continue

    print("\n------------------------- Recipes -------------------------\n")

    while True:
        choice = input("1) Choose a recipe \n"
                       "2) Return to category menu \n"
                       "Input your choice:  ")
        try:
            choice = int(choice)
        except ValueError:
            print(invalidEntry)
            continue

        match choice:
            case 1:
                chooseRecipe()
                break
            case 2:
                displayCategories()
                break
            case _:
                print(invalidChoice + "(1 or 2)")
                continue


def chooseBuilding(buildings: list):
    global buffs

    while True:
        choice = input("".join([f"{i + 1}) {x.title().replace("-", " ")} \n" for i, x in enumerate(buildings)]) + "Input your choice: ")
        try:
            choice = int(choice)
        except ValueError:
            print("Invalid entry, please try again. Make sure you are entering a number.")
            continue

        if (len(buildings) + 1) >= choice >= 1:
            buffs.append(buildings[choice - 1].lower().strip().replace(" ", "-"))
            break


def chooseResearch():
    global buffs

    while True:
        choice = input("How many levels of mining productivity research have you done? ")
        try:
            choice = int(choice)
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
    print("\n---------------------------- Buffs ----------------------------\n"
          "Here you choose which assembly machine tier you use, the mining drill \n"
          "you use, and the furnace you use. For the furnace, you also choose the \n"
          "fuel you'll use (unless its electric), and for the mining drill you\n"
          "also enter how many 'Mining Productivity' researches you have done.\n")

    assembler = [i.name for i in entities if "crafting" in i.categories]
    miner = [i.name for i in entities if "basic-solid" in i.categories]
    furnace = [i.name for i in entities if "smelting" in i.categories]

    chosenAssembler = False
    chosenMiner = False
    chosenFurnace = False

    while not (chosenAssembler and chosenMiner and chosenFurnace):
        try:
            choice = int(input(f"{"* " if not chosenAssembler else ""}1) Assembling Machine \n"
                               f"{"* " if not chosenMiner else ""}2) Miner \n"
                               f"{"* " if not chosenFurnace else ""}3) Furnace \n"
                               "Input your choice:  "))
        except ValueError:
            print("Invalid entry, please try again. Make sure you are entering a number.")
            continue

        if choice == 1 and not chosenAssembler:
            chooseBuilding(assembler)
            chosenAssembler = True
            continue
        elif choice == 2 and not chosenMiner:
            chooseBuilding(miner)
            chooseResearch()
            chosenMiner = True
            continue
        elif choice == 3 and not chosenFurnace:
            chooseBuilding(furnace)
            if "electric-furnace" not in buffs:
                chooseBuilding(fuels)
            chosenFurnace = True
            continue
        elif chosenAssembler or chosenMiner or chosenFurnace:
            print("Already chosen this option, please try again.")
        else:
            print("Invalid choice. Try again with a valid choice (1-4)")


def calculateIngredients(recipe: Recipe):
    global total_ingredients
    global recipes

    for ingredient in recipe.ingredients:
        ingredientItem = items[items.index(ingredient.recipe)]

        if ingredientItem.name == "petroleum-gas" or ingredientItem.name == "heavy-oil" or ingredientItem.name == "light-oil":
            total_ingredients.append(
                Ingredient(recipe=recipes[recipes.index('advanced-oil-processing')], parent=recipe))
            calculateIngredients(recipes[recipes.index("advanced-oil-processing")])
            continue
        elif "fish" in ingredientItem.name or "wood" in ingredientItem.name:
            continue
        elif "uranium-2" in ingredientItem.name:
            total_ingredients.append(Ingredient(recipe=recipes[recipes.index('uranium-processing')], parent=recipe))
            calculateIngredients(recipes[recipes.index("uranium-processing")])
            continue
        elif "solid-fuel" in ingredientItem.name:
            total_ingredients.append(Ingredient(recipe=recipes[recipes.index("solid-fuel-from-light-oil")], parent=recipe))
            calculateIngredients(recipes[recipes.index("solid-fuel-from-light-oil")])
            continue
        else:
            total_ingredients.append(Ingredient(recipe=recipes[recipes.index(ingredient.recipe)], parent=recipe))

        calculateIngredients(recipes[recipes.index(ingredient.recipe)])


def calculateResult():
    for choice in choices:
        total_ingredients.append(Ingredient(recipe=choice[0], required=choice[1], parent=choice[0]))
        calculateIngredients(choice[0])

    for ingredient in total_ingredients:
        ingredient.calculate(entities, buffs, total_ingredients, rate)


def collateResult():
    global ingredientsDict
    global ingredientsTotal

    ingredientsSet = set([i.recipe.name for i in total_ingredients])
    ingredientsDict = {}.fromkeys(ingredientsSet)

    for i in ingredientsSet:
        ingredientsDict[i] = []

    for key in ingredientsSet:
        for ingredient in total_ingredients:
            if ingredient.recipe.name == key:
                ingredientsDict[key].append([ingredient.parent, [ingredient.machines_needed, 0], [ingredient.required, 0]])

    ingredientsTotal = {}.fromkeys(ingredientsSet)

    for i in ingredientsSet:
        ingredientsTotal[i] = [0, 0]

    for key in ingredientsSet:
        totalRequired = 0
        totalMachines = 0

        for ingredient in ingredientsDict[key]:
            totalRequired += ingredient[2][0]
            totalMachines += ingredient[1][0]

        ingredientsTotal[key] = [totalRequired, totalMachines]


def printDetails(choice: int):
    global total_ingredients
    global tableRows
    global ingredientsTotal

    ingredientName = tableRows[choice].lower().replace(" ", "-")
    ingredients = []
    dependants = []
    output = []
    ingredientTotal = ingredientsTotal[ingredientName][0]

    for ingredient in total_ingredients:
        if ingredient.parent.name == ingredientName:
            ingredients.append(ingredient)
        if ingredient.recipe.name == ingredientName:
            dependants.append(ingredient)

    ingredientsSet = set([i.recipe.name for i in ingredients])
    dependantsSet = set([i.parent.name for i in dependants])

    ingredientsDict = {}.fromkeys(ingredientsSet)
    dependantsDict = {}.fromkeys(dependantsSet)

    for i in ingredientsSet:
        ingredientsDict[i] = [0, 0]

    for i in dependantsSet:
        dependantsDict[i] = [0, 0]

    for item in ingredients:
        ingredientsDict[item.recipe.name][0] += item.required
        ingredientsDict[item.recipe.name][1] += item.machines_needed

    for item in dependants:
        dependantsDict[item.parent.name][0] += item.required
        dependantsDict[item.parent.name][1] += item.machines_needed

    output.append("-----Ingredients-----")
    for key in ingredientsSet:
        array = ingredientsDict[key]
        output.append(f"{array[0]} x {key.title().replace("-", " ")} - {array[1]} machines")

    output.append("-----Dependants-----")

    for key in dependantsSet:
        array = dependantsDict[key]
        percent = array[0] / ingredientTotal
        output.append(f"{array[0]} x {key.title().replace("-", " ")} ({percent * 100}%) - {array[1]} machines")

    for i in output:
        print(i)


def detailResults():
    global tableRows

    while True:
        length = len(tableRows)

        choice = input(f"(0-{length}) Select an ingredient for more information \n"
                       f"({length}) Return Home \n"
                       f"Input your choice: ")

        try:
            choice = int(choice)
        except ValueError:
            print("Invalid entry, please try again. Make sure you are entering a number.")
            continue

        if 0 <= choice <= length - 1:
            printDetails(choice)
            continue
        elif choice == length:
            break
        else:
            print(f"Please try again with a number between 0 and {length}")
            continue


def printResults():
    global ingredientsTotal
    global ingredientsDict
    global total_ingredients
    global choices
    global tableRows

    table = PrettyTable(['Number', 'Recipe', 'Items Needed', 'Machines Needed', 'distance'])

    for i, ingredient in enumerate(ingredientsTotal.keys()):
        parentIndexTotal = 0
        ingredientCount = 0
        for x in [i for i in total_ingredients if i.recipe.name == ingredient]:
            parentIndexTotal += x.parentIndex
            ingredientCount += 1

        distance = parentIndexTotal
        if ingredient == choices[0][0]:
            ingredientsTotal[ingredient].append(0)
        else:
            ingredientsTotal[ingredient].append(distance)

        table.add_row([i, ingredient.title().replace("-", " "), roundUp(ingredientsTotal[ingredient][0]), roundUp(ingredientsTotal[ingredient][1]),
                       ingredientsTotal[ingredient][2]])

    table.sortby = "distance"
    tableRows = table.rows.copy()
    tableRows.sort(key=lambda row: row[0])
    tableRows = [i[1] for i in tableRows]

    print(table)

    detailResults()


def helpMe():
    # TODO add help
    pass


def mainMenu():
    print("--------------- Welcome to Factorio Calculator! ---------------\n"
          "This program will calculate the optimum ratios of machines\n"
          "for a desired output rate of an item. Select which machines,\n"
          "fuel and research you desire and then the recipe you want to output.")
    while True:
        choice = input("1) Start \n"
                       "2) Exit \n"
                       "3) Help \n"
                       "What would you like to do? (Enter a number between 1 and 3): ")
        try:
            choice = int(choice)
        except ValueError:
            print(invalidEntry)
            continue

        match choice:
            case 1:
                chooseRate()
                displayCategories()
                chooseBuffs()

                calculateResult()
                collateResult()
                printResults()
            case 2:
                exit()
            case 3:
                helpMe()
            case _:
                print(invalidChoice + "(1-2)")
