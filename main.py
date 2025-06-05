from functions import ingest, recipes, calculate

ingest()
# displayCategories()
# chooseBuffs()

buffs = {'assembly': 'assembly-machine-2', 'fuel': 'coal', 'furnace': 'electric-furnace',
         'miner': 'electric-mining-drill', 'mining-prod': 0.0}
choices = [recipes[recipes.index('transport-belt')]]

for choice in choices:
    calculate(choice)

print("test")
