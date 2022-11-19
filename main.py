from tkinter import *
from tkinter import messagebox
import json
import character_creator
import trade_creator
import utilities
from character_creator import GameCharacter, init_skills_data, create_character_details, get_random_level, \
    init_name_data, init_talents_data, init_magic_data, is_valid_magic
from random import randint, choice
import pyperclip # for using the clipboard
from trade_creator import init_trade_data, Vessel, get_passenger_numbers
from utilities import split_into_lines, get_dictionary_as_string

# ------------------------ VARIABLES ----------------------------


career_data = {}  # career_name : {chance: tuple, level_data: list}
character_details = {}
character = None
valid_races = []  # set in init_data for checking valid user input
# ------------------------ BUTTON FUNCTIONS ----------------------------


def click_clear():
    global character_details
    character_details = {}
    print("clear")
    label_output["text"] = ""


def click_create_vessel():
    vessel = input_vessel.get()
    if trade_creator.is_valid_vessel_type(vessel):
        create_vessel(vessel)


def click_random_vessel():
    create_vessel()


def click_details():
    global character_details
    race = input_race.get()
    if not is_valid_race_input(race):
        return
    character_details = create_character_details(get_gender(), race)
    label_output["text"] = get_dictionary_as_string(character_details, 50)
    pyperclip.copy(label_output["text"])


def click_create():
    global career_data, character, valid_races
    career_name = input_career.get()
    level = int(input_level.get())
    race = input_race.get()
    if not is_valid_race_input(race):
        return
    if career_name in career_data and level < len(career_data[career_name]['level_data'])+1:
        create_character(career_name, level, race)
    else:
        messagebox.showinfo(title="Oops!", message="Invalid Career or Level")


def click_random():
    global character_details
    # clear magic input to prevent issues
    input_magic.delete(0, END)
    input_magic.insert(0, "None")

    # get random race here if checkbox set
    race = get_race()
    character_details = create_character_details(get_gender(), race)
    print(race)
    create_character(get_random_career_key(race), get_random_level(), race)


def get_race():
    race = input_race.get()
    if checked_random_race_state.get() == 1:
        race = character_creator.get_random_race()
        #print(f"Got random race: {race}")
    else:
        if not is_valid_race_input(race):
            return "Human"
    return race

def click_save():
    if radio_save.get() == 1:
        with open("Output/output.txt", "a") as save_data:
            text = pyperclip.paste() + "\n\n"
            save_data.write(text)
    else:
        with open("Output/output.txt", "w") as save_data:
            # currently just uses the text copied to the clipboard as we don't store the character yet 1-11-22
            text = pyperclip.paste() + "\n\n"
            save_data.write(text)


def attribute_test():
    attribs = {"WS": {"val": 1}, "BS": 2}
    for k, v in attribs.items():
        print(k)


def is_valid_race_input(race):
    if race not in valid_races:
        messagebox.showinfo(title="Oops!", message=f"Failed to find race {race}! valid races = {valid_races}")
        return False
    return True

# ---------------------------- DATA SETUP ----------------------------- #


def init_data():
    global career_data, valid_races
    # career_name : {chance: tuple, level_data: list}
    try:
        with open("Data/RulesData-Careers.json", "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Missing data!")
    else:
        #print("Do stuff with found data here...")
        chance_low = {"Human": 0, "Dwarf": 0, "Halfling": 0, "High Elf": 0, "Wood Elf": 0}
        for entry in data:
            # print(f"entry - career: {entry['Career']}")
            if entry['Career'] in career_data:
                # Add level data to existing career
                career_data[entry['Career']]['level_data'].insert(entry['Level'] - 1, entry)
            else:
                # Create new Career entry
                career_chances = {}
                for race, chance in chance_low.items():
                    if race not in valid_races: #  inits valid race list for later use
                        valid_races.append(race)
                    if entry[race] != 0:
                        chance_high = chance + entry[race]
                        chance_tuple = (chance, chance_high)
                        chance_low[race] = chance_high
                        career_chances[race] = chance_tuple
                level_data = []
                level_data.insert(entry['Level'] - 1, entry)
                career_data[entry['Career']] = {'chance': career_chances, 'level_data': level_data}

                # chance_high = chance_low + entry['Chance']
                # chance = (chance_low, chance_high)
                # chance_low = chance_high
                # level_data = []
                # level_data.insert(entry['Level'] - 1, entry)
                # career_data[entry['Career']] = {'chance': chance, 'level_data': level_data}

# -------------------------- FUNCTIONALITY --------------------------------------


def create_vessel(vessel_type=""):
    global character_details, character
    vessel = Vessel(vessel_type)
    vessel_data = vessel.get_vessel_data()
    passengers = get_passenger_numbers(vessel_data)
    for i in range(len(passengers)):
        passengers[i] = f"{passengers[i]} {get_random_career_key()}"
    vessel.set_passengers(passengers)
    vessel_details = vessel.get_output()
    captain_race = get_race()
    captain_origin = trade_creator.get_origin()
    captain_says = trade_creator.get_captain_data("captain_says")

    # create captain as character & replace following
    character_details = create_character_details(get_gender(), captain_race, origin=captain_origin, chat=captain_says)
    captain_level = get_random_level(vessel_data["captain_level"])
    captain_career = choice(vessel_data["captain_career"])

    create_character(captain_career, captain_level, captain_race)
    #print(f"Captain: {captain_career} Level: {captain_level}")

    # ---Display output
    label_output["text"] = vessel_details + "\n\n--------CAPTAIN----------\n\n" + character.get_output()
    pyperclip.copy(label_output["text"])

def get_gender():
    gender = radio_gender.get()
    if gender == 3:
        return choice(["male", "female"])
    elif gender == 1:
        return "male"
    else:
        return "female"


def get_random_career_key(race="Human"):
    roll = randint(1, 100)
    # print(f"random: {roll}")
    # TODO add race then change to value = value['chance'][race]
    for key, value in career_data.items():
        if race in value['chance']:
            chance = value['chance'][race]
            # print(f"{chance}")
            if roll > chance[0] and roll <= chance[1]:
                return key
    messagebox.showinfo(title="Oops!", message=f"Failed to find random character key of race {race}! rolled: {roll}")


def create_character(career, level, race):
    global career_data, character
    magic_domain = input_magic.get()
    if is_valid_magic(magic_domain):
        character = GameCharacter(career, level, career_data[career]['level_data'], magic_domain, race, character_details)
        display_character_stats(character)
    else:
        messagebox.showinfo(title="Oops!", message=f"{magic_domain} is not valid magic type!")


def display_character_stats(character):
    # TODO replace logic with call to simply use character output
    label_output["text"] = character.get_output()
    pyperclip.copy(character.get_output("save"))


def output_trappings_data(data):
    text = ""
    for item, value in data.items():
        text += f"----------- {item} ----------------\n"
        for career in value['level_data']:
            text += career['Trappings'] + "\n"
    with open("Output/trappings_data.txt", "w") as trappings_data:
        trappings_data.write(text)


def test_character_data():
    all_characters = []
    for career in career_data:
        for level in range(1, 5):
            all_characters.append(GameCharacter(career, level, career_data[career]['level_data']))
    character_creator.test_data(all_characters)


def test_random_race_data():
    for career, data in career_data.items():
        print(f"{career} chances: {data['chance']}")


def kwarg_test(a, b, **my_data):
    print(f"a = {a}")
    print(f"a = {b}")
    for key, value in my_data.items():
        print(value)
        if key == "gender":
            print(f"We found an entry for gender: {key}")
# ---------------------------- UI SETUP ------------------------------- #



window = Tk()
window.title("Character Creator")
window.config(padx=20, pady=20)

button_clear = Button(text="Clear", width=15, command=click_clear)
button_save = Button(text="Save", width=15, command=click_save)
radio_save = IntVar()
radio_save.set(1)
radio_append = Radiobutton(text="Append", value=1, variable=radio_save)
radio_replace = Radiobutton(text="Replace", value=2, variable=radio_save)

button_details = Button(text="Details", width=15, command=click_details)
label_gender = Label(text="Gender: ")
radio_gender = IntVar()
radio_gender.set(3)
radio_male = Radiobutton(text="Male", value=1, variable=radio_gender)
radio_female = Radiobutton(text="Female", value=2, variable=radio_gender)
radio_random = Radiobutton(text="Random", value=3, variable=radio_gender)

label_career = Label(text="Career: ")
input_career = Entry(width=12)
label_level = Label(text="Level: ")
input_level = Entry(width=3)

label_race = Label(text="Race:")
input_race = Entry(width=10)

label_magic = Label(text="Magic:")
input_magic = Entry(width=10)
button_create = Button(text="Create", command=click_create)
button_random = Button(text="Random", command=click_random)
checked_random_race_state = IntVar()
checkbutton_random_race = Checkbutton(text="Randomize Race?", variable=checked_random_race_state)
checked_random_race_state.get()

label_vessel = Label(text="Vessel:")
input_vessel = Entry(width=10)
# TODO add checkbox for generate captain here
button_create_vessel = Button(text="Create", command=click_create_vessel)
button_random_vessel = Button(text="Random", command=click_random_vessel)

label_output = Label(text="Character output goes here", width=50, height=40, justify="left", anchor="n", pady=20)


button_clear.grid(column=0, row=0, columnspan=3)
button_save.grid(column=3, row=0, columnspan=2)
radio_append.grid(column=5, row=0)
radio_replace.grid(column=6, row=0)

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
label_race.grid(column=4, row=2)
input_race.grid(column=5, row=2)
input_race.insert(0, "Human")
label_magic.grid(column=6, row=2)
input_magic.grid(column=7, row=2)
input_magic.insert(0, "None")
button_create.grid(column=8, row=2)
button_random.grid(column=9, row=2)
checkbutton_random_race.grid(column=10, row=2)

label_vessel.grid(column=0, row=3)
input_vessel.grid(column=1, row=3)
button_create_vessel.grid(column=3, row=3)
button_random_vessel.grid(column=4, row=3)

label_output.grid(column=0, row=4, columnspan=10)

# ---------------------------- MAIN ------------------------------- #

init_data()
init_skills_data()
init_trade_data()
init_name_data()
init_talents_data()
init_magic_data()
kwarg_test(1, 10, name="Jojo", gender="male")
#test_random_race_data()

#output_trappings_data(career_data)
#character_creator.test_data(career_data, "talents")
#attribute_test()
#print(split_into_lines("Warning about some location visited (thieves, con-men, corrupt river wardens, corrupt officials, disease)", 10))
#test_character_data()




window.mainloop()