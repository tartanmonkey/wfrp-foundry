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

        for key, entry in backgrounds_data.items():
            for set_id, set_data in entry["detail sets"].items():
                for detail in set_data['details']:
                    print(detail)

        # for col in data.columns:
        #     details_data[col] = [item for item in data[col].tolist() if type(item) == str]
        # for key, value in details_data.items():
        #     print(f"{key}: {value}")


def get_background(**kwargs):
    return "Would have background here!"