from enum import Enum


class Category(Enum):
    SMELTING = "smelting"
    CHEMISTRY = "chemistry"
    CRAFTING_WITH_FLUID = "crafting-with-fluid"
    CRAFTING = "crafting"
    ADVANCED_CRAFTING = "advanced-crafting"
    BASIC_CRAFTING = "basic-crafting"
    CENTRIFUGING = "centrifuging"
    OIL_PROCESSING = "oil-processing"
    ROCKET_BUILDING = "rocket-building"
    BASIC_SOLID = "basic-solid"
    BASIC_FLUID = "basic-fluid"


class Item:
    def __init__(self, name: str, order: str, group: str, subgroup: str, translated_name: str):
        self.name = name
        self.order = order
        self.group = group
        self.subgroup = subgroup
        self.translated_name = translated_name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other


class Recipe(Item):
    def __init__(self, ingredients: list, products: list, energy: float, category: Category, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ingredients = ingredients
        self.products = products
        self.energy = energy
        self.category = category

    def printIngredients(self):
        print("---Ingredients---")
        for ingredient in self.ingredients:
            print(f"{ingredient.required}x {ingredient.recipe.title().replace("-", " ")}")

    def printProducts(self):
        print("---Products---")
        for product in self.products:
            print(f"{product['amount']}x {product['name'].title().replace("-", " ")}")


class Entity:
    def __init__(self, categories: list, speed: float, name: str, translated_name: str):
        self.speed = speed
        self.categories = categories
        self.name = name
        self.translated_name = translated_name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other


class Ingredient:
    def __init__(self, recipe, parent: Recipe, machines_needed=0.0, required=0.0, parentIndex=0):
        self.recipe = recipe
        self.required = required
        self.parent = parent
        self.machine = ''
        self.machines_needed = machines_needed
        self.parentIndex = parentIndex

    def chooseMachine(self, entities, buffs):
        possibilities = [i for i in entities if self.recipe.category in i.categories]

        if len(possibilities) > 1:
            self.machine = possibilities[possibilities.index([buff for buff in buffs if buff in possibilities][0])]
        else:
            self.machine = possibilities[0]

        self.machine = entities[entities.index(self.machine)]

    def calculate(self, entities, buffs, total_ingredients):
        self.chooseMachine(entities, buffs)

        # parentIngredient is the Ingredient object of the parent, located in the total_ingredients array
        # parentIngredients contains all ingredients in the parent recipe
        if type(self.parent) != Ingredient:
            counter = 1
            for ingredient in total_ingredients:
                if ingredient.required != 0:
                    counter += 1
            parentIngredient = total_ingredients[0:counter][::-1][total_ingredients[0:counter][::-1].index(self.parent)]
            parentIngredients = self.parent.ingredients
            self.parentIndex = counter
        else:
            parentIngredient = self.parent
            parentIngredients = self.parent.recipe.ingredients

        # parentNeeds is how much of the ingredient is required for the parent recipe
        # recipeOutput is how much product the ingredient's recipe will output
        if self.recipe.name == 'advanced-oil-processing' or self.recipe.name == 'uranium-processing':
            product = [i for i in parentIngredients if i in [i['name'] for i in self.recipe.products]][0]
            parentNeeds = parentIngredients[parentIngredients.index(product)].required

            index = self.recipe.products.index([i for i in self.recipe.products if i['name'] == product][0])
            recipeOutput = self.recipe.products[index]['amount']
        elif parentIngredient == self:
            parentNeeds = self.required
            recipeOutput = self.recipe.products[0]['amount']
        else:
            parentNeeds = parentIngredients[parentIngredients.index(self.recipe.name)].required
            recipeOutput = self.recipe.products[0]['amount']

        # itemsPerSecond is how much product the combo of ingredient recipe and machine choice will output
        if self.recipe.category == 'basic-solid':
            buff = [i for i in buffs if type(i) == float][0]
            energy = self.recipe.energy / (1 + buff)
            itemsPerSecond = (energy / self.machine.speed) / recipeOutput
        else:
            itemsPerSecond = (self.recipe.energy / self.machine.speed) / recipeOutput

        # parentRequired is how much of the parent recipe is required
        parentRequired = parentIngredient.required
        parentRecipeOutput = parentIngredient.recipe.products[0]['amount']

        if parentIngredient == self:
            self.required = parentNeeds
        elif recipeOutput == 2 or self.recipe.category == 'chemistry' or self.recipe.category == 'oil-processing':
            self.required = parentNeeds * (parentRequired / parentRecipeOutput)
        elif self.recipe.name == 'water':
            self.required = parentIngredient.machines_needed * (parentIngredients[parentIngredients.index('water')].required / parentIngredient.recipe.energy)
        else:
            self.required = (parentNeeds / recipeOutput) * (parentRequired / parentRecipeOutput)

        self.machines_needed = self.required * itemsPerSecond

    def __str__(self):
        return f"{self.recipe.translated_name} x {self.required} ({self.machine} x {self.machines_needed})"

    def __eq__(self, other):
        if type(self.recipe) == Recipe:
            return self.recipe.name == other
        else:
            return self.recipe == other

