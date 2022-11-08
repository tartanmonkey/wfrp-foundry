from tkinter import *
from tkinter import messagebox
import json
import character_creator
import trade_creator
import utilities
from character_creator import GameCharacter, init_skills_data, create_character_details, get_random_level, init_name_data
from random import randint, choice
import pyperclip # for using the clipboard
from trade_creator import init_trade_data, Vessel, get_passenger_numbers
from utilities import split_into_lines

# ------------------------ VARIABLES ----------------------------


career_data = {} # career_name : {chance: tuple, level_data: list}
character_detail_text = ""
character = None
# ------------------------ BUTTON FUNCTIONS ----------------------------


def click_clear():
    global character_detail_text
    character_detail_text = ""
    print("clear")
    label_output["text"] = ""


def click_create_vessel():
    global character_detail_text, character
    vessel = Vessel()
    vessel_data = vessel.get_vessel_data()
    passengers = get_passenger_numbers(vessel_data)
    for i in range(len(passengers)):
        passengers[i] = f"{passengers[i]} {get_random_career_key()}"
    vessel.set_passengers(passengers)
    vessel_details = vessel.get_output()
    captain_origin = trade_creator.get_origin()
    captain_says = split_into_lines(trade_creator.get_captain_data("captain_says"), 40)
    # TODO create captain as character & replace following
    character_detail_text = create_character_details(get_gender(), captain_origin, captain_says)
    captain_level = get_random_level(vessel_data["captain_level"])
    captain_career = choice(vessel_data["captain_career"])
    create_character(captain_career, captain_level)
    print(f"Captain: {captain_career} Level: {captain_level}")

    # ---Display output
    label_output["text"] = vessel_details + "\n\n--------CAPTAIN----------\n\n" + character.get_output()
    pyperclip.copy(vessel_details)


def click_details():
    global character_detail_text
    character_detail_text = create_character_details(get_gender())
    label_output["text"] = character_detail_text
    pyperclip.copy(character_detail_text)


def click_create():
    global career_data, character
    career_name = input_career.get()
    level = int(input_level.get())
    if career_name in career_data and level < len(career_data[career_name]['level_data'])+1:
        create_character(career_name, level)
    else:
        messagebox.showinfo(title="Oops!", message="Invalid Career or Level")


def click_random():
    global character_detail_text
    character_detail_text = create_character_details(get_gender())
    create_character(get_random_career_key(), get_random_level())


def click_save():
    with open("Output/output.txt", "a") as save_data:
        # currently just uses the text copied to the clipboard as we don't store the character yet 1-11-22
        text = pyperclip.paste() + "\n\n"
        save_data.write(text)


def gender_set():
    print(radio_gender.get())


def attribute_test():
    attribs = {"WS": {"val": 1}, "BS": 2}
    for k, v in attribs.items():
        print(k)

# ---------------------------- DATA SETUP ----------------------------- #

def init_data():
    global career_data
    # career_name : {chance: tuple, level_data: list}
    try:
        with open("Data/RulesData-Careers.json", "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Missing data!")
    else:
        #print("Do stuff with found data here...")
        chance_low = 0
        for entry in data:
            # print(f"entry - career: {entry['Career']}")
            if entry['Career'] in career_data:
                # Add level data to existing career
                career_data[entry['Career']]['level_data'].insert(entry['Level'] - 1, entry)
            else:
                # Create new Career entry
                chance_high = chance_low + entry['Chance']
                chance = (chance_low, chance_high)
                chance_low = chance_high
                level_data = []
                level_data.insert(entry['Level'] - 1, entry)
                career_data[entry['Career']] = {'chance': chance, 'level_data': level_data}

# -------------------------- FUNCTIONALITY --------------------------------------


def get_gender():
    gender = radio_gender.get()
    if gender == 3:
        return choice(["male", "female"])
    elif gender == 1:
        return "male"
    else:
        return "female"


def get_random_career_key():
    roll = randint(1, 100)
    # print(f"random: {roll}")
    for key, value in career_data.items():
        chance = value['chance']
        # print(f"{chance}")
        if roll > chance[0] and roll <= chance[1]:
            return key
    messagebox.showinfo(title="Oops!", message=f"Failed to find random character key! rolled: {roll}")


def create_character(career, level):
    global career_data, character
    character = GameCharacter(career, level, career_data[career]['level_data'], character_detail_text)
    display_character_stats(character)


def display_character_stats(character):
    # TODO replace logic with call to simply use character output
    label_output["text"] = character.get_output()
    pyperclip.copy(character.get_output("save"))


def test_character_data():
    all_characters = []
    for career in career_data:
        for level in range(1, 5):
            all_characters.append(GameCharacter(career, level, career_data[career]['level_data']))

    character_creator.test_data(all_characters)

# ---------------------------- UI SETUP ------------------------------- #



window = Tk()
window.title("Character Creator")
window.config(padx=20, pady=20)

button_clear = Button(text="Clear", width=15, command=click_clear)
button_save = Button(text="Save", width=15, command=click_save)

button_details = Button(text="Details", width=15, command=click_details)
label_gender = Label(text="Gender: ")
radio_gender = IntVar()
radio_gender.set(3)
radio_male = Radiobutton(text="Male", value=1, variable=radio_gender, command=gender_set)
radio_female = Radiobutton(text="Female", value=2, variable=radio_gender, command=gender_set)
radio_random = Radiobutton(text="Random", value=3, variable=radio_gender, command=gender_set)

label_career = Label(text="Career: ")
input_career = Entry(width=20)
label_level = Label(text="Level: ")
input_level = Entry(width=3)
button_create = Button(text="Create", command=click_create)
button_random = Button(text="Random", command=click_random)

button_create_vessel = Button(text="Create Vessel", width=15, command=click_create_vessel)

label_output = Label(text="Character output goes here", width=50, height=40, justify="left", anchor="n", pady=20)


button_clear.grid(column=0, row=0, columnspan=3)
button_save.grid(column=3, row=0, columnspan=3)

button_details.grid(column=0, row=1, columnspan=1)
label_gender.grid(column=1, row=1)
radio_male.grid(column=2, row=1)
radio_female.grid(column=3, row=1)
radio_random.grid(column=4, row=1)

label_career.grid(column=0, row=2)
input_career.grid(column=1, row=2)
input_career.insert(0, "Soldier")
label_level.grid(column=2, row=2)
input_level.grid(column=3, row=2)
input_level.insert(0, "1")
button_create.grid(column=4, row=2)
button_random.grid(column=5, row=2)

button_create_vessel.grid(column=0, row=3, columnspan=2)

label_output.grid(column=0, row=4, columnspan=6)

# ---------------------------- MAIN ------------------------------- #

init_data()
init_skills_data()
init_trade_data()
init_name_data()
#attribute_test()
#print(split_into_lines("Warning about some location visited (thieves, con-men, corrupt river wardens, corrupt officials, disease)", 10))
#test_character_data()




window.mainloop()