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


# This class is used to represent an Item. This is not a recipe, just the item itself. Used to correctly set groups for recipes.
class Item:
    def __init__(self, name: str, order: str, group: str, subgroup: str, translated_name: str):
        self.name = name
        self.order = order
        self.group = group
        self.subgroup = subgroup
        self.translated_name = translated_name

    # When cast into a string, will return its name. This lets you print an Item without any further code.
    def __str__(self):
        return self.name

    # When comparing an Item to another item, compare its name, not the whole object. Lets you compare an Item to a string, pretty much.
    def __eq__(self, other):
        return self.name == other

# Contains a Recipe. Inherits from item. It has two functions to output its ingredients and its products.
class Recipe(Item):
    def __init__(self, ingredients: list, products: list, energy: float, category: Category, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ingredients = ingredients
        self.products = products
        self.energy = energy
        self.category = category

    # Loops through all ingredients in the recipe and prints them in a certain format.
    def printIngredients(self):
        print("--- Ingredients ---")
        for ingredient in self.ingredients:
            print(f"{ingredient.required}x {ingredient.recipe.title().replace("-", " ")}")

    # Loops through all products in the recipe and prints them in a certain format.
    def printProducts(self):
        print("---- Products ----")
        for product in self.products:
            print(f"{product['amount']}x {product['name'].title().replace("-", " ")}")


# Contains an Entity (Mining drill, assembling machine, etc.)
class Entity:
    def __init__(self, categories: list, speed: float, name: str, translated_name: str):
        self.speed = speed
        self.categories = categories
        self.name = name
        self.translated_name = translated_name

    # When cast into a string, will return its name. This lets you print an entity without any further code.
    def __str__(self):
        return self.name

    # When comparing an Entity to another item, compare its name, not the whole object. Lets you compare an entity to a string, pretty much.
    def __eq__(self, other):
        return self.name == other

# The main class used in the program. Relates a recipe to a parent as well as how much of this recipe is required for the parent.
# It also contains the number of machines required to produce this Ingredient.
class Ingredient:
    def __init__(self, recipe, parent: Recipe, machines_needed=0.0, required=0.0, parentIndex=0):
        self.recipe = recipe
        self.required = required
        self.parent = parent
        self.machine = ''
        self.machines_needed = machines_needed
        self.parentIndex = parentIndex

    # Assigns the Ingredient an Entity to produce it.
    def chooseMachine(self, entities, buffs):
        # Looks at all entities and checks if they can produce the category of recipe for the ingredient. Outputs an array.
        possibilities = [i for i in entities if self.recipe.category in i.categories]

        # Ensure there is a possibility
        if len(possibilities) > 1:
            # Returns the preferred machine from the buffs array if the preferred machine is in possibilities
            buff = [buff for buff in buffs if buff in possibilities]
            # If the buff array exists
            if len(buff) > 0:
                # Assign the possibility to the ingredient's machine variable
                self.machine = possibilities[possibilities.index(buff[0])]
            else:
                # Otherwise, just assign the first possibility
                self.machine = possibilities[0]
        else:
            # If there isn't a preferred machine, just assign the first possibility.
            self.machine = possibilities[0]

        # Assign the actual Entity object, not just the name of the Entity.
        self.machine = entities[entities.index(self.machine)]

    # The heavy lifting of the program. Calculates the number of required machines, and required items, as per the parent
    def calculate(self, entities, buffs, total_ingredients, rate):
        # TODO oil stuff doesn't work still - idk why

        # Makes sure there has been a machine assigned for the ingredient
        self.chooseMachine(entities, buffs)

        # parentIngredient is the Ingredient object of the parent, located in the total_ingredients array
        # parentIngredients contains all ingredients in the parent recipe

        # Checks if the parent is an Ingredient object
        if type(self.parent) != Ingredient:
            # Looks from the back of the total_ingredients array for the last calculated ingredient.
            counter = 1
            for ingredient in total_ingredients:
                if ingredient.required != 0:
                    counter += 1

            # From this sliced total_ingredients, find the ingredient's parent. Checks from the bottom of the array for the last occurance, not the first.
            parentIngredient = total_ingredients[0:counter][::-1][total_ingredients[0:counter][::-1].index(self.parent)]
            parentIngredients = self.parent.ingredients
            # Assigns the index of the parent for later reference.
            self.parentIndex = counter
        else:
            parentIngredient = self.parent
            parentIngredients = self.parent.recipe.ingredients

        # parentNeeds is how much of the ingredient is required for the parent recipe
        # recipeOutput is how much product the ingredient's recipe will output

        # Checks for special cases such as oil or uranium processing, solid-fuel and if the item has itself as a parent.
        if self.recipe.name == 'advanced-oil-processing' or self.recipe.name == 'uranium-processing':
            # Finds the correct product from advanced-oil-processing or uranium-processing depending on the required ingredient for the current recipe.
            product = [i for i in parentIngredients if i in [i['name'] for i in self.recipe.products]][0]

            # Assigns the parentNeeds variable from the amount of the product needed by the parent
            parentNeeds = parentIngredients[parentIngredients.index(product)].required

            # Finds the index of the product and uses it to assign the recipe's output.
            index = self.recipe.products.index([i for i in self.recipe.products if i['name'] == product][0])
            recipeOutput = self.recipe.products[index]['amount']
        elif parentIngredient == self:
            parentNeeds = self.required
            recipeOutput = self.recipe.products[0]['amount']
        elif "solid-fuel" in self.recipe.name:
            # Similar to the advanced-oil-processing section, but hardcoded
            parentNeeds = parentIngredients[parentIngredients.index("solid-fuel")].required
            recipeOutput = self.recipe.products[0]['amount']
        else:
            # Normal case
            # Sets parentNeeds based off how much of the recipe the parent needs.
            parentNeeds = parentIngredients[parentIngredients.index(self.recipe.name)].required
            recipeOutput = self.recipe.products[0]['amount']

        # itemsPerSecond is how much product the combo of ingredient recipe and machine choice will output
        # Only use buff if the recipe category is basic solid
        if self.recipe.category == 'basic-solid':
            # Filters buffs to find the mining buff
            buff = [i for i in buffs if type(i) == float][0]
            # Calculates energy using the buff
            energy = self.recipe.energy / (1 + buff)
            # Sets itemsPerSecond with rate in mind.
            itemsPerSecond = (energy / self.machine.speed) / recipeOutput / rate
        else:
            # Otherwise, just do the normal calculation.
            itemsPerSecond = (self.recipe.energy / self.machine.speed) / recipeOutput / rate

        # parentRequired is how much of the parent recipe is required
        parentRequired = parentIngredient.required
        parentRecipeOutput = parentIngredient.recipe.products[0]['amount']

        # Account for edge cases
        if parentIngredient == self:
            # If parent is self, just assign self.required to what the parent needs.
            self.required = parentNeeds
        elif recipeOutput == 2 or self.recipe.category == 'chemistry' or self.recipe.category == 'oil-processing':
            # If the recipe outputs 2+ products, do this.
            self.required = parentNeeds * (parentRequired / parentRecipeOutput)
        elif self.recipe.name == 'water':
            # Water is weird. Hardcoded case.
            self.required = parentIngredient.machines_needed * (parentIngredients[parentIngredients.index('water')].required / parentIngredient.recipe.energy)
        else:
            # Otherwise, just do this
            self.required = (parentNeeds / recipeOutput) * (parentRequired / parentRecipeOutput)

        self.machines_needed = self.required * itemsPerSecond

    def __str__(self):
        return f"{self.recipe.translated_name} x {self.required} ({self.machine} x {self.machines_needed})"

    def __eq__(self, other):
        if type(self.recipe) == Recipe:
            return self.recipe.name == other
        else:
            return self.recipe == other
