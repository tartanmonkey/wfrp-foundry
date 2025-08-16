import json
import math
import pandas
import random

import utilities
from utilities import *

proprietor_type = [
    {"chance": (0, 90), "race": "Human", "family_chance": 40},
    {"chance": (90, 94), "race": "Halfling", "family_chance": 25},
    {"chance": (94, 98), "race": "Dwarf", "family_chance": 10},
]

inn_data = {}  # Dictionary for holding all Inn data keyed to column headings in the csv


def init_data():
    global inn_data
    try:
        data = pandas.read_csv("Data/Inn_Data.csv")
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Missing Inn_Data.csv")
    else:
        for col in data.columns:
            inn_data[col] = [item for item in data[col].tolist() if type(item) == str]
        print(f"Inn Data initialised - num entries: {len(inn_data)}")

# ---------------------------- INN CLASS ----------------------------------------


class Inn:

    def __init__(self):
        self.name = self.create_name()
        self.description = choice(inn_data["Size"])
        self.condition = choice(inn_data["State of repair"])
        self.details = choice(inn_data["Details"])
        self.proprietor_type = choice(inn_data["Proprietor"])
        self.known_for = f"{choice(inn_data['Known_for_1'])} {choice(inn_data['Known_for_2'])}"
        self.drinks = []
        self.menu = []
        self.create_drinks()
        self.create_menu()

    def create_name(self):
        name_1 = choice(inn_data["Name_1"])
        name_2 = choice(inn_data["Name_2"])
        return f"The {name_1} {name_2}"

    def create_drinks(self):
        for i in range(random.randint(1,3)):
            drink = f"{choice(inn_data['Drink_1'])} {choice(inn_data['Drink_2'])}"
            self.drinks.append(drink)

    def create_menu(self):
        # TODO actually make this be a dictionary with costs
        # TODO have specifics depend on Quality or Condition of Inn
        self.menu.append(choice(inn_data['Food_Poor']))
        self.menu.append(choice(inn_data['Food_Common']))
        self.menu.append(choice(inn_data['Food_Good']))



    def get_output(self):
        # TODO Add kwargs - see same method in character_creator
        text = self.name
        text += f"\n{self.description}, {self.condition} with {self.details}"
        text += f"\nKnown for {self.known_for}"
        text += f"\nInnkeep: {self.proprietor_type}"
        text += f"\nProduce:\n"
        for d in self.drinks:
            text += f"{d}, "
        for m in self.menu:
            text += f"\n{m}"
        return text
