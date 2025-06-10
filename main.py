from functions import ingest, recipes, calculate, total_ingredients, entities

ingest()
# displayCategories()
# chooseBuffs()

buffs = ['assembling-machine-2', 'coal', 'electric-furnace', 'electric-mining-drill', 0.0]
choices = [recipes[recipes.index('transport-belt')]]

for choice in choices:
    calculate(choice)

for ingredient in total_ingredients:
    ingredient.calculate(entities, buffs)
    print(ingredient)

print("test")
