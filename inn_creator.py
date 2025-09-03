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
    {"chance": (94, 100), "race": "Dwarf", "family_chance": 10},
]

food_type_cost = {
    "Food_Dessert": 8,
    "Food_Seafood": 12,
    "Food_Poor": 6,
    "Food_Common": 10,
    "Food_Good": 14,
    "Food_Best": 18
}

room_cost = {"Common": 10, "Private": 120}

food_type_available = {
    "Cheap": {"Food_Common": (0, 2), "Food_Poor": (2, 3)},
    "Average": {"Food_Good": (0, 1), "Food_Common": (1, 3), "Food_Poor": (1, 1)},
    "Expensive": {"Food_Best": (0, 1), "Food_Good": (2, 3), "Food_Common": (1, 1)}
}

known_for_sets = [
    [0], [1], [2], [1, 2], [1, 2], [1, 1, 2], [1, 2, 2]
]

clientele_group = [
    {"chance": (0, 10), "group": "pilgrims"},
    {"chance": (10, 30), "group": "family"},
    {"chance": (30, 60), "group": "travellers group"},
    {"chance": (60, 100), "group": "merchant caravan"},
    {"chance": (90, 100), "group": "road warden patrol", "no_duplicates": True},
]

clientele_sets = {
    "Quiet": {"coach": (0, 0), "clientele_group": (0, 1), "travellers": (1, 1)},
    "Middling": {"coach": (1, 1), "clientele_group": (0, 1), "travellers": (1, 2)},
    "Busy": {"coach": (1, 2), "clientele_group": (1, 1), "travellers": (1, 2)}
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


def get_cost_mod(cost):
    if cost == "Expensive":
        return 0.25
    if cost == "Cheap":
        return -0.25
    else:
        print(f"WARNING: got unhandled cos mod: {cost}")
        return 0


def create_quality_from_cost_mods(cost_mods):
    value = 0
    quality = "Average"
    for k in cost_mods:
        value += cost_mods[k]
    if value > 3:
        quality = "Expensive"
    elif value < 3:
        quality = "Cheap"
    print(f"TOTAL VALUE: {value} - QUALITY: {quality}")
    return quality


def get_coach_type(quality):
    if quality == "Cheap":
        return "coach"
    coach_type = choice(["coach", "coach", "coach noble"])
    return coach_type

def get_coach_output(coach_group, clientele_traits, clientele_stats):
    text = ""
    subtitle = "- Passengers -"
    for member in coach_group:
        if member.career != "Coachman" and subtitle == "- Passengers -":
            text += f"\n{subtitle}"
            subtitle = ""
        text += f"\n{member.get_one_line_details(clientele_traits)}"
        if clientele_stats:
                text += f"\n{member.get_one_line_stats()}\n"
    return text

# ---------------------------- INN CLASS ----------------------------------------


class Inn:

    def __init__(self, quality, occupied):
        self.name = self.create_name()
        self.tags = []
        self.cost_mods = {"All": 0.0, "Food": 1.0, "Drink": 1.0, "Rooms": 1.0}
        self.quality = quality
        self.description = self.get_text(inn_data["Size"], True)
        self.condition = self.get_text(inn_data["State of repair"], True)
        self.details = self.get_text(inn_data["Details"], True, False)
        self.proprietor = None
        # TODO potentially replace with list so its easier to output nice
        self.known_for = self.get_known_for()
        self.process_tags()
        if self.quality == "random":
            self.quality = create_quality_from_cost_mods(self.cost_mods)
        self.drinks = []
        self.menu = []
        self.create_drinks()
        self.create_menu()
        self.occupied = ""  # occupied: "Quiet", "Middling", "Busy"
        if occupied == "random":
            self.occupied = choice(["Quiet", "Middling", "Middling", "Busy"])
        else:
            self.occupied = occupied
        self.clientele = []

    def create_name(self):
        name_1 = choice(inn_data["Name_1"])
        name_2 = choice(inn_data["Name_2"])
        return f"The {name_1} {name_2}"

    def get_known_for(self):
        known_for = ""
        known_for_set = choice(known_for_sets)
        track_duplicates = []
        if len(known_for_set) > 0:
            set_adj = "Known_for_1"  # TODO only this set needs to catch Tags
            set_noun = "Known_for_2"
            for s in known_for_set:
                # TODO could add logic to catch if not 1 line and last line and add 'and'
                # TODO or instead make known_for a list and handle in get_output
                if s == 2:
                    set_adj = "Known_for_3"
                    set_noun = "Known_for_4"
                noun = choice(inn_data[set_noun])
                if noun not in track_duplicates:
                    track_duplicates.append(noun)
                    adj_list = inn_data[set_adj]
                    if set_adj == "Known_for_1":
                        if self.quality != "random":
                            if self.quality == "Average":
                                adj_list = [item for item in inn_data["Known_for_1"] if "Cheap" not in item and "Expensive" not in item]
                            else:
                                adj_list = [item for item in inn_data["Known_for_1"] if self.quality in item]
                    adjective = choice(adj_list)

                    text = f"{adjective} {noun}"
                    text = self.get_text(text, False, False)
                    known_for += f"{text}, "
                else:
                    # For debug only...
                    print(f"!!!!!!!!!!! Binning duplicate Known For noun: {noun}")
        return known_for

    def get_text(self, text, is_list=True, use_quality=True):
        if is_list:
            text_list = text
            # if user input has set quality prune list to only relevant
            if use_quality:
                if self.quality != "random":
                    if self.quality != "Average":
                        text_list = [item for item in text if self.quality in item]
                    else:
                        text_list = [item for item in text if "Cheap" not in item and "Expensive" not in item]
            text = choice(text_list)
        print(text)
        if "[" in text:
            text = self.get_tags_from_string(text)
        # now handle alternatives divided by /
        elif "(" in text:
            while "(" in text:
                substring = get_key_from_string(text, "(", ")")
                if "/" in substring:
                    random_selection = get_random_item(substring, "/")
                    text = replace_text(text, f"({substring})", random_selection)
                else:
                    break
        return text

    def get_tags_from_string(self, text):
        num_tags = text.count("[")
        tag = ""
        # TODO could add a local tag list here to deal with Dessert which doesn't take an adjective
        while num_tags > 0:
            new_tag = utilities.get_key_from_string(text)
            text = utilities.replace_text(text, f"[{new_tag}]", '')
            # TODO *might* need to add a space if more than one tag
            tag += new_tag
            num_tags -= 1
        if len(tag) > 0:
            self.tags.append(tag)
        return text

    def process_tags(self):
        # Note we don't handle Dessert and just check for it in create_menu
        for tag in self.tags:
            if tag == "Expensive" or tag == "Cheap":
                self.cost_mods["All"] += get_cost_mod(tag)
            # now handle specific goods
            elif "Expensive" in tag:
                self.modify_cost_mods(tag, "Expensive")
            elif "Cheap" in tag:
                self.modify_cost_mods(tag, "Cheap")
            print(tag)

    def modify_cost_mods(self, tag_line, cost_type):
        tag_subject = utilities.replace_text(tag_line, cost_type, '')
        if tag_subject in self.cost_mods:
            self.cost_mods[tag_subject] += get_cost_mod(cost_type)
        else:
            print(f"Missing tag_subject from self.cost_mods: {tag_subject}")

    def create_drinks(self):
        # gets price from string and modifies if needed
        for i in range(random.randint(2, 3)):
            drink_type = choice(inn_data['Drink_2'])
            cost = utilities.get_key_from_string(drink_type)
            to_remove = f"[{cost}]"
            cost = self.get_cost("Drink", cost)
            to_add = f"({cost})"
            type_with_price = drink_type.replace(to_remove, to_add)
            drink_adjective = choice(inn_data['Drink_1'])
            drink = f"{drink_adjective} {type_with_price}"
            if drink not in self.drinks:
                self.drinks.append(drink)

    def create_menu(self):
        print(f"In Create Menu - Quality = {self.quality}")
        available_food = food_type_available[self.quality]
        for food_type in available_food:
            num_type = utilities.get_random_int_from_tuple(available_food[food_type])
            for n in range(num_type):
                food = self.get_food_item(food_type)
                if food not in self.menu:
                    self.menu.append(food)
                else:
                    # For Debug only
                    print(f"!!!!! Duplicate Food - binning: {food}")
        # Now Add Dessert if available
        for t in self.tags:
            if "Dessert" in t:
                print("!!!!Dessert Found!!!!")
                num_desserts = randint(1, 3)
                for d in range(num_desserts):
                    self.menu.append(self.get_food_item("Food_Dessert"))
                return

    def get_food_item(self, food_type):
        food = choice(inn_data[food_type])
        cost = self.get_cost("Food", food_type_cost[food_type])
        return f"{food} ({cost})"

    def get_cost(self, goods, cost):
        cost_value = int(cost)  # in case this is a string
        goods_type = goods
        if "Food" in goods:
            goods_type = "Food"
        # print("Got Food Type: " + goods_type)
        multiplier = self.cost_mods["All"] + self.cost_mods[goods_type]
        cost_value = round(cost_value * multiplier)
        cost_notation = utilities.get_cash_notation(cost_value)
        return cost_notation

    def set_proprietor(self, innkeep):
        self.proprietor = innkeep

    def get_clientele_groups(self):
        groups = []
        clientele_pool = clientele_sets[self.occupied]
        for group_type in clientele_pool:
            num_type = utilities.get_random_int_from_tuple(clientele_pool[group_type])
            # print(f"Group {group_type} num_type = {num_type}")
            for n in range(num_type):
                if group_type == "coach":
                    groups.append(get_coach_type(self.quality))
                elif group_type == "clientele_group":
                    # TODO now pick partic group and check for duplicates where needed
                    group_data = utilities.get_random_chance_entry(clientele_group, "chance")
                    if "no_duplicates" in group_data:
                        if group_data["group"] not in groups:
                            groups.append(group_data["group"])
                    else:
                        groups.append(group_data["group"])
                else:
                    groups.append(group_type)
        return groups

    def set_clientele(self, clientele):
        self.clientele = clientele

    def set_occupied(self, new_quantity_clientele):
        self.occupied = new_quantity_clientele

# ----------------------------------------- GET OUTPUT ----------------------------

    def get_output(self, clientele_traits, clientele_stats, show_clientele, is_wiki_output):
        # TODO Add kwargs - see same method in character_creator
        prefix = ""
        if is_wiki_output:
            prefix = "+++ "
        text = f"{prefix}{self.name}"
        text += f"\n{self.description}, {self.condition} with {self.details}"
        text += self.get_known_for_output()
        text += f"\nInnkeep: {self.proprietor.get_one_line_details(True)}"
        if self.proprietor.has_family():
            text += self.proprietor.get_family_output(clientele_traits)
        text += f"\n{self.get_rooms_output()}"
        prefix = "\n"
        if is_wiki_output:
            prefix = "++++ "
        text += f"\n{prefix}Produce:\n"
        for d in self.drinks:
            text += f"{d}, "
        for m in self.menu:
            text += f"\n{m}"
        text += self.get_clientele_output(clientele_traits, clientele_stats, show_clientele, is_wiki_output)
        return text

    def get_known_for_output(self):
        text = ""
        # TODO probably update to handle known_for as a list rather than string so we can add 'and'
        if len(self.known_for) > 0:
            text = f"\nKnown for {self.known_for}"
        return text

    def get_rooms_output(self):
        text = "Rooms:"
        for rooms in room_cost:
            text += f" {rooms} ({self.get_cost('Rooms', room_cost[rooms])}),"
        return text

    def get_clientele_output(self, clientele_traits, clientele_stats, show_clientele, is_wiki_output):
        prefix = "\n"
        if is_wiki_output:
            prefix = "++++ "
        text = f"\n{prefix}Occupied: {self.occupied}"
        if show_clientele:
            text += " - Clientele:"
            for group in self.clientele:
                goods = ""
                # add goods to title if group contains it
                if "goods" in group:
                    goods = group["goods"]
                text += f"\n\n-- {group['group_name'].capitalize()}{goods} --"
                # Handle coach separately so can split out passengers...
                if "coach" in group['group_name']:
                    text += get_coach_output(group["members"], clientele_traits, clientele_stats)
                else:
                    for member in group["members"]:
                        text += f"\n{member.get_one_line_details(clientele_traits)}"
                        if clientele_stats:
                            text += f"\n{member.get_one_line_stats()}\n"
                        if member.has_family():
                            text += member.get_family_output(clientele_traits)
        return text




