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
    def __init__(self, ingredients: list, products: list, energy: float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ingredients = ingredients
        self.products = products
        self.energy = energy

    def printIngredients(self):
        print("---Ingredients---")
        for ingredient in self.ingredients:
            print(f"{ingredient['amount']}x {ingredient['name'].title().replace("-", " ")}")

    def printProducts(self):
        print("---Products---")
        for product in self.products:
            print(f"{product['amount']}x {product['name'].title().replace("-", " ")}")


class Entity(Item):
    def __init__(self, crafting_categories: list, crafting_speed: float, manufacturing_type: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crafting_speed = crafting_speed
        self.manufacturing_type = manufacturing_type
        self.crafting_categories = crafting_categories
