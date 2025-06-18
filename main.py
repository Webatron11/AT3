from functions import ingest, choices, buffs, calculate, total_ingredients, entities, chooseBuffs, displayCategories, \
    recipes, Ingredient

ingest()
# displayCategories()
# chooseBuffs()

buffs = ['assembling-machine-2', 'coal', 'electric-furnace', 'electric-mining-drill', 0.0]
choices = [recipes[recipes.index('chemical-science-pack')]]

for choice in choices:
    total_ingredients.append(Ingredient(recipe=choice, amount=choice.products[0]['amount'], parent=choice))
    calculate(choice)

for ingredient in total_ingredients:
    ingredient.calculate(entities, buffs)
    print(ingredient)

print("test")
