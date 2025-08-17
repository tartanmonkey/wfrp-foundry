import utilities
import character_creator
from random import randint, choice


class FamilyMember:
    def __init__(self, is_adult, relative_gender, relative_race):
        self.relationship = ""
        self.age = 0  # note if i made teh default high could use it to sort whole family by age
        self.gender = choice(["male", "female"])
        self.name = character_creator.get_random_name(self.gender, relative_race, True)
        if is_adult:
            self.relationship = self.get_relationship(relative_gender)
        else:
            self.relationship = "Child"
            # TODO should consider Halfling or Dwarf here
            self.age = randint(1, 18)

    def get_relationship(self, relative_gender):
        if self.gender == relative_gender:
            if self.gender == "male":
                return "Brother"
            else:
                return "Sister"
        else:
            if relative_gender == "male":
                return "Wife"
            else:
                return "Husband"

    def is_sibling(self):
        return self.relationship == "Brother" or self.relationship == "Sister"

    def get_output(self):
        if self.relationship == "Child":
            return f"{self.name} ({self.age})"
        return f"{self.relationship} {self.name}"
