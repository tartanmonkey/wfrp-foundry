import json
import math
import pandas

import utilities
from utilities import *

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
        self.name = "The New Inn"

    def get_output(self):
        # TODO Add kwargs - see same method in character_creator
        return self.name
