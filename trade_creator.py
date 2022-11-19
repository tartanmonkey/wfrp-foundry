from tkinter import messagebox
import json
from random import randint, choice
from utilities import *
from math import floor

name_data = {}  # string : [list]
vessel_data = []  # list of dictionaries
goods_data = []  # list of dictionaries (trade_good: str, chance: int, value:{spring: float, summer: float, autumn: float, # winter: float}
destination_data = []  # list of dictionaries {chance: tuple, destination: str}
origin_data = []  # list of dictionaries {chance: tuple, origin: str}
captain_data = [] # list of dictionaries, currently could be a list as only contains { captain_says: str}


def init_trade_data():
    init_name_data()
    init_vessel_data()
    init_cargo_data()
    init_captain_data()
    init_destination_data()


def init_vessel_data():
    global vessel_data
    try:
        with open("Data/Trade/Digital_Trade_Data_Vessel.json", "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Missing Digital_Trade_Data_Vessel.json!")
    else:
        chance_low = 0
        for entry in data:
            chance_high = chance_low + entry['Chance']
            chance = (chance_low, chance_high)
            chance_low = chance_high
            careers = entry["Captain"].split(',')
            careers = [c.strip() for c in careers]
            vessel_entry = {
                "vessel_type": entry["Vessel"],
                "has_name": convert_to_bool(entry["Has Name"]),
                "chance": chance,
                "crew": entry["Num Crew"],
                "max_passengers": entry["Num Passengers"],
                "cargo_chance": entry["Cargo Chance"],
                "passenger_chance": entry["Passenger Chance"],
                "cargo_capacity": entry["Capacity"],
                "captain_career": careers,
                "captain_level": entry["Captain Level"]
            }
            vessel_data.append(vessel_entry)
    # for n in vessel_data:
    #     print(n)


def init_cargo_data():
    global goods_data
    try:
        with open("Data/Trade/Digital_Trade_Data_Trade_Goods.json", "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Digital_Trade_Data_Trade_Goods.json!")
    else:
        chance_low = 0
        for entry in data:
            chance_high = chance_low + entry['Chance']
            chance = (chance_low, chance_high)
            chance_low = chance_high
            trade_entry = {
                "trade_good": entry["Goods"],
                "chance": chance,
                "value": {"spring": get_json_int(entry["Spring"], 0),
                          "summer": get_json_int(entry["Summer"], 0),
                          "autumn": get_json_int(entry["Autumn"], 0),
                          "winter": get_json_int(entry["Winter"], 0)}
            }
            goods_data.append(trade_entry)
    # for n in goods_data:
    #     print(n)


def init_destination_data():
    global destination_data, origin_data
    try:
        with open("Data/Trade/Digital_Trade_Data_Destination.json", "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Digital_Trade_Data_Destination.json!")
    else:
        global destination_data, origin_data
        for entry in data:
            destination_data.append({"chance": entry["Chance_D"], "destination": entry["Destination"]})
            if type(entry["Chance_O"]) is not str:
                origin_data.append({"chance": entry["Chance_O"], "origin": entry["Origin"]})

        destination_data = replace_chance_with_tuple(destination_data, "chance")
        origin_data = replace_chance_with_tuple(origin_data, "chance")

    # for n in destination_data:
    #     print(n)
    # print("Origin data-------------------")
    # for n in origin_data:
    #     print(n)


def init_captain_data():
    global captain_data
    try:
        with open("Data/Trade/Digital_Trade_Data_Captain.json", "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Digital_Trade_Data_Captain.json!")
    else:
        for entry in data:
            captain_data.append({"captain_says": entry["Captain Says"]})

    # for n in captain_data:
    #     print(n["captain_says"])


def init_name_data():
    try:
        with open("Data/Trade/Digital_Trade_Data_Vessel_Name.json", "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Digital_Trade_Data_Vessel_Name.json!")
    else:
        for entry in data:
            for key, value in entry.items():
                if key in name_data:
                    if len(value) > 0:
                        name_data[key].append(value)
                else:
                    name_data[key] = [value]


def get_vessel_name():
    # get random Name Structure from name_data
    name_format = name_data["Name Structure"][randint(0, len(name_data["Name Structure"]) - 1)]
    name_created = False
    # while structure contains '[' call replace_key_in_string
    while not name_created:
        if "[" in name_format:
            key = get_key_from_string(name_format)
            substitute = get_random_from_keyed_lists(key, name_data)
            name_format = name_format.replace(f"[{key}]", substitute)
        else:
            name_created = True

    return name_format


def get_origin():
    # TODO pass in race and use
    origin = get_random_chance_entry(origin_data, "chance")["origin"]
    if origin == "[Destination]":
        origin = get_random_chance_entry(destination_data, "chance")["destination"]
    return origin


def get_captain_data(key):
    data = get_random_key_value(key, captain_data)
    print(data)
    if "[" in data and "/" in data:
        choices = get_key_from_string(data, "[", "]")
        print(f"should get random detail from: {choices}")
        data = data.split("[")
        data = f"{data[0]} {get_random_item(choices, '/')}"
        return data
    return data

def get_cargo(vessel):
    cargo = []
    if roll_under(vessel["cargo_chance"]):
        cargo_amount = [randint(2, 10)]
        if cargo_amount[0] > 6:
            cargo_amount.append(randint(1, cargo_amount[0] - 1))
            cargo_amount[0] = cargo_amount[0] - cargo_amount[1]
        for n in range(len(cargo_amount)):
            # TODO implement actual amount using capacity and include in string entry
            amount = floor((cargo_amount[n] / 10) * vessel["cargo_capacity"])
            goods = get_random_chance_entry(goods_data, "chance")["trade_good"]
            cargo.append(f"{goods} ({amount})")
    return cargo


def get_passenger_numbers(vessel):
    passenger_numbers = []
    if roll_under(vessel["passenger_chance"]):
        passenger_numbers = [randint(1, vessel["max_passengers"])]
        if passenger_numbers[0] > 2:
            passenger_numbers.append(randint(1, passenger_numbers[0] - 2))
            passenger_numbers[0] = passenger_numbers[0] - passenger_numbers[1]
    return passenger_numbers


def is_valid_vessel_type(vessel_type):
    if len(vessel_type) > 0:
        valid_types = ""
        for entry in vessel_data:
            valid_types += entry["vessel_type"] + ", "
            if entry["vessel_type"] == vessel_type:
                return True
        messagebox.showinfo(title="Oops!", message=f"Invalid Vessel Type! valid types = {valid_types}")
    return False


def get_vessel_type(vessel_type):
    for entry in vessel_data:
        if entry["vessel_type"] == vessel_type:
            return entry
# ---------------------------- VESSEL CLASS------------------------------------------------------------- #


class Vessel:
    def __init__(self, vessel_type=""):
        # TODO get specific vessel if provided
        if len(vessel_type) > 0:
            vessel = get_vessel_type(vessel_type)
        else:
            vessel = get_random_chance_entry(vessel_data, "chance")
        self.vessel_type = vessel["vessel_type"]
        self.name = ""
        if vessel["has_name"]:
            self.name = get_vessel_name()
        self.num_crew = vessel["crew"]
        self.passengers = []  # set from main by calling class set function
        self.cargo = get_cargo(vessel)
        self.destination = get_random_chance_entry(destination_data, "chance")["destination"]
        # TODO implement Captain data < this is temp, maybe better way of doing? get_captain_data?

    def get_vessel_data(self):
        for entry in vessel_data:
            if entry["vessel_type"] == self.vessel_type:
                return entry
        messagebox.showinfo(title="Oops!", message=f"Failed to find {self.vessel_type} in vessel_data")

    def set_passengers(self, passengers):
        self.passengers = passengers

    def get_output(self):
        output = f"{self.vessel_type}, {self.name}\nDestination: {self.destination}"
        if len(self.cargo) > 0:
            output += f"\nCargo: {convert_list_to_string(self.cargo)}"
        if len(self.passengers) > 0:
            output += f"\nPassengers: {convert_list_to_string(self.passengers)}"
        return output

