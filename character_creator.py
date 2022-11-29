import json
import math
import pandas
from tkinter import messagebox
from random import randint, choice
from utilities import *

skills = {}
skill_groups = {}
SKILL_ANY_THRESHOLD = 10  # the threshold at which a new skill group is taken rather than increasing existing
levels = {
    2: [{"chance": (0, 70), "level": 1}, {"chance": (70, 100), "level": 2}],
    3: [{"chance": (0, 60), "level": 1}, {"chance": (60, 85), "level": 2}, {"chance": (85, 100), "level": 3}],
    4: [{"chance": (0, 40), "level": 1}, {"chance": (40, 75), "level": 2}, {"chance": (75, 95), "level": 3}, {"chance": (95, 100), "level": 4}]
}

names = {
    "empire": {"male": [], "female": [], "surname": []},
    "halfling": {"male": [], "female": [], "surname": []},
    "dwarf": {"male": [], "female": [], "surname": []},
    "high elf": {"male": [], "female": [], "surname": []},
    "wood elf": {"male": [], "female": [], "surname": []},
}

talents_random = []  # this is the human list which is read in then added to talents_race_random on init
talents_race_random = {
    "Human": [],
    "Dwarf": ["Resolute", "Strong-minded", "Relentless", "Read/Write"],
    "High Elf": ["Coolheaded", "Savvy", "Second Sight", "Sixth Sense"],
    "Wood Elf": ["Second Sight", "Read/Write", "Very Resilient", "Hardy"]
}
talent_bonus = {}  # talent name: attribute

hand_weapons = ["Sword", "Axe", "Mace", "Studded Club"]

wealth_data = {
    "Brass": {"coin": "d", "rolls": 2},
    "Silver": {"coin": "s", "rolls": 1},
    "Gold": {"coin": "GC", "rolls": 0},
}

magic_colours = ["Beasts", "Death", "Fire", "Heavens", "Metal", "Life", "Light", "Shadow"]
gods = ["Manann", "Morr", "Myrmidia", "Ranald", "Rhya", "Shallya", "Sigmar", "Taal", "Ulric", "Verena"]
spells = {}  # domain: [list of spells]
blessings = {}  # god: [list of blessings]
magic_talents = ["Petty Magic", "Arcane Magic (Arcane Lore)", "Bless (Any)", "Invoke (Any)", "Arcane Magic (Hedgecraft)"
    , "Arcane Magic (Heavens)", "Arcane Magic (Witchcraft)"]

attribute_overrides = {
    "Dwarf": {"WS": 30, "T": 30, "Agi": 10, "Dex": 30, "WP": 40, "Fel": 10},
    "Halfling": {"WS": 10, "BS": 30, "S": 10, "Dex": 30, "WP": 30, "Fel": 30},
    "High Elf": {"WS": 30, "BS": 30, "I": 40, "Agi": 30, "Dex": 30, "Int": 30, "WP": 30},
    "Wood Elf": {"WS": 30, "BS": 30, "I": 40, "Agi": 30, "Dex": 30, "Int": 30, "WP": 30},
}

random_race = [
    {"chance": (0, 90), "race": "Human"},
    {"chance": (90, 94), "race": "Halfling"},
    {"chance": (94, 98), "race": "Dwarf"},
    {"chance": (98, 99), "race": "High Elf"},
    {"chance": (99, 100), "race": "Wood Elf"}
]

race_data = {
    "Human": { "base_talents": [], "random_talents": "Human", "num_random_talents" : 3, "skills": [], "name_table": "empire"},
    "Dwarf": { "base_talents": ["Magic Resistance", "Night Vision", "Sturdy"], "random_talents": "Dwarf", "num_random_talents" : 1, "skills": [], "name_table": "dwarf"},
    "Halfling": { "base_talents": ["Acute Sense (Taste)", "Night Vision", "Resistance (Chaos)", "Small"], "random_talents": "Human", "num_random_talents" : 2, "skills": [], "name_table": "halfling"},
    "High Elf": { "base_talents": ["Acute Sense (Sight)", "Night Vision", "Read/Write"], "random_talents": "High Elf", "num_random_talents" : 1, "skills": [], "name_table": "high elf"},
    "Wood Elf": { "base_talents": ["Acute Sense (Sight)", "Night Vision", "Rover"], "random_talents": "Wood Elf", "num_random_talents" : 1, "skills": [], "name_table": "wood elf"},
}

details_data = {}  # a dictionary of lists keyed to detail type, using Column titles exactly as they are in the csv


def init_details():
    global details_data
    try:
        data = pandas.read_csv("Data/Details_Data_GMS.csv")
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Missing Details_Data_GMS.csv")
    else:
        for col in data.columns:
            details_data[col] = [item for item in data[col].tolist() if type(item) == str]
        # for key, value in details_data.items():
        #     print(f"{key}: {value}")


def init_magic_data():
    global spells, blessings
    try:
        with open("Data/Domain_Magic.json", "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Missing Domain_Magic.json!")
    else:
        for entry in data:
            spell_list = entry["Spells"].split(",")
            spell_list = [spell.strip() for spell in spell_list]
            spells[entry["Domain"]] = spell_list
            if len(entry["Blessings"]) > 0:
                blessings_list = entry["Blessings"].split(",")
                blessings_list = [blessing.strip() for blessing in blessings_list]
                blessings[entry["Domain"]] = blessings_list
    # print("Spells----------------------")
    # for key, entry in spells.items():
    #     print(f"{key} : {entry}")
    # print("Blessings----------------------")
    # for key, entry in blessings.items():
    #     print(f"{key} : {entry}")


def init_name_data():
    global names
    try:
        with open("Data/Names/Names_Data_Empire.json", "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Missing Names_Data_Empire.json!")
    else:
        for entry in data:
            names["empire"]["male"].append(entry["Male"])
            names["empire"]["female"].append(entry["Female"])

    with open("Data/Names/Data_Names_Empire_Surnames.txt", "r") as surnames:
        names["empire"]["surname"] = surnames.readlines()
        names["empire"]["surname"] = [surname.strip() for surname in names["empire"]["surname"]]

    non_human_data = pandas.read_csv("Data/Names/Names_Non-Human.csv")
    names["halfling"]["male"] = [item for item in non_human_data["Halfling Male"].tolist() if type(item) == str]
    names["halfling"]["female"] = [item for item in non_human_data["Halfling Female"].tolist() if type(item) == str]
    names["halfling"]["surname"] = [item for item in non_human_data["Halfling Surname"].tolist() if type(item) == str]
    names["dwarf"]["male"] = [item for item in non_human_data["Dwarf Male"].tolist() if type(item) == str]
    names["dwarf"]["female"] = [item for item in non_human_data["Dwarf Female"].tolist() if type(item) == str]
    names["dwarf"]["surname"] = [item for item in non_human_data["Dwarf Surname"].tolist() if type(item) == str]
    names["high elf"]["male"] = [item for item in non_human_data["Elf Forename"].tolist() if type(item) == str]
    names["high elf"]["female"] = names["high elf"]["male"]
    names["high elf"]["surname"] = [item for item in non_human_data["High Elf"].tolist() if type(item) == str]
    names["wood elf"]["male"] = names["high elf"]["male"]
    names["wood elf"]["female"] = names["high elf"]["male"]
    names["wood elf"]["surname"] = [item for item in non_human_data["Wood Elf"].tolist() if type(item) == str]

    # for item in names["wood elf"]["surname"]:
    #     print(item)
    #halflings = non_human_data["Halfling Male"].tolist()
    #print(halflings)

    # print(get_random_name("female"))


def init_skills_data():
    global skills, race_data
    try:
        with open("Data/Skills_Data.json", "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Missing Skills data!")
    else:
        for entry in data:
            skills[entry["Skill"]] = entry["Attribute"]
    try:
        data = pandas.read_csv("Data/Race_Skills.csv")
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Missing Race_Skills.csv")
    else:
        for col in data.columns:
            race_data[col]["skills"] = [item for item in data[col].tolist() if type(item) == str]
            # details_data[col] = [item for item in data[col].tolist() if type(item) == str]
    try:
        data = pandas.read_csv("Data/Skill_Groups.csv")
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Skill_Groups.csv")
    else:
        for col in data.columns:
            skill_groups[col] = [item for item in data[col].tolist() if type(item) == str]

    # for group, data in skill_groups.items():
    #     print(f"{group} : {data}")
    # for race, data in race_data.items():
    #     print(f"{race} skills: {data['skills']}")

def init_talents_data():
    global talents_random, talent_bonus
    try:
        with open("Data/Talents_Random.txt", "r") as data_file:
            talents_random = data_file.readlines()
            # add human talents to race talents
            talents_race_random["Human"] = [talent.strip() for talent in talents_random]
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Talents_Random data!")
    try:
        with open("Data/Talents_Attrubute_Bonus.json", "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Missing Skills data!")
    else:
        for entry in data:
            talent_bonus[entry["Talent"]] = entry["Attribute"]


def get_random_name(gender, race="Human"):
    region = race_data[race]["name_table"]
    if gender in names[region]:
        return f"{choice(names[region][gender])} {choice(names[region]['surname'])}"
    else:
        messagebox.showinfo(title="Oops!", message=f"Missing {gender} from {region}")


def test_data(characters, data_type="skills"):
    missing_data = ""
    if data_type == "skills":  # Note this is expecting actual character instances
        for character in characters:
            for skill in character.skills:
                skill_key = extract_key(skill)
                if skill_key not in skills:
                    missing_data += f"{character.career}: {skill}\n"
        with open("Output/missing_data.txt", "w") as data:
            data.write(missing_data)
    elif data_type == "talents":
        try:
            with open("Data/Talents_All_Keys.txt", "r") as data_file:
                talents_all_keys = data_file.readlines()
        except FileNotFoundError:
            messagebox.showinfo(title="Oops!", message="Talents_Random data!")
        else:
            talents_all_keys = [talent.strip() for talent in talents_all_keys]
            # print(talents_all_keys)
            for career, level_set in characters.items():
                for entry in level_set["level_data"]:
                    talent_list = entry["Talents"].split(",")
                    talent_list = [t.strip() for t in talent_list]
                    #print(talent_list)
                    for career_talent in talent_list:
                        talent_key = extract_key(career_talent)
                        if talent_key not in talents_all_keys:
                            missing_data += f"{career} {entry['Title']} missing: {talent_key}\n"
            with open("Output/missing_data.txt", "w") as data:
                data.write(missing_data)


def get_random_skill_value(num_rolls):
    value = 0
    for n in range(num_rolls):
        value += randint(0, 5)
    return value


def extract_key(string):
    words = string.split("(")
    return words[0].strip()


def get_attribute_value(value):
    if type(value) == str:
        return 0
    else:
        return value


def get_list_output(list_name, data):
    output = f"\n\n-----{list_name.upper()}----------------\n"
    for n in range(len(data)):
        if n != 0 and n % 3 == 0:
            output += "\n"
        output += f"{data[n]}, "
    return output


def get_random_level(max_level=4):
    if max_level == 1:
        return 1
    level_data = get_random_chance_entry(levels[max_level], "chance")
    return level_data["level"]


def create_character_details(gender, race, **extra_details):
    details = {}
    details["Name"] = get_random_name(gender, race)
    details["Description"] = f"{choice(details_data['Description'])}, "
    details["Description"] += f"{get_extra_detail(gender, choice(details_data['Detail']))}."
    if "origin" in extra_details:
        details["Origin"] = extra_details["origin"]
    details["Trait"] = choice(details_data["Trait"])
    details["Motivation"] = choice(details_data["Motivation"])
    details["Ambition"] = choice(details_data["Ambition"])
    details["Quirk"] = choice(details_data["Quirk"])
    details[choice(["Likes", "Dislikes"])] = choice(details_data["Opinions"])
    if "chat" in extra_details:
        details["Chat"] = extra_details["chat"]

    return details

def create_attribute(attribute, race="Human"):
    roll_1 = randint(1, 10)
    roll_2 = randint(1, 10)
    bonus = 20
    if race in attribute_overrides:
        if attribute in attribute_overrides[race]:
            bonus = attribute_overrides[race][attribute]
    return {"base": roll_1 + roll_2 + bonus, "advances": 0, "total": roll_1 + roll_2 + 20}


def get_attribute_bonus(attribute):
    return math.floor(attribute / 10)


def get_extra_detail(gender, detail):
    if "/" in detail:
        options = detail.split("/")
        if gender == "male":
            return options[0]
        else:
            return options[1]
    return detail


def get_magic_talent(talents):
    for talent in talents:
        if talent in magic_talents:
            return talent
    return "None"


def get_number_of_spells(magic_type, level):
    # work out number of spells based on type & level
    if magic_type == "Petty":
        return level + 2
    if magic_type == "Arcane Magic":
        return level + randint(0, 2)
    return level


def is_valid_magic(magic):
    if magic == "None":
        return True
    if magic in spells:
        return True
    if magic in blessings:
        return True
    return False


def get_random_race():
    return get_random_chance_entry(random_race, "chance")["race"]


def get_skill_from_group(skill_group, exclude):
    group_list = [item for item in skill_groups[skill_group] if item not in exclude]
    group_item = choice(group_list)
    return f"{skill_group} ({group_item})"

# ---------------------------- CHARACTER CLASS------------------------------------------------------------- #


class GameCharacter:
    def __init__(self, career_name, level, levels_data, magic_domain, race, details={}):
        self.level = level
        self.career = career_name
        self.race = race
        index = level -1
        self.path = levels_data[index]["Title"]
        self.status = levels_data[index]["Status"]
        path_data = levels_data[index]
        self.attributes = {
            "WS": create_attribute("WS", self.race),
            "BS": create_attribute("BS", self.race),
            "S": create_attribute("S", self.race),
            "T": create_attribute("T", self.race),
            "I": create_attribute("I", self.race),
            "Agi": create_attribute("Agi", self.race),
            "Dex": create_attribute("Dex", self.race),
            "Int": create_attribute("Int", self.race),
            "WP": create_attribute("WP", self.race),
            "Fel": create_attribute("Fel", self.race),
        }
        self.set_attributes(path_data)
        self.skills = {}
        self.set_skills(levels_data)
        self.magic = {}  # talent key: specific domain
        self.spells = {}  # Domain: spell list
        # talents list
        self.talents = self.set_talents(levels_data, magic_domain)
        # self.set_talents(levels_data[index]["Talents"])
        if len(self.magic) > 0:
            self.set_spells()
        # set wounds
        self.wounds = self.set_wounds()
        # trappings list
        self.trappings = []
        self.set_trappings(levels_data[index]["Trappings"])
        self.details = details
        # for attribute, value in self.attributes.items():
        #     print(f"{attribute} advances: {value['advances']}")

    def set_talents(self, talent_string):
        self.talents = talent_string.split(',')

    def set_trappings(self, trappings_string):
        self.trappings = trappings_string.split(',')
        self.trappings = [item.strip() for item in self.trappings]
        for i in range(len(self.trappings)):
            if self.trappings[i] == "Hand Weapon":
                # replace hand weapon if it exists
                self.trappings[i] = choice(hand_weapons)
            elif "[" in self.trappings[i]:
                # replace options with one
                item = get_key_from_string(self.trappings[i], '[', ']')
                item = item.split('/')
                self.trappings[i] = choice(item)
        # now add money
        self.trappings.append(self.get_money())

    def get_money(self):
        wealth = self.status.split(" ")
        multiplier = int(wealth[1])
        money = 0
        rolls = wealth_data[wealth[0]]["rolls"] * multiplier
        for c in range(rolls):
            money += randint(1, 10)
        if money == 0:
            return f"{multiplier}GC"
        else:
            return f"{money}{wealth_data[wealth[0]]['coin']}"


    def set_details(self, details):
        self.details = details

    def set_attributes(self, level_data):
        for attribute, value in self.attributes.items():
            level_multiplier = get_attribute_value(level_data[attribute])
            if level_multiplier > 0:
                level_multiplier -= 1
                if level_multiplier < 0:
                    level_multiplier = 0
                self.attributes[attribute]["advances"] = level_multiplier * 5 + randint(0, 5)
            self.attributes[attribute]["total"] = self.attributes[attribute]["base"] + self.attributes[attribute]["advances"]

    def get_output(self, output_type="ui"):
        output = f"{self.career}: {get_dictionary_as_string(self.details, 50, ['Name'])}\n"
        if output_type == "ui":
            output += f"{self.get_title_output()}\nWS  BS   S    T     I   Agi Dex Int WP Fel W"
            output += f"\n{self.attributes['WS']['total']}   {self.attributes['BS']['total']}   {self.attributes['S']['total']}  {self.attributes['T']['total']}"
            output += f"  {self.attributes['I']['total']}  {self.attributes['Agi']['total']}    {self.attributes['Dex']['total']}   {self.attributes['Int']['total']}"
            output += f"  {self.attributes['WP']['total']}  {self.attributes['Fel']['total']}  {self.wounds}"
        else:
            output += f"{self.get_title_output()}\nWS  BS  S   T   I   Agi Dex Int  WP Fel  W"
            output += f"\n{self.attributes['WS']['total']}  {self.attributes['BS']['total']}  {self.attributes['S']['total']}  {self.attributes['T']['total']}"
            output += f"  {self.attributes['I']['total']}  {self.attributes['Agi']['total']}   {self.attributes['Dex']['total']}  {self.attributes['Int']['total']}"
            output += f"  {self.attributes['WP']['total']}  {self.attributes['Fel']['total']}  {self.wounds}"

        output += self.get_skills_output()
        output += self.get_talents_output()
        output += get_list_output("trappings", self.trappings)
        output += self.get_spells_output()

        return output

    def get_skills_output(self):
        # add combat & magic skills first
        ordered_skills = {key: value for key, value in self.skills.items() if "Melee" in key or "Ranged" in key or "Dodge" in key or "Channelling" in key or "Language (Magick)" in key or "Pray" in key}
        for skill, value in self.skills.items():
            if skill not in ordered_skills:
                ordered_skills[skill] = value
        output = "\n-----SKILLS----------------\n"
        index = 0
        for skill, value in ordered_skills.items():
            if index != 0 and index % 3 == 0:
                output += "\n"
            output += f"{skill}: {self.get_skill_total(skill)}, " #call to get skill total here
            index += 1
        return output

    def get_talents_output(self):
        output = "\n-----TALENTS---------------\n"
        for i in range(len(self.talents)):
            if i != 0 and i % 4 == 0:
                output += "\n"
            output += f"{self.talents[i]}, "
        return output

    def get_skill_total(self, skill_name):
        skill_key = extract_key(skill_name)
        if skill_key in skills:
            if skills[skill_key] in self.attributes:
                attribute = skills[skill_key]
                return self.attributes[attribute]["total"] + self.skills[skill_name]
            else:
                messagebox.showinfo(title="Oops!", message=f"Missing {skills[skill_name]}!")
        else:
            messagebox.showinfo(title="Oops!", message=f"Missing {skills[skill_name]}!")
        return 0

    def set_skills(self, level_data):
        # add race skills
        race_skills = get_random_list_items(race_data[self.race]["skills"], 4)
        # TODO replace Any if race_skills contains
        # note in the rules it should actually be 3 at 5 and 3 at 3, instead I'm adding just 4 at 4
        for skill in race_skills:
            #self.skills[skill] = 4
            self.advance_skill(skill, 4)
        print(f"--- {self.career} - Race Skills: {self.skills} ------------")
        if self.level == 1:
            skill_list = get_stripped_list(level_data[0]["Skills"])
            for skill in skill_list:
                self.advance_skill(skill, get_random_skill_value(1))
        else:
            for i in range(self.level):
                skill_list = get_stripped_list(level_data[i]["Skills"])
                for skill in skill_list:
                    if i == 0:
                        value = (self.level - 1) * 5
                    else:
                        num_rolls = self.level - i
                        value = get_random_skill_value(num_rolls)
                    # self.skills[skill] = value
                    self.advance_skill(skill, value)

    def advance_skill(self, skill, value):
        global skill_groups
        if skill in self.skills:
            self.skills[skill] += value
            print(f"Increasing Previous skill: {skill} by {value} to {self.skills[skill]}")
        else:
            # check if 'Any'
            if "Any" in skill:
                skill_group = get_first_word(skill)
                print(f"Got skill group: {skill_group}")
                 # check if already have this key and only get a new one if advances high enough
                skill_groups_known = []
                for key, entry in self.skills.items():
                    # check keys for skill_group and store if so
                    if skill_group in key:
                        skill_groups_known.append(key) # note this is the whole name
                # iterate through know skills to decide whether to add a new group or increase existing
                print(f"Skills Groups Known: {skill_groups_known}")
                for known in skill_groups_known:
                    if self.skills[known] < SKILL_ANY_THRESHOLD:
                        print(f"increase {known} as its only {self.skills[known]}")
                        self.skills[known] += value
                        return
                # get new skill group
                if skill_group in skill_groups:
                    # add a random item from skill_group, excluding any I currently have
                    exclude = [get_key_from_string(item, "(", ")") for item in skill_groups_known]
                    self.skills[get_skill_from_group(skill_group, exclude)] = value
                else:
                    print(f"Did not find {skill_group} in skill_groups, so adding {skill}")
                     # simply add the whole skill name (with Any included)
                    self.skills[skill] = value
            elif "(" in skill and "/" in skill:
                # check for options and use one if present
                choices = get_key_from_string(skill, "(", ")")
                new_skill = f"{get_first_word(skill)} ({get_random_item(choices, '/')})"
                self.skills[new_skill] = value
            else:
                # otherwise set as usual
                self.skills[skill] = value

    def set_talents(self, levels_data, magic_domain):
        # look up race for base set
        base_set = race_data[self.race]["base_talents"]
        # get random set based on race
        talent_list_name = race_data[self.race]["random_talents"]
        race_talents = talents_race_random[talent_list_name].copy()
        # make new set from random set, removing any which are in base set
        for talent in base_set:
            if talent in race_talents:
                race_talents.remove(talent)

        # add random talents, using race list & race number
        num_race_talents = race_data[self.race]["num_random_talents"]
        talents = get_random_list_items(race_talents, num_race_talents)
        for talent in base_set:
            talents.append(talent)

        # get one Career Talent/level - data needs prep
        for i in range(self.level):
            talents.append(self.get_career_talent(levels_data[i]["Talents"], talents, magic_domain))
        # apply and Talent Attribute bonuses
        for talent in talents:
            self.apply_talent_attribute_bonus(talent)
        return talents

    def get_career_talent(self, path_talents, my_talents, magic_domain):
        # prep list of current career level talents
        talent_list = path_talents.split(",")
        talent_list = [talent.strip() for talent in talent_list]
        # remove any talents i already have
        for t in talent_list:
            if t in my_talents:
                # print(f"already have Talent: {t} removing from random list")
                talent_list.remove(t)
        if len(talent_list) == 0:
            print("WARNING: already have all talents in list, returning none")
        # check for essential career talents, i.e. Pray, Petty Magic etc
        magic_talent = get_magic_talent(talent_list)
        if magic_talent == "None":
            return choice(talent_list)
        else:
            self.set_magic_talent(magic_talent, magic_domain)
            return magic_talent

    def apply_talent_attribute_bonus(self, talent):
        talent_key = extract_key(talent)
        if talent_key in talent_bonus:
            self.increase_attribute(talent_bonus[talent_key], 5)
            # print(f"Applied talent bonus: {talent}; {talent_bonus[talent_key]}")

    def increase_attribute(self, attribute, amount):
        self.attributes[attribute]["base"] += amount
        self.attributes[attribute]["total"] = self.attributes[attribute]["base"] + self.attributes[attribute]["advances"]
        # print(f"Increased {attribute} to total {self.attributes[attribute]['total']}")

    def set_wounds(self):
        tb = get_attribute_bonus(self.attributes["T"]["total"])
        sb = get_attribute_bonus(self.attributes["S"]["total"])
        wpb = get_attribute_bonus(self.attributes["WP"]["total"])
        if self.race == "Halfling":
            sb = 0
        wounds = (2 * tb) + sb + wpb
        if "Hardy" in self.talents:
            # print("Increasing wounds as have Hardy Talent")
            wounds += tb
        return wounds

    def set_magic_talent(self, talent, user_input):
        print(f"Got magic talent: {talent}")
        talent_key = extract_key(talent)
        # if petty magic don't add a domain
        if talent_key == "Petty Magic":
            self.magic["Petty"] = ""
        else:
            if user_input != "None":
                # TODO add safety here?
                self.magic[talent_key] = user_input
            else:
                self.magic[talent_key] = self.set_magic_domain(talent, talent_key)
        # print(f"{self.magic}")

    def get_magic_domain(self):
        """Returns 'None' if there is no domain value in any of the self.magic items """
        for magic, domain in self.magic.items():
            if domain != "":
                return domain
        return "None"

    def set_magic_domain(self, talent_string, talent_key):
        for magic, domain in self.magic.items():
            if domain != "":
                return domain
        domain = self.get_magic_domain()
        if domain != "None":
            return domain
        # now get domain from talent_string as we don't already have one
        my_domain = talent_string.split("(")
        my_domain[1] = my_domain[1].replace(")", "")
        if talent_key == "Arcane Magic":
            if my_domain[1] != "Arcane Lore":
                return my_domain[1]
            return choice(magic_colours)
        else:
            return choice(gods)

    def set_spells(self):
        global spells
        for key, domain in self.magic.items():
            if key == "Bless":
                self.spells["Bless"] = blessings[domain]
            else:
                spell_domain = domain
                if len(domain) == 0:
                    spell_domain = "Petty"
                num_spells = get_number_of_spells(key, self.level)
                if key == "Arcane Magic":
                    # work out number of Arcane spells & number of colour spells
                    num_arcane = math.ceil(num_spells/2)
                    num_spells = cap_number(num_spells - num_arcane, 1, 100)
                    arcane_list = get_random_list_items(spells["Arcane"], num_arcane)
                    self.spells["Arcane"] = arcane_list
                spell_list = get_random_list_items(spells[spell_domain], num_spells)
                self.spells[spell_domain] = spell_list
        # for magic, my_spells in self.spells.items():
        #     print(f"{magic} : {my_spells}")

    def get_spells_output(self):
        output = ""
        if len(self.spells) > 0:
            output += "\n\n-----SPELLS---------------"
            for domain, spell_list in self.spells.items():
                output += f"\n------  {domain}  ------------\n"
                my_spells = convert_list_to_string(spell_list)
                my_spells = split_into_lines(my_spells, 50)
                output += my_spells
        return output

    def get_title_output(self):
        domain = self.get_magic_domain()
        if domain != "None":
            return f"{self.career} {domain} ({self.level} {self.path}) {self.status} - {self.race}"
        return f"{self.career} ({self.level} {self.path}) {self.status} - {self.race}"


