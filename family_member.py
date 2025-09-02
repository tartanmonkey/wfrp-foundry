import utilities
import character_creator
from random import randint, choice


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

        for x in range(0, num_children):
            child = FamilyMember("child", person.details["Gender"], person.race)
            family.append(child)

    return family

# ------------------------------------------------- CLASS ---------------------------------------------------------
class FamilyMember:
    def __init__(self, relationship, relative_gender, relative_race):
        self.relationship = relationship
        self.age = 0  # note if i made teh default high could use it to sort whole family by age
        self.gender = self.set_gender_and_relationship(relationship, relative_gender)
        self.name = character_creator.get_random_name(self.gender, relative_race, True)
        if self.relationship == "Child":
            # TODO should consider Halfling or Dwarf here
            self.age = randint(1, 18)

    def is_sibling(self):
        return self.relationship == "Brother" or self.relationship == "Sister"

    def is_parent(self):
        return self.relationship == "Mother" or self.relationship == "Father"

    def get_output(self):
        if self.relationship == "Child":
            return f"{self.name} ({self.age})"
        return f"{self.relationship} {self.name}"

    def set_gender_and_relationship(self, relationship, relative_gender):
        if relationship == "Mother":
            self.relationship = "Mother"
            return "female"
        if relationship == "Father":
            self.relationship = "Father"
            return "male"
        if relationship == "partner":
            if relative_gender == "female":
                self.relationship = "Husband"
                return "male"
            else:
                self.relationship = "Wife"
                return "female"
        if relationship == "sibling":
            gender = choice(["male", "female"])
            if gender == "male":
                self.relationship = "Brother"
            else:
                self.relationship = "Sister"
            return gender
        self.relationship = "Child"
        return choice(["male", "female"])
