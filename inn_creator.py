import json
import math
import pandas
import random
import family_member

import utilities
from utilities import *
from family_member import FamilyMember

proprietor_type = [
    {"chance": (0, 90), "race": "Human", "family_chance": 50},
    {"chance": (90, 94), "race": "Halfling", "family_chance": 25},
    {"chance": (94, 98), "race": "Dwarf", "family_chance": 10},
]

food_type_cost = {
    "Food_Dessert": 5,
    "Food_Seafood": 6,
    "Food_Poor": 3,
    "Food_Common": 4,
    "Food_Good": 6,
    "Food_Best": 8
}

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
        self.cost_mods = {"All": -0.5, "Food": 1.0, "Drink": 2.1, "Rooms": 1.0}
        self.description = self.get_text(inn_data["Size"])
        self.condition = self.get_text(inn_data["State of repair"])
        self.details = self.get_text(inn_data["Details"])
        # TODO remove proprietor_type from here and the csv data
        self.proprietor_type = choice(inn_data["Proprietor"])
        self.proprietor = None
        # TODO known_for probs needs own method to deal with tags
        self.known_for = f"{choice(inn_data['Known_for_1'])} {choice(inn_data['Known_for_2'])}"
        self.drinks = []
        self.menu = []
        self.create_drinks()
        self.create_menu()

    def create_name(self):
        name_1 = choice(inn_data["Name_1"])
        name_2 = choice(inn_data["Name_2"])
        return f"The {name_1} {name_2}"

    def get_text(self, text_list):
        return choice(text_list)

    def create_drinks(self):
        # gets price from string and modifies if needed
        for i in range(random.randint(1,3)):
            drink_type = choice(inn_data['Drink_2'])
            cost = utilities.get_key_from_string(drink_type)
            to_remove = f"[{cost}]"
            cost = self.get_cost("Drink", cost)
            to_add = f"({cost})"
            type_with_price = drink_type.replace(to_remove, to_add)
            drink_adjective = choice(inn_data['Drink_1'])
            drink = f"{drink_adjective} {type_with_price}"
            self.drinks.append(drink)

    def create_menu(self):
        # TODO actually make this be a dictionary with costs
        # TODO have specifics depend on Quality or Condition of Inn

        self.menu.append(self.get_food_item('Food_Poor'))
        self.menu.append(self.get_food_item('Food_Common'))
        self.menu.append(self.get_food_item('Food_Good'))

    def get_food_item(self, food_type):
        food = choice(inn_data[food_type])
        cost = self.get_cost("Food", food_type_cost[food_type])
        return f"{food} ({cost})"

    def get_cost(self, goods, cost):
        cost_value = int(cost)  # in case this is a string
        goods_type = goods
        if "Food" in goods:
            goods_type = "Food"
        print("Got Food Type: " + goods_type)
        multiplier = self.cost_mods["All"] + self.cost_mods[goods_type]
        cost_value = round(cost_value * multiplier)
        return cost_value

    def set_proprietor(self, innkeep):
        self.proprietor = innkeep

    def get_output(self):
        # TODO Add kwargs - see same method in character_creator
        text = self.name
        text += f"\n{self.description}, {self.condition} with {self.details}"
        text += f"\nKnown for {self.known_for}"
        text += f"\nInnkeep: {self.proprietor.get_one_line_details(True)}"
        if self.proprietor.has_family():
            text += self.get_family_output()
        text += f"\nProduce:\n"
        for d in self.drinks:
            text += f"{d}, "
        for m in self.menu:
            text += f"\n{m}"
        return text

    def get_family_output(self):
        text = f"\nFamily: "
        added_child = False
        for n in range(0, len(self.proprietor.family)):
            if self.proprietor.family[n].relationship == "Child":
                if added_child:
                    text += f", {self.proprietor.family[n].get_output()}"
                else:
                    text += f"\nChildren: {self.proprietor.family[n].get_output()}"
                    added_child = True
            else:
                text += f"{self.proprietor.family[n].get_output()}"
        return text
