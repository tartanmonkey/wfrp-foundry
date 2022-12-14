import pandas
from random import randint, choice
from utilities import *
from tkinter import messagebox


backgrounds_data = {}  # { Background Type: { "question": str, "detail sets": { Detail Type Id: { "detail title": str, "details": List }}}}


def init_backgrounds_data():
    global backgrounds_data
    try:
        data = pandas.read_csv("Data/Character_Data_Backgrounds.csv")
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Missing Character_Data_Backgrounds.csv")
    else:
        current_type = ""
        for row in data.iterrows():
            # create initial entry if it doesn't exist
            if type(row[1]["Background Type"]) is str:
                if row[1]["Background Type"] not in backgrounds_data:
                    current_type = row[1]["Background Type"]
                    backgrounds_data[row[1]["Background Type"]] = {"question": row[1]["Question"], "detail sets": {row[1]["Detail Type Id"]: {"detail title": row[1]["Detail Title"], "details": [row[1]["Detail"]]}}}
            else:
                if row[1]["Detail Type Id"] not in backgrounds_data[current_type]["detail sets"]:
                    # create new detail set
                    backgrounds_data[current_type]["detail sets"][row[1]["Detail Type Id"]] = {"detail title": row[1]["Detail Title"], "details": [row[1]["Detail"]]}
                else:
                    # add to existing set
                    backgrounds_data[current_type]["detail sets"][row[1]["Detail Type Id"]]["details"].append(row[1]["Detail"])

        # for key, entry in backgrounds_data.items():
        #     for set_id, set_data in entry["detail sets"].items():
        #         for detail in set_data['details']:
        #             print(detail)


def get_background(**kwargs):
    text = ""
    # use args key to lookup specific instructions; Default, Random, Specific etc
    if kwargs["args"] == "short":
        for n in range(3):  # gets details from 3 random background types (rather than all 10)
            data = choice(list(backgrounds_data.values()))
            detail_type = choice(list(data["detail sets"].values()))
            line = f"\n{get_text(detail_type['detail title'])}: "
            line += f"{get_text(choice(detail_type['details']))}"
            text += line
    else:
        for background_type, data in backgrounds_data.items():
            # text += f"{len(data['detail sets'])} * "
            detail_type = choice(list(data["detail sets"].values()))
            line = f"\n{get_text(detail_type['detail title'])}: "
            line += f"{get_text(choice(detail_type['details']))}"
            text += line

    return text


def get_text(text):
    replace_text = False
    if "[" in text:
        replace_text = True
    while replace_text:
        replace = get_key_from_string(text)
        substitute = "MISSING SUBSTITUTE!"
        # replace with one from set
        if "/" in replace:
            substitute = get_random_item(replace, "/")
        # replace with die roll
        elif "*" in replace:
            substitute = str(get_value_from_die_roll_string(replace))
        # if is number look up appropriate table
        elif replace.isnumeric():
            substitute = get_detail_from_table(int(replace))
        text = text.replace(f"[{replace}]", substitute)
        if "[" not in text:
            replace_text = False

    return text


def get_detail_from_table(table_id):
    global backgrounds_data
    for background_type, data in backgrounds_data.items():
        if table_id in data["detail sets"]:
            return choice(data["detail sets"][table_id]["details"])
    return f"WARNING! failed to find table_id: {table_id}"


def get_value_from_die_roll_string(string):
    """* denotes d in expression 1d10, split into number of times to randint between 1 and second value
    it can also cope with use + to add and x to multiply, was created to handle:
    1*10 = 1d10
    10+1*10 = 10 + 1d10
    1*10x5 = 1d10 * 5"""
    add = 0
    multiply = 1
    if "+" in string:
        elements = string.split("+")
        for item in elements:
            if item.isnumeric():
                add = int(item)
            else:
                string = item
    if "x" in string:
        elements = string.split("x")
        for item in elements:
            if item.isnumeric():
                multiply = int(item)
            else:
                string = item
    die_roll = 0
    for n in range(int(string.split("*")[0])):
        die_roll += randint(1, int(string.split("*")[1]))
    die_roll = (die_roll * multiply) + add
    return die_roll

def test(arg):
    print(get_text(arg))
    #print(get_value_from_die_roll_string(arg))
    #print(get_detail_from_table(arg))

