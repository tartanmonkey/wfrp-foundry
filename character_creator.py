import json
from tkinter import messagebox
from random import randint, choice
from utilities import get_random_chance_entry

skills = {}
levels = {
    2: [{"chance": (0, 70), "level": 1}, {"chance": (70, 100), "level": 2}],
    3: [{"chance": (0, 60), "level": 1}, {"chance": (60, 85), "level": 2}, {"chance": (85, 100), "level": 3}],
    4: [{"chance": (0, 40), "level": 1}, {"chance": (40, 75), "level": 2}, {"chance": (75, 95), "level": 3}, {"chance": (95, 100), "level": 4}]
}

names = {
    "empire": {"male": [], "female": [], "surname": []}
}


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


def get_random_name(gender, region="empire"):
    if gender in names[region]:
        return f"{choice(names[region][gender])} {choice(names[region]['surname'])}"
    else:
        messagebox.showinfo(title="Oops!", message=f"Missing {gender} from {region}")


def test_data(characters, data_type="skills"):
    missing_data = ""
    for character in characters:
        for skill in character.skills:
            skill_key = get_skill_key(skill)
            if skill_key not in skills:
                missing_data += f"{character.career}: {skill}\n"
    with open("Output/missing_data.txt", "w") as data:
        data.write(missing_data)

# TODO Remove once new skill logic complete
def get_skill_value(skill_name, attributes):
    # print(f"skill name: {skill_name} * attributes: {attributes}")
    skill_key = get_skill_key(skill_name)
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


def get_skill_key(skill_name):
    words = skill_name.split("(")
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
        details += f"{data[randint(0, rand_cap)]['Detail']}.\n"
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
        # TODO set wounds
        self.wounds = 0
        self.skills = {}
        self.set_skills(levels_data[index]["Skills"])
        # TODO talents list
        self.talents = []
        self.set_talents(levels_data[index]["Talents"])
        # TODO trappings list
        self.trappings = []
        self.set_trappings(levels_data[index]["Trappings"])
        self.details = details

    def set_skills(self, skill_string):
        skill_list = skill_string.split(',')
        skills_stripped = [skill.strip() for skill in skill_list]
        # print(skill_list)
        # print(skills_stripped)
        # TODO set initial values
        for s in skills_stripped:
            self.skills[s] = 5#get_skill_value(s, self.attributes)

    def set_talents(self, talent_string):
        self.talents = talent_string.split(',')

    def set_trappings(self, trappings_string):
        self.trappings = trappings_string.split(',')

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
        output += get_list_output("talents", self.talents)
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

    def get_skill_total(self, skill_name):
        skill_key = get_skill_key(skill_name)
        if skill_key in skills:
            if skills[skill_key] in self.attributes:
                attribute = skills[skill_key]
                return self.attributes[attribute]["total"] + self.skills[skill_name]
            else:
                messagebox.showinfo(title="Oops!", message=f"Missing {skills[skill_name]}!")
        else:
            messagebox.showinfo(title="Oops!", message=f"Missing {skills[skill_name]}!")
        return 0
