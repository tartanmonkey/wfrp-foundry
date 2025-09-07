import pandas

import utilities
from utilities import *
from random import randint, choice

# structured as a dictionary simply so can look up random elements in each mutation
mutation_data = {
    "Physical Mutation": {},
    "Beast Head": {},
    "Hit Location": {}
}


def init_mutation_data():
    global mutation_data
    # Set up physical mutations
    try:
        data = pandas.read_csv("Data/Mutations/Physical_Mutations.tsv", delimiter='\t')
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Data/Mutations/Physical_Mutations.tsv")
    else:
        for index, row in data.iterrows():
            mutation = {'Chance': row['Chance'], 'Effect': row['Effect'], 'Stats': {'BS': row['BS'], 'S': row['S'], 'T': row['T'], 'I': row['I'], 'Agi': row['Agi'], 'Dex': row['Dex'], 'Fel': row['Fel'] }}
            mutation_data["Physical Mutation"][row['Name']] = mutation
        # Test print
        # for k, v in mutation_data["Physical Mutation"].items():
        #     mutation = mutation_data["Physical Mutation"][k]
        #     print(f"{k} : {mutation['Effect']}")
    # Add beast heads
    try:
        data = pandas.read_csv("Data/Mutations/Beast_Heads.tsv", delimiter='\t')
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Data/Mutations/Beast_Heads.tsv")
    else:
        for index, row in data.iterrows():
            beast_head = {'Chance': row['Chance'], 'Effect': row['Effect']}
            mutation_data["Beast Head"][row['Name']] = beast_head
    # Add hit locations - this is overkill a simple list would probably do
    try:
        data = pandas.read_csv("Data/Hit_Locations.tsv", delimiter='\t')
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Data/Hit_Locations.tsv")
    else:
        for index, row in data.iterrows():
            hit_location = {'Chance': row['Chance']}
            mutation_data["Hit Location"][row['Name']] = hit_location


def get_detail_string(text=""):
    if isinstance(text, str):
        if len(text) == 0:
            return ""
    else:
        return ""
    if "[" in text:
        while "[" in text:
            key = get_key_from_string(text)
            substitute_text = ""
            if key in mutation_data:
                # get random entry, Name & Effect if exists
                substitute_text = choice(list(mutation_data[key].keys()))
                if "Effect" in mutation_data[key][substitute_text]:
                    substitute_text = f"{substitute_text} ({mutation_data[key][substitute_text]['Effect']})"
            text = replace_text(text, f"[{key}]", substitute_text)

    return text

# -------------------------------------- MUTATION CLASS ----------------------------------------------

class Mutation:
    def __init__(self):
        self.name = choice(list(mutation_data["Physical Mutation"].keys()))
        self.attributes = mutation_data["Physical Mutation"][self.name]["Stats"]
        self.details = get_detail_string(mutation_data["Physical Mutation"][self.name]["Effect"])

    def get_output(self):
        details = ""
        if len(self.details) > 0:
            details = f" : {self.details}"
        return f"{self.name}{details}"
