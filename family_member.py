import utilities
import character_creator
from random import randint, choice


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
        self.details = ""

    def is_sibling(self):
        return self.relationship == "Brother" or self.relationship == "Sister"

    def is_parent(self):
        return self.relationship == "Mother" or self.relationship == "Father"

    def get_output(self):
        if self.relationship == "Child":
            return f"{self.name} ({self.age})"
        return f"\n{self.details}"

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

    def set_details(self, details):
        self.details = details
