"""
Use this to add recipes from a JSON file into the database (mySQL)

DB Structure:
    :table tblRecipes (PRIMARY KEY: RecipeID)
	    RecipeID    INTEGER NOT NULL UNIQUE
	    Title       TEXT NOT NULL
	    Image       TEXT

    :table tblIngredients (PRIMARY KEY: IngredientID)
	    IngredientID	INTEGER NOT NULL UNIQUE
	    IngredientName  TEXT NOT NULL UNIQUE

    :table tblMeasurements (PRIMARY KEY: MeasurementID)
	    MeasurementID	INTEGER NOT NULL UNIQUE
	    Measurement 	TEXT NOT NULL UNIQUE
	    Abbreviation	TEXT UNIQUE

    :table tblRecipeIngredients (PRIMARY KEY: id
	    FOREIGN KEY: RecipeID => REFERENCES tblRecipes RecipeID
	    FOREIGN KEY: MeasurementID => REFERENCES tblMeasurements MeasurementID
	    FOREIGN KEY: IngredientID => REFERENCES tblIngredients IngredientID)
        id              INTEGER NOT NULL UNIQUE
	    RecipeID        INTEGER NOT NULL
	    Amount          NUMERIC NOT NULL
	    MeasurementID   INTEGER NOT NULL
	    IngredientID    INTEGER NOT NULL

    :table tblRecipeSteps (PRIMARY KEY: id
	    FOREIGN KEY: RecipeID => REFERENCES tblRecipes RecipeID
	    id          INTEGER NOT NULL UNIQUE
	    RecipeID    INTEGER NOT NULL
	    StepNumber  INTEGER NOT NULL
	    StepText    TEXT NOT NULL

JSON Structure:
    See recipe-sample.json
"""
from re import L
import sqlite3
import json
import sys
from random import randint

# Ensure that the database variable has the correct name for the database
database = 'recipes.db'
jsonfile = 'recipes.json'
connection = sqlite3.connect(database)

def add_recipe(recipe = None):
    """
    Add a recipe to the database

    :param recipe in JSON format (mandatory)

    :return the ID of the recipe that was added
    """
    success = False
    RecipeID = 0
    ingredientid = 0
    measurmentid = 0

    if (not recipe):
        print('ERROR: No recipe provided!')
        return((success, RecipeID))
    
    try:
        # populate tblRecipes
        command = """INSERT INTO tblRecipes (title, image) VALUES (?, ?)"""
        image = recipe['image'] if 'image' in recipe else ''
        cursor = connection.execute(command, (recipe['title'], image))
        RecipeID = cursor.lastrowid

        #pupulate the tblRecipeSteps
        command = """INSERT INTO tblRecipeSteps (RecipeID, StepNumber, StepText) VALUES (?, ?, ?)"""
        for step in recipe['steps']:
            cursor = connection.execute(command, (RecipeID, step, recipe['steps'][f'{step}']))
        
        # populate tblRecipeIngredients
        for i in recipe['ingredients']:
            ingredientid = getingredientid(i['ingredient'])
            if ingredientid == 0:
                ingredientid = addingredient(i['ingredient'])

            # Look for the Measurement, if it is not there we add it
            if 'measure' in i:
                measurmentid = getmeasurementid(i['measure'])
                if measurmentid == 0:
                    # We need to add the measurement to the table
                    measurmentid = addmeasurement(i['measure'])
            
            insertrecipeingredient(RecipeID, i['quantity'], measurmentid, ingredientid)
            measurmentid = ''
            ingredientid = ''

        # Commit all changes
        connection.commit()
    except Exception as e:
        print(f'ERROR: Failed to add {recipe} due to error: {str(e)}')

    return(success, RecipeID)

def addmeasurement(measure = None, abbreviation = None):
    """
    Add a measurement to the measurements table

    :param measure (mandatory)
    :param abbreviation (optional)

    :retrun the ID of the measument that was added
    """
    if not measure:
        return(0)
    
    command = """INSERT INTO tblMeasurements (Measurement, Abbreviation) VALUES (?, ?)"""
    cursor = connection.execute(command, (measure, abbreviation))
    return(cursor.lastrowid)

def getmeasurementid(measure = None):
    """
    Given a measure return its id if it exists

    :param measure (mandatory)

    :retrun the ID of the measument if it exists
    """
    if not measure:
        return(0)
    
    command = """SELECT MeasurementID FROM tblMeasurements WHERE lower(Measurement) = lower(?)"""
    cursor = connection.execute(command, (measure,)).fetchone()
    return(cursor[0] if cursor else 0)

def insertrecipeingredient(recipeid = None, amount = None, measureid = None, ingredientid = None):
    """
    Add an ingredient to the recipe ingredients table

    :param recipeid (mandatory)
    :param amount (optional)
    :param measureid (optional)
    :param ingredientid (mandatory)

    :retrun the ID of the recipe ingredient that was added
    """

    if (not recipeid) or (not ingredientid):
        return(0)

    command = """INSERT INTO tblRecipeIngredients (RecipeID, Amount, MeasurementID, IngredientID) VALUES (?, ?, ?, ?)"""
    cursor = connection.execute(command, (recipeid, amount, measureid, ingredientid))
    return(cursor.lastrowid)

def addingredient(ingredient = None):
    """
    Add an ingredient to the ingredients table

    :param ingredient (mandatory)

    :retrun the ID of the ingredient that was added
    """
    if not ingredient:
        return(0)
    
    command = """INSERT INTO tblIngredients (IngredientName) VALUES (?)"""
    cursor = connection.execute(command, (ingredient,))
    return(cursor.lastrowid)

def getingredientid(ingredient = None):
    """
    Given an ingredient return its id if it exists

    :param ingredient (mandatory)

    :retrun the ID of the ingredient if it exists
    """
    if not ingredient:
        return(0)
    
    command = """SELECT IngredientID FROM tblIngredients WHERE lower(IngredientName) = lower(?)"""
    cursor = connection.execute(command, (ingredient,)).fetchone()
    return (cursor[0] if cursor else 0)

def addrecipes(filename = None):
    """
    Given a JSON file containing a recipes add them to the database

    :param filename of containing recipes in JSON format (mandatory)

    :retrun the total number of recipes added
    """
    if not filename:
        print('ERROR: No filename to read recipes from was provided.')
        return(0)

    with open(filename, 'r', encoding='utf-8') as recipes:
        data = json.load(recipes)
        total_recipes = len(data)
        for x in range(total_recipes):
            print(f'Processing: {data[x]["title"]}')
            recipe_exists = searchrecipebyname(data[x]["title"])
            if (recipe_exists == 0):
                add_recipe(data[x])
    return(total_recipes)

def searchrecipebyname(recipe = None):
    """
    Given a recipe name return its id if it exists

    :param recipe (mandatory)

    :retrun the ID of the recipe if it exists
    """
    if not recipe:
        print('ERROR: No recipe to search for provided')
        return(0)

    command = """SELECT RecipeID from tblRecipes where lower(Title) = lower(?)"""
    cursor = connection.cursor()
    recipeid = cursor.execute(command, (recipe,)).fetchone()
    return(recipeid[0] if recipeid else 0)

def getrecipescount():
    """
    Return the total count of recipes in the database

    :retrun the total number of recipes in the database
    """
    tRecipes = 0
    command = """SELECT COUNT(RecipeID) as tRecipes from tblRecipes"""
    cursor = connection.cursor()
    tRecipes = cursor.execute(command).fetchone()[0]
    return tRecipes

def main() -> int:
    addrecipes(jsonfile)
    connection.close()

if __name__ == '__main__':
    sys.exit(main())
