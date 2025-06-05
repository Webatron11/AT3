from functions import ingest, displayCategories, chooseBuffs, choices, buffs, recipes, items, fluids
from classes import Recipe

ingest()
# displayCategories()
# chooseBuffs()

buffs = {'assembly': 'assembly-machine-2', 'fuel': 'coal', 'furnace': 'electric-furnace', 'miner': 'electric-mining-drill', 'mining-prod': 0.0}
choices = [recipes[recipes.index('transport-belt')]]

total_ingredients = []

def calculate(recipe: Recipe):
    for ingredient in recipe.ingredients:
        if ingredient['type'] == 'fluid':
            total_ingredients.append(fluids[fluids.index(ingredient['name'])])
            continue
        if items[items.index(ingredient['name'])].subgroup != "raw-resource":
            total_ingredients.append(recipes[recipes.index(ingredient['name'])])
            calculate(recipes[recipes.index(ingredient['name'])])
        else:
            total_ingredients.append(items[items.index(ingredient['name'])])

for choice in choices:
    calculate(choice)

print("test")
