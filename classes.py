from enum import Enum


# from functions import entities, buffs


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
            print(f"{ingredient.amount}x {ingredient.recipe.title().replace("-", " ")}")

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
    def __init__(self, recipe, amount: float, parent: Recipe, machines_needed=0.0):
        self.recipe = recipe
        self.amount = amount
        self.parent = parent
        self.machine = ''
        self.machines_needed = machines_needed

    def chooseMachine(self, entities, buffs):
        if self.recipe.category == "basic-fluid":
            self.machine = "N/A"
            return

        if type(self.recipe) == Recipe:
            possibilities = [i for i in entities if self.recipe.category in i.categories]
        else:
            possibilities = [i for i in entities if "basic-solid" in i.categories]  # TODO NOT SMELTING, MINING

        if buffs in possibilities:
            self.machine = possibilities[possibilities.index([buff for buff in buffs if buff in possibilities][0])]
            self.machine = entities[entities.index(self.machine)]
        else:
            self.machine = possibilities[0]
            self.machine = entities[entities.index(self.machine)]

    def calculate(self, entities, buffs):
        self.chooseMachine(entities, buffs)
        if self.recipe.category == "basic-fluid":
            self.machines_needed = 0
        else:
            self.machines_needed = self.amount * (self.recipe.energy / self.machine.speed)

    def __str__(self):
        return f"{self.recipe.translated_name} x {self.amount} ({self.machine} x {self.machines_needed})"
