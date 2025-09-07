from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import json
from tkinter.messagebox import showinfo

import pandas

import backgrounds
import character_creator
import trade_creator
import utilities
import group_data
import inn_creator
import family_member
import mutant_creator
from mutant_creator import Mutation
from family_member import FamilyMember
from character_creator import GameCharacter, init_skills_data, create_character_details, get_random_level, \
    init_name_data, init_talents_data, init_magic_data, is_valid_magic, init_details, create_one_line_details, \
    get_one_line_traits
from random import randint, choice
import pyperclip  # for using the clipboard
from trade_creator import init_trade_data, Vessel, get_passenger_numbers
from utilities import split_into_lines, get_dictionary_as_string
from backgrounds import init_backgrounds_data
from group_data import groups
from inn_creator import Inn

# ------------------------ VARIABLES ----------------------------


career_data = {}  # career_name : {chance: tuple, level_data: list}
character_details = {}
character = None
valid_races = []  # set in init_data for checking valid user input

extra_details = {
    "Origin": {"function": trade_creator.get_origin, "args": ""},
    "Chat": {"function": trade_creator.get_captain_data, "args": "captain_says"},
    "Background": {"function": backgrounds.get_background, "args": ""},
    "[Background]short": {"function": backgrounds.get_background, "args": "short"},
}

detail_data_sets = {
    "Default": ["Trait", "Ambition", "Opinion"],
    "Captain": ["Origin", "Trait", "Quirk", "Opinion", "Chat"],
    "All": ["Origin", "Trait", "Motivation", "Ambition", "Quirk", "Opinion", "Chat"], #  this is no longer actually All! 21-02-23
    "Motivated": ["Trait", "Motivation"],
    "Quirky": ["Origin", "Trait", "Quirk"],
    "Background": ["Background"],  # this is a temp set up for testing, ideally should be 'Verbose' or something 11-12-22
    "Background short": ["Trait", "[Background]short", "Opinion"],  # as above
    "Conflict": ["Driven by", "Towards", "Is"],  # inspired by https://playfulvoid.game.blog/2023/02/10/internal-conflicts-in-osr-play/
    "5e": ["Ideal", "Bond", "Flaw"],  # from https://traversefantasy.blogspot.com/2023/02/d-5es-dialogue-procedure-npc-traits.html
    "Basic": ["Personality"],
    "Cairn": ["CairnBackground", "CairnQuirk", "CairnGoal", "CairnVirtue", "CairnVice"], # from https://cairnrpg.com/second-edition/wardens-guide/npc-tables/
    "CairnShort": ["CairnQuirk", "CairnGoal", "CairnVirtue", "CairnVice"],
    "None": []
}



dreams_data = [] # a list of lists
detail_set_options = []
career_options = []
magic_options = ["None", "Beasts", "Death", "Fire", "Heavens", "Metal", "Life", "Light", "Shadow", "Manann", "Morr",
                  "Myrmidia", "Ranald", "Rhya", "Shallya", "Sigmar", "Taal", "Ulric", "Verena", "Hedgecraft",
                  "Witchcraft", "Daemonology", "Necromancy", "Petty", "Arcane"]
group_options = []

inn_busy_states = ["random", "Quiet", "Middling", "Busy"]
inn_quality_options = ["random", "Cheap", "Average", "Expensive"]
inn = None
character_group = []
add_relationships = 0
# ------------------------ BUTTON FUNCTIONS ----------------------------


def click_csv_to_wiki():
    print("csv_to_wiki")
    # TODO read in csv data file
    try:
        with open("Data/csv_to_wiki_data.csv", mode="r") as data_file:
            data = data_file.readlines()
    except FileNotFoundError:
        print("Missing CSV file!")
        return
    # TODO replace commas with "|"
    wiki_string = "<<|\n"
    for lines in data:
        wiki_string += lines.replace(",", " |")
    wiki_string += "\n>>"
    # TODO copy to clipboard
    pyperclip.copy(wiki_string)


def click_clear():
    # TODO remove mutant_test!
    global character_details
    character_details = {}
    print("clear")
    label_output["text"] = ""
    # mutant_test_new = Mutation()
    # print(mutant_test_new.get_output())


def click_create_vessel():
    vessel = vessel_dropdown.get()
    if trade_creator.is_valid_vessel_type(vessel):
        create_vessel(vessel)


def click_random_vessel():
    create_vessel()


def click_details():
    global character_details
    race = race_dropdown.get()
    if not is_valid_race_input(race):
        return
    detail_set = detail_set_dropdown.get() # input_details.get()
    # if no detail set chosen do random
    if checked_random_details_state.get() == 1:
        detail_set = choice(list(detail_data_sets.keys()))
    if checked_one_line_details_state.get():
        career = ""
        name = ""
        wiki_output = checked_wiki_output_state.get() == 1
        if checked_one_line_career_state.get():
            career = f"({get_random_career_key()}) "
        label_output["text"] = create_one_line_details(get_gender(), race, checked_one_line_traits_state.get(), career, name, wiki_output)
        character_details.clear()
        character_details["OneLine"] = label_output["text"]
    else:
        character_details = create_character_details(get_gender(), race, get_details_data(race, detail_set), checked_wiki_output_state.get())
        #label_output["text"] = get_dictionary_as_string(character_details, 50, ["Name"], ['Background'])
        label_output["text"] = get_dictionary_as_string(character_details, 50, ["Name", "CairnBackground", "CairnQuirk", "CairnGoal", "CairnVirtue", "CairnVice"], ['Background'], ['CairnBackground', 'CairnQuirk', 'CairnGoal', 'CairnVirtue'])
    pyperclip.copy(label_output["text"])


def click_create():
    global career_data, character, valid_races
    career_name = careers_dropdown.get() #input_career.get()
    level = int(input_level.get())
    race = race_dropdown.get()
    if is_valid_character_input(career_name, level, race):
        character = create_character(career_name, level, race, magic_dropdown.get(), character_details)
        if character is not None:
            display_character_stats(character)


# def click_random():
#     global character_details, character
#     # get random race here if checkbox set
#     race = get_race()
#     detail_set = input_details.get()
#     if checked_random_details_state.get() == 1:
#         detail_set = choice(list(detail_data_sets.keys()))
#     character_details = create_character_details(get_gender(), race, get_details_data(race, detail_set), checked_wiki_output_state.get())
#     character = create_character(get_random_career_key(race), get_random_level(), race, "None", character_details)
#     display_character_stats(character)


def click_save():
    save_to = f"Output/{input_filename.get()}.txt"
    if radio_save.get() == 1:
        try:
            with open(save_to, "a") as save_data:
                text = f"\n*****************************************\n\n{pyperclip.paste()}\n"
                save_data.write(text)
        except FileNotFoundError:
            with open(save_to, "w") as save_data:
                print("Creating new file")
                # currently just uses the text copied to the clipboard as we don't store the character yet 1-11-22
                text = pyperclip.paste() + "\n\n"
                save_data.write(text)
    else:
        with open(save_to, "w") as save_data:
            # currently just uses the text copied to the clipboard as we don't store the character yet 1-11-22
            text = pyperclip.paste() + "\n\n"
            save_data.write(text)


def click_add_levels():
    global character, career_data
    if character is not None:
        career_name = careers_dropdown.get()
        level = int(input_level.get())
        if is_valid_character_input(career_name, level, character.race):
            # TODO check here or elsewhere that we are not adding a new magic domain
            # Its not actually possible to check here as problems are likely ony caused when Talents are added
            magic_domain = magic_dropdown.get()
            if is_valid_magic(magic_domain):
                character.add_levels(career_name, level, career_data[career_name]['level_data'], magic_domain)
                display_character_stats(character)
            else:
                messagebox.showinfo(title="Oops!", message=f"{magic_domain} is not valid magic type!")
    else:
        print("No character to add level to")


def click_create_group():
    global character_group
    group_type = groups_dropdown.get()
    if group_type in groups:
        character_group = create_group(group_type)
        output_group(character_group)
    else:
        valid_groups = ""
        for k, v in groups.items():
            valid_groups += k + ", "
        messagebox.showinfo(title="Oops!", message=f"{group_type} is not valid Character group, choose from: {valid_groups}")


def click_update_group():
    global add_relationships
    print("Update Group!")
    if add_relationships != checked_add_relationships_state.get():
        if checked_add_relationships_state.get() == 1:
            add_group_relationships(character_group)
        add_relationships = checked_add_relationships_state.get()
    if len(character_group) > 0:
        output_group(character_group)
    else:
        messagebox.showinfo(title="Oops!", message=f"No group to update! Create one first")


def click_create_dreams():
    create_dreams(int(input_number_dreams.get()))


def click_create_inn():
    global inn
    inn = Inn(inn_quality_dropdown.get(), inn_occupied_dropdown.get())
    innkeep_data = utilities.get_random_chance_entry(inn_creator.proprietor_type, "chance")
    innkeep = create_innkeep(innkeep_data)
    # innkeep.family = create_character_family(innkeep, innkeep_data['family_chance'])
    innkeep.family = create_persons_family(innkeep, innkeep_data['family_chance'])
    inn.set_proprietor(innkeep)
    clientele_groups = inn.get_clientele_groups()
    inn.set_clientele(create_inn_clientele(clientele_groups))
    output_inn()

def inn_occupied_changed(event):
    # print("Woot this worked!!!!")
    # showinfo(
    #     title='Result',
    #     message=f'You selected {inn_occupied_dropdown.get()}!'
    # )
    on_inn_input_changed()


def inn_checkbox_changed():
    # print("Woot this worked!!!!")
    on_inn_input_changed()


def on_inn_input_changed():
    if inn is not None:
        button_update_inn["state"] = "normal"


def output_inn():
    if inn is not None:
        include_traits = checked_one_line_traits_state.get() == 1
        one_line_stats = checked_one_line_stats_state.get() == 1
        show_clientele = checked_show_clientele_state.get() == 1
        is_wiki_output = checked_wiki_output_state.get() == 1
        show_family = checked_innkeep_family_state.get() == 1
        label_output["text"] = inn.get_output(include_traits, one_line_stats, show_clientele, is_wiki_output, show_family)
        pyperclip.copy(label_output["text"])
    else:
        messagebox.showinfo(title="Oops!", message=f"Create Inn first!")


def click_update_inn():
    # TODO add checking if clientele has changed
    amount_clientele = inn_occupied_dropdown.get()
    if amount_clientele != "random":
        if amount_clientele != inn.occupied:
            inn.set_occupied(amount_clientele)
            clientele_groups = inn.get_clientele_groups()
            inn.set_clientele(create_inn_clientele(clientele_groups))

    output_inn()
    # commented out as we may want to re-output when group inputs are changed
    # button_update_inn["state"] = "DISABLED"

def attribute_test():
    attribs = {"WS": {"val": 1}, "BS": 2}
    for k, v in attribs.items():
        print(k)


def get_race():
    race = race_dropdown.get()
    if checked_random_race_state.get() == 1:
        race = character_creator.get_random_race()
        race_dropdown.set(race)
        #print(f"Got random race: {race}")
    else:
        if not is_valid_race_input(race):
            return "Human"
    return race


def is_valid_race_input(race):
    if race not in valid_races:
        messagebox.showinfo(title="Oops!", message=f"Failed to find race {race}! valid races = {valid_races}")
        return False
    return True


def is_valid_character_input(career_input, level_input, race):
    if level_input < 1 or level_input > 4:
        messagebox.showinfo(title="Oops!", message=f"Level must be between 1 and 4")
        return False
    if is_valid_race_input(race):
        if career_input in career_data:
            if race not in career_data[career_input]["chance"]:
                show_valid_careers(race)
                return False
            else:
                return True
        else:
            show_valid_careers(race)
            return False
    return False


def show_valid_careers(race):
    # print(f"invalid career for {race}")
    header = f"Valid careers for {race}:\n"
    output = ""
    for career, data in career_data.items():
        if race in data["chance"]:
            output += f"{career}, "
    label_output["text"] = header + utilities.split_into_lines(output, 100)


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
    init_dream_data()
    mutant_creator.init_mutation_data()


def init_dream_data():
    #print("Dream Data Init")
    global dreams_data
    try:
        data = pandas.read_csv("Data/Character_Data-Dreams.csv")
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Missing Character_Data-Dreams.csv")
    else:
        for col in data.columns:
            dreams = data[col].tolist()
            dreams.append(col)
            dreams_data.append(dreams)
        # for dreams in dreams_data:
        #     for dream in dreams:
        #         print(dream)


def init_ui_dropdowns():
    for k, v in detail_data_sets.items():
        detail_set_options.append(k)
    init_ui_career_dropdown()
    for k, v in groups.items():
        group_options.append(k)


def init_ui_career_dropdown(race='Human'):  # Note hack (maybe?) of passing race - shouldn't do this?
    career_options.clear()
    for key, value in career_data.items():
        if race in value['chance']:
            career_options.append(key)
    career_options.sort()

# -------------------------- FUNCTIONALITY --------------------------------------


def create_innkeep(innkeep_data):
    # print(f"Inkeep race: {innkeep_data['race']} family chance: {innkeep_data['family_chance']}")
    gender = choice(["male", "female"])
    details = create_character_details(gender, innkeep_data['race'], "one_line_traits", checked_wiki_output_state.get())
    level = 2  # TODO probs add a range, or maybe even user input here
    innkeep = create_character("Townsman", level, innkeep_data['race'], "None", details)
    return innkeep


def create_persons_family(person, family_chance):
    family = []
    roll = randint(1, 100)
    # TODO implement using some kind of data here rather than hard coded number of adults and children
    if roll <= family_chance:
        num_other_adults = randint(0, 2)
        num_children = choice([0, 0, 0, 0, 1, 2, 3, 5])
        if num_other_adults == 0:
            num_children = choice([1, 1, 1, 2, 3])
        # create adults
        family = []
        for n in range(num_other_adults):
            relationship = choice(["sibling", "parent", "partner", "partner"])
            if relationship == "partner":
                for relative in family:
                    if relative.relationship == "Husband" or "Wife":
                        relationship = "sibling"
            if relationship == "parent":
                # if parent random it, if find parent set specific
                current_parents = []
                for relative in family:
                    if relative.is_parent():
                        current_parents.append(relative.relationship)
                if len(current_parents) == 0:
                    relationship = choice(["Mother", "Father"])
                elif len(current_parents) > 1:
                    relationship = "sibling"
                else:
                    if current_parents[0] == "Mother":
                        relationship = "Father"
                    else:
                        relationship = "Mother"
            other_adult = FamilyMember(relationship, person.details["Gender"], person.race)
            family.append(other_adult)
        # add details to adults
        for adult in family:
            name = f"{adult.relationship} {adult.name}"
            career = ""
            add_traits = checked_one_line_traits_state.get()
            wiki_output = checked_wiki_output_state.get() == 1
            adult.set_details(create_one_line_details(adult.gender, person.race, add_traits, career, name, wiki_output))
        # create children
        for x in range(0, num_children):
            child = FamilyMember("child", person.details["Gender"], person.race)
            family.append(child)

    return family

def create_inn_clientele(clientele_types):
    clientele = []
    for c in clientele_types:
        new_group = {"group_name": c, "members": create_group(c, details="one_line")}
        if c == "merchant caravan":
            num_goods = int(len(new_group["members"])/3)
            print(f"num goods: {num_goods}")
            new_group["goods"] = f" {trade_creator.get_cargo_simple(num_goods)}"
        clientele.append(new_group)
    return clientele


def create_dreams(num_dreams):
    dream_text = ""
    for n in range(num_dreams):
        print(f"dream {n}")
        dream_text += (utilities.get_random_list_item(utilities.get_random_list_item(dreams_data))) + "\n"
        dream_index = (randint(1, len(dreams_data))) -1
        dream_text += choice(dreams_data[dream_index]) + "\n"
        # TODO should add this as a variable somewhere, essentially its hard coded that there will be between 2 to 5 elements in a dream
        num_tries = 3
        while num_tries > 0:
            num_tries -= 1
            dream_index = utilities.get_next_number(dream_index, len(dreams_data) -1)
            if utilities.roll_under(50):
                dream_text += choice(dreams_data[dream_index]) + "\n"
        dream_text += "\n"
    print(dream_text)
    label_output["text"] = dream_text
    pyperclip.copy(dream_text)


def create_group(group_type, **options):  # details="one_line", relationship="random"
    print(f"Clicked create group: {group_type}")
    group = []
    one_line_details = checked_one_line_details_state.get() == 1
    create_relationships = checked_add_relationships_state.get() == 1
    # override user input options if passed - added for inn clientele 27/8/25
    if "details" in options:
        print(f"Got details in options: {options['details']}")
        one_line_details = options["details"] == "one_line"
    if "relationship" in options:
        create_relationships = options["relationship"] == "random"
    for members in groups[group_type]:
        num_members = randint(members["number"][0], members["number"][1])
        print(f"would create {num_members} group members")
        # TODO at some point drive race from data rather than hard coded, complicated just due to career chances
        race = "Human"
        magic = "None"
        if "magic" in members:
            magic = members["magic"]
        collective_career = ""  # Added for handling Groups of travellers where they all share one random career
        if len(collective_career) == 0 and "group_type" in members:
            if members["group_type"] == "collective":
                collective_career = choice(members["career"])
                # print(f"Got collective career: {collective_career}")
        for member in range(num_members):
            details_set = "one_line_traits"
            if not one_line_details:
                details_set = get_details_data(race, choice(members["details"]))
                print("!!Not One Line Details!!")
            details = create_character_details(get_gender(), race, details_set, checked_wiki_output_state.get())
            # TODO if lower of levels is not 1 just use basic logic to determine 11/8/25
            level = members["level"][1]
            if members["level"][1] != members["level"][0]: # if both tuple values are not the same get a random val using 2nd as highest
                if members["level"][0] > 1:
                    level = randint(members["level"][0], members["level"][1])
                else:
                    level = get_random_level(level)
            career_key = collective_career
            print(f"Collective career here: {collective_career}")
            if len(career_key) == 0:
                career_key = choice(members["career"])
            group_member = create_character(career_key, level, race, magic, details)
            # test for leader = should always be first
            if len(group) == 0:
                print(f"Created Leader: {group_member.details['Name']} - Level range was: {members['level'][0]} to {members['level'][1]}")
            group.append(group_member)
    # add family if specified
    if "group_type" in members:
        if members["group_type"] == "family":
            for person in group:
                person.family = create_persons_family(person, 100)
    # if Add Relationship ticked add one for each member of group
    add_relationships != checked_add_relationships_state.get()
    if create_relationships:
        group = add_group_relationships(group)
    return group


def add_group_relationships(group):
    if len(group) > 1:
        for person in group:
            # get random person in group who is not me
            subject = utilities.get_random_list_item(group, person)
            subject_name = subject.details['Name'].replace('*', '')
            # add_detail("Relationship", name-of-other-person)
            person.add_detail("Relationship", f" {choice(character_creator.relationship_types)} {subject_name}")
    return group


def output_group(group):
    group_text = ""
    save_text = ""
    if checked_one_line_details_state.get():
        for person in group:
            group_text += f"{person.get_one_line_details(checked_one_line_traits_state.get())} \n"
            # check for one line stats and handle here - would mean for a group must also have one line deets
            if checked_one_line_stats_state.get():
                group_text += f"{person.get_one_line_stats()}\n"
            if checked_show_relationships_state.get() == 1 and "Relationship" in person.details:
                group_text += f"{person.details['Relationship']}\n"
            if person.has_family():
                group_text += person.get_family_output(checked_one_line_traits_state.get(),False)
            group_text += "\n"
            save_text = group_text
    else:
        if checked_minimal_stats_state.get() == 1:  # output only description
            for person in group:
                group_text += person.get_output(wiki_output=checked_wiki_output_state.get(), output_type="minimal") + "\n"
                save_text += person.get_output(wiki_output=checked_wiki_output_state.get(), output_type="minimal") + "\n"
        else:
            for person in group:
                # get all descriptions
                group_text += person.get_output(wiki_output=checked_wiki_output_state.get(), output_type="ignore", group_stage=1)
                save_text += person.get_output(wiki_output=checked_wiki_output_state.get(), output_type="save", group_stage=1)
            for person in group:
                # get all stats
                group_text += person.get_output(wiki_output=False, group_stage=2) + "\n"
                save_text += person.get_output(wiki_output=checked_wiki_output_state.get(), output_type="save", group_stage=2) + "\n"
    label_output["text"] = group_text
    pyperclip.copy(save_text)


def create_vessel(vessel_type=""):
    global character_details, character
    vessel = Vessel(vessel_type)
    vessel_data = vessel.get_vessel_data()
    passengers = get_passenger_numbers(vessel_data)
    for i in range(len(passengers)):
        passengers[i] = f"{passengers[i]} {get_random_career_key()}"
    vessel.set_passengers(passengers)
    vessel_details = vessel.get_output()
    if checked_captain_state.get() == 1:
        captain_race = get_race()
        character_details = create_character_details(get_gender(), captain_race,
                                                     get_details_data(captain_race, "Captain"), checked_wiki_output_state.get())
        captain_level = get_random_level(vessel_data["captain_level"])
        captain_career = choice(vessel_data["captain_career"])
        character = create_character(captain_career, captain_level, captain_race, "None", character_details)
        label_output["text"] = vessel_details + "\n\n--------CAPTAIN----------\n\n" + character.get_output(wiki_output=checked_wiki_output_state.get())
        pyperclip.copy(vessel_details + "\n\n--------CAPTAIN----------\n\n" + character.get_output(wiki_output=checked_wiki_output_state.get(), output_type="save"))
    else:
        label_output["text"] = vessel_details
        pyperclip.copy(label_output["text"])



def get_details_data(race, set_name):
    details_data = {}
    if set_name in detail_data_sets:
        # print(f"detail set {set_name}: {detail_data_sets[set_name]}")
        for key in detail_data_sets[set_name]:
            # print(f"key: {key}")
            if key in extra_details:  # extra details contains the instructions on how to create the initial data
                if "[" in key: # brackets used for having different behaviours for the same key, added for Backgrounds random
                    details_data[utilities.get_key_from_string(key)] = extra_details[key]["function"](race=race, args=extra_details[key]["args"])
                else:
                    details_data[key] = extra_details[key]["function"](race=race, args=extra_details[key]["args"])
            else:
                details_data[key] = ""
    # print(details_data)
    return details_data


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
    for key, value in career_data.items():
        if race in value['chance']:
            chance = value['chance'][race]
            # print(f"{chance}")
            if roll > chance[0] and roll <= chance[1]:
                return key
    messagebox.showinfo(title="Oops!", message=f"Failed to find random character key of race {race}! rolled: {roll}")


def create_character(career, level, race, magic_domain, details):
    global career_data, character
    # this check for valid magic should now be redundant now that dropdowns are implemented 6/7/25
    if is_valid_magic(magic_domain):
        return GameCharacter(career, level, career_data[career]['level_data'], magic_domain, race, details)
    else:
        messagebox.showinfo(title="Oops!", message=f"{magic_domain} is not valid magic type!")
        return


def display_character_stats(character):
    # TODO replace logic with call to simply use character output
    one_line_only = checked_one_line_stats_state.get() == 1
    label_output["text"] = character.get_output(wiki_output=checked_wiki_output_state.get(), one_line_stats=one_line_only)
    pyperclip.copy(character.get_output(wiki_output=checked_wiki_output_state.get(), one_line_stats=one_line_only))


def output_trappings_data(data):  # Just a Test function
    text = ""
    for item, value in data.items():
        text += f"----------- {item} ----------------\n"
        for career in value['level_data']:
            text += career['Trappings'] + "\n"
    with open("Output/trappings_data.txt", "w") as trappings_data:
        trappings_data.write(text)


def test_character_data():
    all_characters = []
    race = "Wood Elf"
    for career in career_data:
        if race in career_data[career]["chance"]:
            for level in range(1, 5):
                all_characters.append(GameCharacter(career, level, career_data[career]['level_data'], "None", race))
    # character_creator.test_data(all_characters)


def test_random_race_data():
    for career, data in career_data.items():
        print(f"{career} chances: {data['chance']}")


def test_print_careers(race="Human"):
    for key, value in career_data.items():
        if race in value['chance']:
            print(key)


def test_list_pruning(text, exclude_1, exclude_2):
    text_list = [item for item in text if exclude_1 not in item and exclude_2 not in item]
    for item in text_list:
        print(item)

def kwarg_test(a, b, **my_data):
    print(f"a = {a}")
    print(f"a = {b}")
    if "name" in my_data:
        print(f"Got name: {my_data['name']}")
    for key, value in my_data.items():
        print(value)
        if key == "gender":
            print(f"We found an entry for gender: {key}")

# ---------------------------- DATA SETUP ----------------------------- #

init_data()
init_skills_data()
init_trade_data()
init_name_data()
init_talents_data()
init_magic_data()
init_details()
init_backgrounds_data()  # note this has now been moved to backgrounds.py 11-12-22
inn_creator.init_data()
init_ui_dropdowns()

# ---------------------------- UI SETUP ------------------------------- #

window = Tk()
window.title("Character Creator")
window.config(padx=20, pady=20)
# Save & Output
button_clear = Button(text="Clear", width=15, command=click_clear)
button_save = Button(text="Save", width=15, command=click_save)
label_filename = Label(text="Save to: ")
input_filename = Entry(width=15)
radio_save = IntVar()
radio_save.set(1)
radio_append = Radiobutton(text="Append", value=1, variable=radio_save)
radio_replace = Radiobutton(text="Replace", value=2, variable=radio_save)
checked_wiki_output_state = IntVar()
checkbutton_wiki_output = Checkbutton(text="Wiki Output?", variable=checked_wiki_output_state)
checked_wiki_output_state.set(1)
button_csv_to_wiki = Button(text="csv to wiki", width=15, command=click_csv_to_wiki)

# Details & Sets
label_details = Label(text="Detail Set:")
#input_details = Entry(width=12)
detail_set_dropdown = ttk.Combobox(values=detail_set_options)
detail_set_dropdown.set(detail_set_options[0])  # note could also use choice(detail_set_options) to have random start
label_gender = Label(text="Gender: ")
radio_gender = IntVar()
radio_gender.set(3)
radio_male = Radiobutton(text="Male", value=1, variable=radio_gender)
radio_female = Radiobutton(text="Female", value=2, variable=radio_gender)
radio_random = Radiobutton(text="Random", value=3, variable=radio_gender)
checked_random_details_state = IntVar()
checkbutton_random_details = Checkbutton(text="Random Details Set?", variable=checked_random_details_state)
checked_random_details_state.get()
button_details = Button(text="Create Details", width=15, command=click_details)

# Career
label_career = Label(text="Career: ")
#input_career = Entry(width=12)
careers_dropdown = ttk.Combobox(values=career_options)
careers_dropdown.set(get_random_career_key())
label_level = Label(text="Level: ")
input_level = Entry(width=3)

label_race = Label(text="Race:")
#input_race = Entry(width=10)
race_dropdown = ttk.Combobox(values=valid_races)
race_dropdown.set("Human")

label_magic = Label(text="Magic:")
#input_magic = Entry(width=10)
magic_dropdown = ttk.Combobox(values=magic_options)
magic_dropdown.set(magic_options[0])
button_create = Button(text="Create Character", command=click_create)
#button_random = Button(text="Random", command=click_random)
checked_random_race_state = IntVar()
checkbutton_random_race = Checkbutton(text="Randomize Race?", variable=checked_random_race_state)
checked_random_race_state.get()
button_add_level = Button(text="Add Career", command=click_add_levels)


# Groups
label_group = Label(text="Group:")
#input_group = Entry(width=15)
groups_dropdown = ttk.Combobox(values=group_options)
groups_dropdown.set(choice(group_options))
checked_minimal_stats_state = IntVar()
checkbutton_minimal_stats = Checkbutton(text="No Stats?", variable=checked_minimal_stats_state)
checked_add_relationships_state = IntVar()
add_relationships = checked_add_relationships_state.get()
checkbutton_add_relationships = Checkbutton(text="Add Relationships?", variable=checked_add_relationships_state)
button_group = Button(text="Create Group", command=click_create_group)
button_update_group = Button(text="Update Group", command=click_update_group)


# Details Options
label_details_options = Label(text="Details Options", bg="lightblue")
checked_one_line_details_state = IntVar()
checkbutton_one_line = Checkbutton(text="One line only?", variable=checked_one_line_details_state)
checked_one_line_details_state.set(1)
checked_one_line_traits_state = IntVar()
checkbutton_one_line_traits = Checkbutton(text="Include Traits?", variable=checked_one_line_traits_state)
checked_one_line_traits_state.set(1)
checked_one_line_career_state = IntVar()
checkbutton_one_line_career = Checkbutton(text="Include Career?", variable=checked_one_line_career_state)
checked_one_line_stats_state = IntVar()
checkbutton_one_line_stats = Checkbutton(text="One line stats?", variable=checked_one_line_stats_state)
checked_one_line_stats_state.set(0)
checked_show_relationships_state = IntVar()
checkbutton_show_relationships = Checkbutton(text="Show relationships?", variable=checked_show_relationships_state)
checked_show_relationships_state.set(1)

# Vessels
label_vessel = Label(text="Vessel:")
#input_vessel = Entry(width=10)
vessel_dropdown = ttk.Combobox(values=trade_creator.get_vessel_types())
vessel_dropdown.set("Barge")  # this is a bit hacky as it relies on Barge being in the data
# checkbox for generate captain here
checked_captain_state = IntVar()
checkbutton_create_captain = Checkbutton(text="Create Captain?", variable=checked_captain_state)
checked_captain_state.set(1)

button_create_vessel = Button(text="Create Vessel", command=click_create_vessel)
button_random_vessel = Button(text="Random", command=click_random_vessel)

# Dreams

label_dreams = Label(text="Dreams (number): ")
input_number_dreams = Entry(width=3)
button_dreams = Button(text="Create Dreams", command=click_create_dreams)

# Inns

label_inns = Label(text="Inns: ")
label_inn_quality = Label(text="Quality:")
inn_quality_dropdown = ttk.Combobox(values=inn_quality_options)
inn_quality_dropdown.set("random")
label_inn_clientele = Label(text="Clientele:")
inn_occupied_dropdown = ttk.Combobox(values=inn_busy_states)
inn_occupied_dropdown.set("random")
inn_occupied_dropdown.bind('<<ComboboxSelected>>', inn_occupied_changed)
checked_show_clientele_state = IntVar()
checkbutton_show_clientele = Checkbutton(text="Show Clientele?", variable=checked_show_clientele_state, command=inn_checkbox_changed)
checked_show_clientele_state.set(1)
checked_innkeep_family_state = IntVar()
checkbutton_innkeep_family = Checkbutton(text="Innkeep Family?", variable=checked_innkeep_family_state, command=inn_checkbox_changed)
checked_innkeep_family_state.set(1)
button_inns = Button(text="Create Inn", command=click_create_inn)
button_update_inn = Button(text="Update Inn", command=click_update_inn, state=DISABLED)

# Output
label_output = Label(text="Character output goes here", width=100, height=40, justify="left", anchor="n", pady=20)

# Save & Output ----------------------------------------
button_clear.grid(column=0, row=0)
button_save.grid(column=2, row=0, columnspan=2)
label_filename.grid(column=4, row=0)
input_filename.grid(column=5, row=0)
input_filename.insert(0, "output")
radio_append.grid(column=6, row=0)
radio_replace.grid(column=7, row=0)
checkbutton_wiki_output.grid(column=8, row=0)
button_csv_to_wiki.grid(column=11, row=0)

# Details & Sets
label_details.grid(column=0, row=1)
#input_details.grid(column=1, row=1)
#input_details.insert(0, "Motivated")
# input_details.insert(0, "Background")
detail_set_dropdown.grid(column=1, row=1) # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
label_gender.grid(column=2, row=1)
radio_male.grid(column=3, row=1)
radio_female.grid(column=4, row=1)
radio_random.grid(column=5, row=1)
checkbutton_random_details.grid(column=6, row=1)
button_details.grid(column=7, row=1, columnspan=1)

# Career
label_career.grid(column=0, row=2)
#input_career.grid(column=1, row=2)
careers_dropdown.grid(column=1, row=2)
label_level.grid(column=2, row=2)
input_level.grid(column=3, row=2)
input_level.insert(0, "1")
label_race.grid(column=4, row=2)
race_dropdown.grid(column=5, row=2)
label_magic.grid(column=6, row=2)
magic_dropdown.grid(column=7, row=2)
button_create.grid(column=8, row=2)
#button_random.grid(column=9, row=2)
checkbutton_random_race.grid(column=10, row=2)
button_add_level.grid(column=11, row=2)


# Groups
label_group.grid(column=0, row=3)
groups_dropdown.grid(column=1, row=3)
#input_group.insert(0, "None")
checkbutton_minimal_stats.grid(column=2, row=3)
checkbutton_add_relationships.grid(column=3, row=3)
button_group.grid(column=4, row=3)
button_update_group.grid(column=5, row=3)

# Details Options

label_details_options.grid(column=0, row=4)
checkbutton_one_line.grid(column=1, row=4)
checkbutton_one_line_traits.grid(column=2, row=4)
checkbutton_one_line_career.grid(column=3, row=4)
checkbutton_one_line_stats.grid(column=4, row=4)
checkbutton_show_relationships.grid(column=5, row=4)

# Vessels
label_vessel.grid(column=0, row=5)
vessel_dropdown.grid(column=1, row=5)
checkbutton_create_captain.grid(column=2, row=5)
button_create_vessel.grid(column=3, row=5)
button_random_vessel.grid(column=4, row=5)


# Dreams
label_dreams.grid(column=0, row=6)
input_number_dreams.grid(column=1, row=6)
input_number_dreams.insert(0, "5")
button_dreams.grid(column=2, row=6)


# Inns
label_inns.grid(column=0, row=7)
label_inn_quality.grid(column=1, row=7)
inn_quality_dropdown.grid(column=2, row=7)
label_inn_clientele.grid(column=3, row=7)
inn_occupied_dropdown.grid(column=4, row=7)
checkbutton_show_clientele.grid(column=5, row=7)
checkbutton_innkeep_family.grid(column=6, row=7)
button_inns.grid(column=7, row=7)
button_update_inn.grid(column=8, row=7)


# Output
label_output.grid(column=0, row=9, columnspan=10)

# ---------------------------- MAIN ------------------------------- #

# input_career.insert(0, get_random_career_key())
# input_group.insert(0, choice(list(groups.keys())))

#backgrounds.test("I have a [21] with [2*10+10] [pennies/warts/problems]")
#backgrounds.test("I have a [21]")
#test_character_data()
#kwarg_test(1, 10, name="Jojo", gender="male")
#kwarg_test(1, 10)
#test_random_race_data()

#output_trappings_data(career_data)
#character_creator.test_data(career_data, "talents")
#attribute_test()
#print(split_into_lines("Warning about some location visited (thieves, con-men, corrupt river wardens, corrupt officials, disease)", 10))
#test_character_data()

# test_pennies = 512
# print(f"{test_pennies} in proper notation: {utilities.get_cash_notation(test_pennies)}")
# test_list_pruning(["Cheap Fries", "Expensive Eggs", "Ham", "Cheap Peas", "Mushrooms"], "Cheap", "Expensive")
# test_print_careers()
mutant_test = Mutation()
print(mutant_test.get_output())

window.mainloop()