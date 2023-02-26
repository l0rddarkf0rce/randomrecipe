import sqlite3
from random import randint

# Database name in URI form, so we can open it in read only mode.
dbFile = 'file:db/recipes.db?mode=ro'

def getSecretKey():
    """
    This function generates a random key used by the application to securely sign session cookies
    """
    from os import urandom
    return urandom(12).hex()

def getrecipescount(cur):
    """
    Return the total number of recipes in the database

    :param cur : cursor to the database
    :return the total number of recipes in the database (INT)
    """
    tRecipes = 0
    command = """SELECT COUNT(RecipeID) as tRecipes from tblRecipes"""
    tRecipes = cur.execute(command).fetchone()[0]
    return tRecipes

def genrandom(cur):
    """
    Generate a random recipe ID from the database

    :param cur : cursonr to the database
    :return the id of a random recipe
    """
    command = """SELECT RecipeID from tblRecipes where RecipeID = (?)"""
    recipeid = cur.execute(command, (randint(1,getrecipescount(cur)),)).fetchone()
    return recipeid[0]

def getrandomrecipe():
    """
    Get a random recipe from the database. We first select a random number between 1 and the total number of recipes, then we
    retreive all of the ingredients, procedure, and image (if available).

    :return JSON recipe
    """
    # SQL commands needed to fetch a recipe
    command1 = """SELECT title, image from tblRecipes where RecipeID = (?)"""
    command2 = """SELECT Amount, MeasurementID, IngredientID from tblRecipeIngredients WHERE RecipeID = (?)"""
    command3 = """SELECT Measurement, Abbreviation from tblMeasurements WHERE MeasurementID = (?)"""
    command4 = """SELECT IngredientName FROM tblIngredients WHERE IngredientID = (?)"""
    command5 = """SELECT StepNumber, StepText FROM tblRecipeSteps WHERE RecipeID = (?)"""
    recipe = {}
    
    # Get recipe name and image
    connection = sqlite3.connect(dbFile, uri=True)
    cursor = connection.cursor()
    recipeid = genrandom(cursor)
    name = cursor.execute(command1, (recipeid,)).fetchone()

    # Initialize the recipe JSON object
    recipe["title"] = name[0]
    recipe["ingredients"] = []
    recipe["steps"] = []
    recipe["image"] = name[1] if name[1] != None else ''
    # Get all of the ingredients
    ingredients = cursor.execute(command2, (recipeid,)).fetchall()
    
    # Get recipe steps
    steps = cursor.execute(command5, (recipeid,)).fetchall()

    # Process ingredients and add them to the JSON object
    for ingredient in ingredients:
        # Get meassurement for the ingredient
        m = cursor.execute(command3, (ingredient[1],)).fetchone()
        # Get the ingredient name
        n = cursor.execute(command4, (ingredient[2],)).fetchone()
        if hasattr(m, '__getitem__'):
            if m[1] == 'None' or m[0] == 'none':
                recipe["ingredients"].append(f'{ingredient[0]} {n[0]}')
            else:
                recipe["ingredients"].append(f'{ingredient[0]} {m[0]} {n[0]}')
        else:
            recipe["ingredients"].append(f'{ingredient[0]} {n[0]}')
        m = ''
        n = ''
    
    # Process all steps for the recipe and add them to the JSON object
    for step in steps:
        recipe["steps"].append(f'{step[0]:2}. {step[1]}')

    return(recipe)