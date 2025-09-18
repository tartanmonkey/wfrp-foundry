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
    init_name_data, init_talents_data, init_magic_data, is_valid_magic, init_details
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
vessel = None
inn = None
valid_races = []  # set in init_data for checking valid user input
dropdown_races = []  # copy of valid + 'Random'

extra_details = {
    "Origin": {"function": trade_creator.get_origin, "args": ""},
    "Chat": {"function": trade_creator.get_captain_data, "args": "captain_says"},
    "Background": {"function": backgrounds.get_background, "args": ""},
    "[Background]short": {"function": backgrounds.get_background, "args": "short"},
}

detail_data_sets = {
    "Default": ["Trait", "Ambition", "Opinion"],
    "Simple": ["Personality", "Motivation"],
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

# Added for creating Adult Family members, also used by Innkeeps
detail_sets_short = ["Default", "Simple", "Motivated", "Basic", "CairnShort"]

dreams_data = [] # a list of lists
detail_set_options = []  # stores names of detail sets loaded
detail_set_dropdown_list = []  # copy of above but with 'Random' added
career_options = []  # stores names of careers loaded
magic_options = ["None", "Beasts", "Death", "Fire", "Heavens", "Metal", "Life", "Light", "Shadow", "Manann", "Morr",
                  "Myrmidia", "Ranald", "Rhya", "Shallya", "Sigmar", "Taal", "Ulric", "Verena", "Hedgecraft",
                  "Witchcraft", "Daemonology", "Necromancy", "Petty", "Arcane"]
group_options = []

inn_busy_states = ["random", "Quiet", "Middling", "Busy"]
inn_quality_options = ["random", "Cheap", "Average", "Expensive"]
character_group = []
add_relationships = 0
show_details_options = ["Minimal", "One line", "Full", "None"]
show_stats_options = ["Minimal", "One line", "Full", "None"]
gender_options = ["Random", "Female", "Male"]

# ---------------------------- DATA SETUP ----------------------------- #


def init_data():
    global career_data, valid_races, dropdown_races
    # career_name : {chance: tuple, level_data: list}
    try:
        with open("Data/RulesData-Careers.json", "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Missing data!")
    else:
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
                dropdown_races = valid_races.copy()
                dropdown_races.append("Random")
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


def init_ui_dropdowns():
    global detail_set_options, detail_set_dropdown_list
    for k, v in detail_data_sets.items():
        detail_set_options.append(k)
    detail_set_dropdown_list = detail_set_options.copy()
    detail_set_dropdown_list.append("Random")
    init_ui_career_dropdown()
    for k, v in groups.items():
        group_options.append(k)


def init_ui_career_dropdown(race='Human'):  # Note hack (maybe?) of passing race - shouldn't do this?
    career_options.clear()
    for key, value in career_data.items():
        if race in value['chance']:
            career_options.append(key)
    career_options.sort()
    career_options.insert(0, "Random")

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


def click_create_vessel():
    global character, vessel
    captain = None
    vessel_obj = create_vessel(get_vessel_dropdown())
    vessel_data = vessel_obj.get_vessel_data()  # vessel.get_output()
    vessel = vessel_obj
    if checked_captain_state.get() == 1:
        captain_race = get_race()
        captain_details = create_character_details(get_gender(), captain_race, get_details_data(captain_race, "Captain"))
        captain_level = get_random_level(vessel_data["captain_level"])
        captain_career = choice(vessel_data["captain_career"])
        captain = create_character(captain_career, captain_level, captain_race, "None", captain_details)
        vessel_obj.set_captain(captain)
        character = captain  # left this in after adding captain as vessel variable in hopes can utilize add Mutation etc
    output_vessel(vessel_obj)
    manage_enabled_update_buttons("Vessel")


def click_update_vessel():
    if vessel is not None:
        output_vessel(vessel)


def click_create_character():
    global character
    # TODO handle random career here? - if so remove current starting on random
    career_name = get_career_dropdown()
    level = int(input_level.get())
    race = get_race()
    is_mutant = checked_mutations_state.get() == 1
    if is_valid_character_input(level):
        details = get_character_details(race)
        character = create_character(career_name, level, race, magic_dropdown.get(), details, is_mutant)
        if character is not None:
            output_character(character)
            manage_enabled_update_buttons("Character")


def click_update_character():
    if character is not None:
        output_character(character)


def click_add_levels():
    global character, career_data
    if character is not None:
        career_name = get_career_dropdown()
        level = int(input_level.get())
        if is_valid_character_input(level):
            # TODO check here or elsewhere that we are not adding a new magic domain
            # Its not actually possible to check here as problems are likely ony caused when Talents are added
            magic_domain = magic_dropdown.get()
            if is_valid_magic(magic_domain):
                character.add_levels(career_name, level, career_data[career_name]['level_data'], magic_domain)
                output_character(character)
            else:
                messagebox.showinfo(title="Oops!", message=f"{magic_domain} is not valid magic type!")
    else:
        print("No character to add level to")


def click_add_family():
    if character is not None:
        character.family = create_persons_family(character, 100)
        output_character(character)


def click_add_mutation():
    global character
    if character is not None:
        mutant_creator.add_mutations(character, 1)
        output_character(character)
    else:
        messagebox.showinfo(title="Oops!", message="You need to create a character first!")


def click_create_group():
    global character_group
    group_type = groups_dropdown.get()
    if group_type in groups:
        character_group = create_group(group_type)
        output_group(character_group)
        manage_enabled_update_buttons("Group")
    else:
        valid_groups = ""
        for k, v in groups.items():
            valid_groups += k + ", "
        messagebox.showinfo(title="Oops!", message=f"{group_type} is not valid Character group, choose from: {valid_groups}")


def click_add_relationships():
    global character_group
    if len(character_group) > 1:
        character_group = add_group_relationships(character_group)
        click_update_group()
    else:
        messagebox.showinfo(title="Oops!", message=f"No group to add to! Create one first")


def click_update_group():
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
    innkeep.family = create_persons_family(innkeep, innkeep_data['family_chance'])
    inn.set_proprietor(innkeep)
    clientele_groups = inn.get_clientele_groups()
    inn.set_clientele(create_inn_clientele(clientele_groups))
    output_inn()
    manage_enabled_update_buttons("Inn")


def click_update_inn():
    # TODO add checking if clientele has changed
    amount_clientele = inn_occupied_dropdown.get()
    if amount_clientele != "random":
        if amount_clientele != inn.occupied:
            inn.set_occupied(amount_clientele)
            clientele_groups = inn.get_clientele_groups()
            inn.set_clientele(create_inn_clientele(clientele_groups))

    output_inn()


def manage_enabled_update_buttons(button_name):
    buttons = {
        "Character": {"function": set_update_button_state_character},
        "Inn": {"function": set_update_button_state_inn},
        "Group": {"function": set_update_button_state_group},
        "Vessel": {"function": set_update_button_state_vessel}
    }
    for k, v in buttons.items():
        if k == button_name:
            state = 'normal'
        else:
            state = 'disabled'
        buttons[k]["function"](state)
    manage_secondary_buttons(button_name)


def manage_secondary_buttons(button_set):
    # TODO change so we set state based on button_set then do anyway
    new_state = 'normal'
    if button_set != "Character":
        new_state = 'disabled'
    button_add_level['state'] = new_state
    button_add_family['state'] = new_state
    button_add_mutation['state'] = new_state
    new_state = 'normal'
    if button_set != "Group":
        new_state = 'disabled'
    button_add_relationships['state'] = new_state


def set_update_button_state_inn(state):
    button_update_inn['state'] = state


def set_update_button_state_group(state):
    button_update_group['state'] = state


def set_update_button_state_character(state):
    button_update_character['state'] = state


def set_update_button_state_vessel(state):
    button_update_vessel['state'] = state

# -------------------------- HELPERS --------------------------------------


def get_vessel_dropdown():
    vessel_type = vessel_dropdown.get()
    if vessel_type == "Random":
        return ""
    return vessel_type


def get_career_dropdown():
    career_name = careers_dropdown.get()
    if career_name == "Random":
        return get_random_career_key(get_race())
    return career_name


def get_details_dropdown():
    details_set = detail_set_dropdown.get()
    if details_set == "Random":
        return choice(detail_set_options)
    return details_set


def get_character_details(race):
    detail_set = get_details_dropdown() # input_details.get()
    details = create_character_details(get_gender(), race, get_details_data(race, detail_set))
    return details


def get_race():
    race = race_dropdown.get()
    if race == "Random":
        race = character_creator.get_random_race()
        # race_dropdown.set(race) # Could uncomment this to have it show the random race
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


def is_valid_character_input(level_input):
    if level_input < 1 or level_input > 4:
        messagebox.showinfo(title="Oops!", message=f"Level must be between 1 and 4")
        return False
    return True


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
    gender = gender_dropdown.get()
    if gender == "Random":
        return choice(["male", "female"])
    return gender.lower()


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


# -------------------------- FUNCTIONALITY --------------------------------------


def create_character(career, level, race, magic_domain, details, is_mutant=False):
    global career_data, character
    # this check for valid magic should now be redundant now that dropdowns are implemented 6/7/25
    if is_valid_magic(magic_domain):
        new_character = GameCharacter(career, level, career_data[career]['level_data'], magic_domain, race, details)
        if is_mutant:
            new_character= mutant_creator.add_mutations(new_character)
        return new_character
    else:
        messagebox.showinfo(title="Oops!", message=f"{magic_domain} is not valid magic type!")
        return


def create_innkeep(innkeep_data):
    # print(f"Inkeep race: {innkeep_data['race']} family chance: {innkeep_data['family_chance']}")
    gender = choice(["male", "female"])
    detail_set = get_details_data(innkeep_data['race'], choice(detail_sets_short))
    details = create_character_details(gender, innkeep_data['race'], detail_set)
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
            adult_name = f"{adult.relationship} {adult.name}"
            detail_set = get_details_data(person.race, choice(detail_sets_short))
            adult_details = create_character_details(adult.gender, person.race, detail_set, name=adult_name)
            # wiki_output = checked_wiki_output_state.get() == 1
            adult.set_details(adult_details)
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
    is_mutant = checked_mutations_state.get()
    print(f"Clicked create group: {group_type}")
    group = []
    # override user input options if passed - added for inn clientele 27/8/25
    details_type = ""
    if "details" in options:
        print(f"Got details_type in options: {options['details']}")
        details_type = options["details"]
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
            elif members["group_type"] == "mutants":
                is_mutant = True
        for member in range(num_members):
            if details_type == "":
                details_type = choice(members["details"])
            details_set = get_details_data(race, details_type)
            details = create_character_details(get_gender(), race, details_set)
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
            group_member = create_character(career_key, level, race, magic, details, is_mutant)
            # test for leader = should always be first
            if len(group) == 0:
                print(f"Created Leader: {group_member.details['Name']} - Level range was: {members['level'][0]} to {members['level'][1]}")
            group.append(group_member)
    # add family if specified
    if "group_type" in members:
        if members["group_type"] == "family":
            for person in group:
                person.family = create_persons_family(person, 100)
    return group


def add_group_relationships(group):
    for person in group:
        # get random person in group who is not me
        subject = utilities.get_random_list_item(group, person)
        subject_name = subject.details['Name'].replace('*', '')
        # add_detail("Relationship", name-of-other-person)
        person.add_detail("Relationship", f" {choice(character_creator.relationship_types)} {subject_name}")
    return group


def create_vessel(vessel_type=""):
    vessel_obj = Vessel(vessel_type)
    vessel_data = vessel_obj.get_vessel_data()
    passengers = get_passenger_numbers(vessel_data)
    for i in range(len(passengers)):
        passengers[i] = f"{passengers[i]} {get_random_career_key()}"
    vessel_obj.set_passengers(passengers)
    return vessel_obj


# ------------------------------- OUTPUT FUNCTIONS ---------------------------------------------------------

def output_character(character_obj):
    # TODO replace logic with call to simply use character output
    details_type = show_details_dropdown.get()
    stats_type = show_stats_dropdown.get()
    label_output["text"] = character_obj.get_output(details_type, stats_type, wiki_output=checked_wiki_output_state.get())
    pyperclip.copy(label_output["text"])  # TODO double check this works, used to make teh call again to get_output


def output_trappings_data(data):  # Just a Test function
    text = ""
    for item, value in data.items():
        text += f"----------- {item} ----------------\n"
        for career in value['level_data']:
            text += career['Trappings'] + "\n"
    with open("Output/trappings_data.txt", "w") as trappings_data:
        trappings_data.write(text)


def output_group(group):
    group_text = ""
    save_text = ""
    details_type = show_details_dropdown.get()
    stats_type = show_stats_dropdown.get()
    relationship_vis = checked_show_relationships_state.get() == 1
    for person in group:
        group_text += f"{person.get_output(details_type, stats_type, wiki_output=checked_wiki_output_state.get(), show_relationship=relationship_vis)}\n\n"
        # TODO remove following if decide to have save different from wiki output 13/9/25
        # save_text += f"{person.get_output(wiki_output=checked_wiki_output_state.get())}\n\n"
        save_text = group_text
    label_output["text"] = group_text
    pyperclip.copy(save_text)


def output_vessel(vessel_obj):
    output = vessel_obj.get_output()
    if vessel_obj.captain is not None:
        details_type = show_details_dropdown.get()
        stats_type = show_stats_dropdown.get()
        output += "\n\n--------CAPTAIN----------\n\n" + vessel_obj.captain.get_output(details_type, stats_type, wiki_output=checked_wiki_output_state.get())
    label_output["text"] = output
    pyperclip.copy(label_output["text"])  # TODO consider orig also had output_type="save" on Captain output


def output_inn():
    if inn is not None:
        details_type = show_details_dropdown.get()
        stats_type = show_stats_dropdown.get()
        show_clientele = checked_show_clientele_state.get() == 1
        is_wiki_output = checked_wiki_output_state.get() == 1
        label_output["text"] = inn.get_output(details_type, stats_type, show_clientele, is_wiki_output)
        pyperclip.copy(label_output["text"])
        button_update_inn["state"] = "normal"
    else:
        messagebox.showinfo(title="Oops!", message=f"Create Inn first!")

# ------------------------------- TEST FUNCTIONS ---------------------------------------------------------


def attribute_test():
    attribs = {"WS": {"val": 1}, "BS": 2}
    for k, v in attribs.items():
        print(k)


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
vessel_dropdown_items = trade_creator.get_vessel_types().copy()
vessel_dropdown_items.append("Random")

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
detail_set_dropdown = ttk.Combobox(values=detail_set_dropdown_list)
detail_set_dropdown.set(detail_set_dropdown_list[0])  # note could also use choice(detail_set_options) to have random start
label_gender = Label(text="Gender: ")
gender_dropdown = ttk.Combobox(values=gender_options)
gender_dropdown.set("Random")
# Details Options
label_details_options = Label(text="Show Details", bg="lightblue")
show_details_dropdown = ttk.Combobox(values=show_details_options)
show_details_dropdown.set("One line")
label_stats_options = Label(text="Show Stats")
show_stats_dropdown = ttk.Combobox(values=show_stats_options)
show_stats_dropdown.set("One line")



# Career
label_career = Label(text="Career: ")
#input_career = Entry(width=12)
careers_dropdown = ttk.Combobox(values=career_options)
careers_dropdown.set("Random")
label_level = Label(text="Level: ")
input_level = Entry(width=3)
label_race = Label(text="Race:")
race_dropdown = ttk.Combobox(values=dropdown_races)
race_dropdown.set("Human")
label_magic = Label(text="Magic:")
magic_dropdown = ttk.Combobox(values=magic_options)
magic_dropdown.set(magic_options[0])
button_create = Button(text="Create Character", command=click_create_character)
button_update_character = Button(text="Update", command=click_update_character, state=DISABLED)
button_add_level = Button(text="Add Career", command=click_add_levels, state=DISABLED)
button_add_family = Button(text="Add Family", command=click_add_family, state=DISABLED)
# TODO potentially eventually replace with a dropdown for None, Physical, Mental or both
checked_mutations_state = IntVar()
checkbutton_mutations = Checkbutton(text="Mutant?", variable=checked_mutations_state)
button_add_mutation = Button(text="Add Mutation", command=click_add_mutation, state=DISABLED)

# Groups
label_group = Label(text="Group:")
groups_dropdown = ttk.Combobox(values=group_options)
groups_dropdown.set(choice(group_options))
button_group = Button(text="Create Group", command=click_create_group)
button_add_relationships = Button(text="Add Relationships", command=click_add_relationships, state=DISABLED)
button_update_group = Button(text="Update Group", command=click_update_group, state=DISABLED)
checked_show_relationships_state = IntVar()
checkbutton_show_relationships = Checkbutton(text="Show relationships?", variable=checked_show_relationships_state)
checked_show_relationships_state.set(1)

# Vessels
label_vessel = Label(text="Vessel:")
vessel_dropdown = ttk.Combobox(values=vessel_dropdown_items)
vessel_dropdown.set("Barge")  # this is a bit hacky as it relies on Barge being in the data
# checkbox for generate captain here
checked_captain_state = IntVar()
checkbutton_create_captain = Checkbutton(text="Create Captain?", variable=checked_captain_state)
checked_captain_state.set(1)

button_create_vessel = Button(text="Create Vessel", command=click_create_vessel)
button_update_vessel = Button(text="Update", command=click_update_vessel, state=DISABLED)

# Dreams

label_dreams = Label(text="Dreams (number): ")
input_number_dreams = Entry(width=3)
button_dreams = Button(text="Create Dreams", command=click_create_dreams)

# Inns

label_inns = Label(text="Inn Quality: ")
inn_quality_dropdown = ttk.Combobox(values=inn_quality_options)
inn_quality_dropdown.set("random")
label_inn_clientele = Label(text="Clientele:")
inn_occupied_dropdown = ttk.Combobox(values=inn_busy_states)
inn_occupied_dropdown.set("random")
checked_show_clientele_state = IntVar()
checkbutton_show_clientele = Checkbutton(text="Show Clientele?", variable=checked_show_clientele_state)
checked_show_clientele_state.set(1)
button_inns = Button(text="Create Inn", command=click_create_inn)
button_update_inn = Button(text="Update Inn", command=click_update_inn, state=DISABLED)

# Output
label_output = Label(text="Character output goes here", width=100, height=40, justify="left", anchor="n", pady=20)

# ----------------------------------------------------------- UI LAYOUT -----------------------------------------
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
detail_set_dropdown.grid(column=1, row=1) # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
label_gender.grid(column=2, row=1)
gender_dropdown.grid(column=3, row=1)
# Details Options
label_details_options.grid(column=4, row=1)
show_details_dropdown.grid(column=5, row=1)
label_stats_options.grid(column=6, row=1)
show_stats_dropdown.grid(column=7, row=1)


# Career
label_career.grid(column=0, row=2)
careers_dropdown.grid(column=1, row=2)
label_level.grid(column=2, row=2)
input_level.grid(column=3, row=2)
input_level.insert(0, "1")
label_race.grid(column=4, row=2)
race_dropdown.grid(column=5, row=2)
label_magic.grid(column=6, row=2)
magic_dropdown.grid(column=7, row=2)
checkbutton_mutations.grid(column=8, row=2)
button_create.grid(column=9, row=2)
button_update_character.grid(column=10, row=2)
button_add_level.grid(column=11, row=2)
button_add_family.grid(column=12, row=2)
button_add_mutation.grid(column=13, row=2)


# Groups
label_group.grid(column=0, row=3)
groups_dropdown.grid(column=1, row=3)
button_group.grid(column=2, row=3)
button_add_relationships.grid(column=3, row=3)
button_update_group.grid(column=4, row=3)
checkbutton_show_relationships.grid(column=5, row=3)


# Vessels
label_vessel.grid(column=0, row=5)
vessel_dropdown.grid(column=1, row=5)
checkbutton_create_captain.grid(column=2, row=5)
button_create_vessel.grid(column=3, row=5)
button_update_vessel.grid(column=4, row=5)

# Dreams
label_dreams.grid(column=0, row=7)
input_number_dreams.grid(column=1, row=7)
input_number_dreams.insert(0, "5")
button_dreams.grid(column=2, row=7)


# Inns
label_inns.grid(column=0, row=6)
inn_quality_dropdown.grid(column=1, row=6)
label_inn_clientele.grid(column=2, row=6)
inn_occupied_dropdown.grid(column=3, row=6)
checkbutton_show_clientele.grid(column=4, row=6)
button_inns.grid(column=5, row=6)
button_update_inn.grid(column=6, row=6)


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
# mutant_test = Mutation()
# print(mutant_test.get_output())



window.mainloop()