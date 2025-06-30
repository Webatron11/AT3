from json import load
from prettytable import PrettyTable

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
order = []
tableRows = []


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


def ingestEntities(craftingmachinesJson, miningdrillsJson):
    global entities

    for entity in craftingmachinesJson:
        entities.append(
            Entity(name=entity['key'], translated_name=entity['localized_name']['en'], speed=entity['crafting_speed'],
                   categories=entity['crafting_categories']))
    for entity in miningdrillsJson:
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
        print(item.name.title().replace('-', " "))


def chooseRate():
    global rate

    while True:
        choice = input("1) Items Per Second \n"
                       "2) Items Per Minute \n"
                       "3) Items Per Hour \n"
                       "Input your choice: ")
        try:
            choice = int(choice)
        except ValueError:
            print("Invalid input. Please try again.")
            continue

        if 1 >= choice >= 3:
            print("Invalid choice. Try again with a valid choice (1 or 2)")
            continue
        else:
            break

    rate = 60 ** (choice - 1)


def chooseAmount():
    global rate

    while True:
        try:
            choice = int(input("Input desired amount: "))
        except ValueError:
            print("Invalid input, please try again. Make sure you are inputting a number.")
            continue
        else:
            return choice / rate


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

    recipes[index].printProducts()
    recipes[index].printIngredients()

    while True:
        choice = input("1) Choose this recipe \n"
                       "2) Choose another recipe \n"
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
            case _:
                print("Invalid choice. Try again with a valid choice (1 or 2)")
                continue


def displayCategories():
    global groups

    for i, group in enumerate(groups):
        print(f"{i + 1}) {group.title().replace('-', " ")}")

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
        choice = input("1) Choose a recipe \n"
                       "2) Return to category menu \n"
                       "Input your choice:  ")
        try:
            choice = int(choice)
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
    assembler = [i.name for i in entities if "crafting" in i.categories]
    miner = [i.name for i in entities if "basic-solid" in i.categories]
    furnace = [i.name for i in entities if "smelting" in i.categories]

    chosenAssembler = False
    chosenMiner = False
    chosenFurnace = False

    while not (chosenAssembler and chosenMiner and chosenFurnace):
        try:
            choice = int(input("1) Assembling Machine \n"
                               "2) Miner \n"
                               "3) Furnace \n"
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
        else:
            # # Checks if the last ingredient in total_ingredients has the current ingredient in its ingredient list
            # if ingredientItem in total_ingredients[-1].recipe.ingredients:
            #     # If so, makes the last item in total_ingredients the parent, in place of the parent recipe.
            #     total_ingredients.append(Ingredient(recipe=recipes[recipes.index(ingredient.recipe)], parent=total_ingredients[-1]))
            # else:
            total_ingredients.append(Ingredient(recipe=recipes[recipes.index(ingredient.recipe)], parent=recipe))

        calculateIngredients(recipes[recipes.index(ingredient.recipe)])


def calculateResult():
    global buffs
    global choices

    buffs = ['assembling-machine-2', 'electric-mining-drill', 0.30000000000000004, 'electric-furnace']
    choices = [[recipes[recipes.index("spidertron")], 1]]

    for choice in choices:
        total_ingredients.append(Ingredient(recipe=choice[0], required=choice[1], parent=choice[0]))
        calculateIngredients(choice[0])

    for ingredient in total_ingredients:
        ingredient.calculate(entities, buffs, total_ingredients)


def collateResult():
    global ingredientsDict
    global ingredientsTotal

    ingredientsSet = set([i.recipe.name for i in total_ingredients])
    ingredientsDict = {}.fromkeys(ingredientsSet)

    for i in ingredientsSet:
        ingredientsDict[i] = []

    for key in ingredientsSet:
        for ingredient in total_ingredients:
            print(ingredient)
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

        choice = input(f"(1-{length}) Select an ingredient for more information \n"
                       f"({length + 1}) Return Home \n"
                       f"({length + 2}) Save Output \n"
                       f"Input your choice: ")

        try:
            choice = int(choice)
        except ValueError:
            print("Invalid entry, please try again. Make sure you are entering a number.")
            continue

        if 0 <= choice <= length:
            printDetails(choice)
            continue
        elif choice == 1:
            # Return home
            break
        elif choice == 2:
            # Save output
            break
        else:
            print(f"Please try again with a number between 1 and {length + 2}")
            continue


def printResults():
    global ingredientsTotal
    global ingredientsDict
    global total_ingredients
    global choices
    global tableRows

    table = PrettyTable(['Number', 'Recipe', 'Machines Needed', 'Items Needed', 'distance'])

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

        table.add_row([i, ingredient.title().replace("-", " "), round(ingredientsTotal[ingredient][1], 1), round(ingredientsTotal[ingredient][0], 1),
                       ingredientsTotal[ingredient][2]])

    table.sortby = "distance"
    tableRows = table.rows
    tableRows.sort(key=lambda row: row[0])
    tableRows = [i[1] for i in tableRows]

    print(table)

    detailResults()
