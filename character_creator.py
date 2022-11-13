import json
import math
from tkinter import messagebox
from random import randint, choice
from utilities import get_random_chance_entry, get_stripped_list, get_random_list_items, get_key_from_string

skills = {}
levels = {
    2: [{"chance": (0, 70), "level": 1}, {"chance": (70, 100), "level": 2}],
    3: [{"chance": (0, 60), "level": 1}, {"chance": (60, 85), "level": 2}, {"chance": (85, 100), "level": 3}],
    4: [{"chance": (0, 40), "level": 1}, {"chance": (40, 75), "level": 2}, {"chance": (75, 95), "level": 3}, {"chance": (95, 100), "level": 4}]
}

names = {
    "empire": {"male": [], "female": [], "surname": []}
}

talents_random = []
talent_bonus = {}  # talent name: attribute

hand_weapons = ["Sword", "Axe", "Mace", "Studded Club"]

wealth_data = {
    "Brass": {"coin": "d", "rolls": 2},
    "Silver": {"coin": "s", "rolls": 1},
    "Gold": {"coin": "GC", "rolls": 0},
}

magic_colours = ["Beasts", "Death", "Fire", "Heavens", "Metal", "Life", "Light", "Shadow"]
gods = ["Manann", "Morr", "Myrmidia", "Ranald", "Rhya", "Shallya", "Sigmar", "Taal", "Ulric", "Verena"]
spells = {} # domain: [list of spells]
blessings = {} # god: [list of blessings]


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
    # print(get_random_name("female"))


def init_skills_data():
    global skills
    try:
        with open("Data/Skills_Data.json", "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Missing Skills data!")
    else:
        for entry in data:
            skills[entry["Skill"]] = entry["Attribute"]


def init_talents_data():
    global talents_random, talent_bonus
    try:
        with open("Data/Talents_Random.txt", "r") as data_file:
            talents_random = data_file.readlines()
            talents_random = [talent.strip() for talent in talents_random]
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


def get_random_name(gender, region="empire"):
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

# TODO Remove once new skill logic complete
def get_skill_value(skill_name, attributes):
    # print(f"skill name: {skill_name} * attributes: {attributes}")
    skill_key = extract_key(skill_name)
    print(skill_key)
    # TODO set only some skills defined by Level
    if skill_key in skills:
        if skills[skill_key] in attributes:
            attribute = skills[skill_key]
            return attributes[attribute]["total"] + 5  # this probably needs to take level or distinguish between set & add
        else:
            messagebox.showinfo(title="Oops!", message=f"Missing {skills[skill_name]}!")
    else:
        messagebox.showinfo(title="Oops!", message=f"Missing {skills[skill_name]}!")
    return 30


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


def create_character_details(gender, origin="", says=""):
    details = get_random_name(gender)
    try:
        with open("Data/Details_Data_GMS.json", "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Oops!", message="Missing Details_Data_GMS.json!")
    else:
        rand_cap = len(data) - 1
        details += f"{data[randint(0, rand_cap)]['Description']}, "
        details += f"{get_extra_detail(gender, data[randint(0, rand_cap)]['Detail'])}.\n"
        if len(origin) > 0:
            details += f"Origin: {origin}.\n"
        details += f"Trait: {data[randint(0, rand_cap)]['Trait']}\n"
        details += f"Motivation: {data[randint(0, rand_cap)]['Motivation']}\n"
        details += f"Ambition: {data[randint(0, rand_cap)]['Ambition']}\n"
        details += f"Quirk: {data[randint(0, rand_cap)]['Quirk']}\n"
        if len(says) > 0:
            details += f"Says: {says}\n"
        details += "\n"

    return details


def create_attribute(race="human"):
    roll_1 = randint(1, 10)
    roll_2 = randint(1, 10)
    return {"base": roll_1 + roll_2 + 20, "advances": 0, "total": roll_1 + roll_2 + 20}


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
# ---------------------------- CHARACTER CLASS------------------------------------------------------------- #


class GameCharacter:
    def __init__(self, career_name, level, levels_data, details=""):
        self.level = level
        self.career = career_name
        index = level -1
        self.path = levels_data[index]["Title"]
        self.status = levels_data[index]["Status"]
        path_data = levels_data[index]
        self.attributes = {
            "WS": create_attribute(),
            "BS": create_attribute(),
            "S": create_attribute(),
            "T": create_attribute(),
            "I": create_attribute(),
            "Agi": create_attribute(),
            "Dex": create_attribute(),
            "Int": create_attribute(),
            "WP": create_attribute(),
            "Fel": create_attribute(),
        }
        self.set_attributes(path_data)
        self.skills = {}
        self.set_skills(levels_data)
        self.magic = {}
        # talents list
        self.talents = self.set_talents(levels_data)
        # self.set_talents(levels_data[index]["Talents"])
        # set wounds
        self.wounds = self.set_wounds()
        # trappings list
        self.trappings = []
        self.set_trappings(levels_data[index]["Trappings"])
        self.details = details

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
            self.attributes[attribute]["advances"] = level_multiplier * 5 + randint(0, 5)
            self.attributes[attribute]["total"] = self.attributes[attribute]["base"] + self.attributes[attribute]["advances"]


    def get_output(self, output_type="ui"):
        output = self.details
        if output_type == "ui":
            output += f"{self.career} ({self.level} {self.path}) {self.status}\nWS  BS   S    T     I   Agi Dex Int WP Fel W"
            output += f"\n{self.attributes['WS']['total']}   {self.attributes['BS']['total']}   {self.attributes['S']['total']}  {self.attributes['T']['total']}"
            output += f"  {self.attributes['I']['total']}  {self.attributes['Agi']['total']}    {self.attributes['Dex']['total']}   {self.attributes['Int']['total']}"
            output += f"  {self.attributes['WP']['total']}  {self.attributes['Fel']['total']}  {self.wounds}"
        else:
            output += f"{self.career} ({self.path}) {self.status}\nWS  BS  S   T   I   Agi Dex Int  WP Fel  W"
            output += f"\n{self.attributes['WS']['total']}  {self.attributes['BS']['total']}  {self.attributes['S']['total']}  {self.attributes['T']['total']}"
            output += f"  {self.attributes['I']['total']}  {self.attributes['Agi']['total']}   {self.attributes['Dex']['total']}  {self.attributes['Int']['total']}"
            output += f"  {self.attributes['WP']['total']}  {self.attributes['Fel']['total']}  {self.wounds}"

        output += self.get_skills_output()
        output += self.get_talents_output()
        output += get_list_output("trappings", self.trappings)

        return output

    def get_skills_output(self):
        output = "\n-----SKILLS----------------\n"
        index = 0
        for skill, value in self.skills.items():
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
        if self.level == 1:
            skill_list = get_stripped_list(level_data[0]["Skills"])
            for skill in skill_list:
                self.skills[skill] = get_random_skill_value(1)
        else:
            for i in range(self.level):
                skill_list = get_stripped_list(level_data[i]["Skills"])
                for skill in skill_list:
                    if i == 0:
                        value = (self.level - 1) * 5
                    else:
                        num_rolls = self.level - i
                        value = get_random_skill_value(num_rolls)
                    self.skills[skill] = value

    def set_talents(self, levels_data):
        # get 3 unique random talents
        talents = get_random_list_items(talents_random, 3)
        # get one Career Talent/level - data needs prep
        for i in range(self.level):
            talents.append(self.get_career_talent(levels_data[i]["Talents"], talents))
        # apply and Talent Attribute bonuses
        for talent in talents:
            self.apply_talent_attribute_bonus(talent)
        return talents

    def get_career_talent(self, path_talents, my_talents):
        talent_list = path_talents.split(",")
        talent_list = [talent.strip() for talent in talent_list]
        # remove any talents i already have
        for t in talent_list:
            if t in my_talents:
                # print(f"already have Talent: {t} removing from random list")
                talent_list.remove(t)
        if len(talent_list) == 0:
            print("WARNING: already have all talents in list, returning none")
            return ""
        # TODO check for essential career talents, i.e. Pray, Petty Magic etc
        return choice(talent_list)

    def apply_talent_attribute_bonus(self, talent):
        talent_key = extract_key(talent)
        if talent_key in talent_bonus:
            self.increase_attribute(talent_bonus[talent_key], 5)
            #print(f"Applied talent bonus: {talent}; {talent_bonus[talent_key]}")

    def increase_attribute(self, attribute, amount):
        self.attributes[attribute]["base"] += amount
        self.attributes[attribute]["total"] = self.attributes[attribute]["base"] + self.attributes[attribute]["advances"]
        #print(f"Increased {attribute} to total {self.attributes[attribute]['total']}")

    def set_wounds(self):
        tb = get_attribute_bonus(self.attributes["T"]["total"])
        sb = get_attribute_bonus(self.attributes["S"]["total"])
        wpb = get_attribute_bonus(self.attributes["WP"]["total"])
        wounds = (2 * tb) + sb + wpb
        if "Hardy" in self.talents:
            #print("Increasing wounds as have Hardy Talent")
            wounds += tb
        return wounds
