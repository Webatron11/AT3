from functions import ingest, choices, buffs, calculate, total_ingredients, entities, chooseBuffs, displayCategories, \
    recipes, Ingredient

ingest()
# displayCategories()
# chooseBuffs()

buffs = ['assembling-machine-2', 'coal', 'electric-furnace', 'electric-mining-drill', 0.3]
choices = [recipes[recipes.index('spidertron')]]

for choice in choices:
    total_ingredients.append(Ingredient(recipe=choice, required=2, parent=choice))
    calculate(choice)

for ingredient in total_ingredients:
    ingredient.calculate(entities, buffs, total_ingredients)
    print(ingredient)

print("test")
