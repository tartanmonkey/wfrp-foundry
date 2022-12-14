from random import choice, randint
from tkinter import messagebox


def get_key_from_string(text, sep_start='[', sep_end=']'):
    """returns the text in a string found between the separators"""
    start = text.index(sep_start) + 1
    end = text.index(sep_end)
    key = ""
    for n in range(start, end):
        key += text[n]
    return key


def get_random_from_keyed_lists(key, dictionary):
    """Sent a dictionary of lists will return a random item from the list assigned to the key """
    if key in dictionary:
        return choice(dictionary[key])
    else:
        messagebox.showinfo(title="Oops!", message=f"ERROR - failed to find {key} in \n{dictionary}")
        return "ERROR"


def get_random_chance_entry(dictionary_list, chance_key):
    """returns a dictionary from a list by making a random 1 - 100 roll and consulting the chance_key in the dictionary
     which has form (higher than this value, lower than or equal to this value)"""
    roll = randint(1, 100)
    #print(f"random: {roll}")
    for item in dictionary_list:
        chance = item[chance_key]
        #print(f"{chance}")
        if roll > chance[0] and roll <= chance[1]:
            return item
    messagebox.showinfo(title="Oops!", message=f"ERROR - failed to find random entry with key{chance_key} in \n{dictionary_list}")


def get_random_key_value(key, list_dictionaries):
    """given a list of dictionaries returns the key from a random dictionary"""
    random_dictionary = choice(list_dictionaries)
    if key in random_dictionary:
        return random_dictionary[key]
    messagebox.showinfo(title="Oops!",
                        message=f"ERROR - failed to find key{key} in \n{list_dictionaries}")

def get_json_int(value, default):
    """For dealing with missing numerical values in json files as they will be empty strings if there is no value
    send the value from the json and a default value, it will return teh default if value is a string, otherwise returns teh value"""
    if type(value) == str:
        return default
    else:
        return value


def replace_chance_with_tuple(data, chance_key):
    """given a list of dictionaries with a chance_key, it creates a tuple in form (higher than this value, lower than or
     equal to this value)"""
    chance_low = 0
    for entry in data:
        chance_high = chance_low + entry[chance_key]
        chance = (chance_low, chance_high)
        chance_low = chance_high
        entry[chance_key] = chance
    return data


def convert_to_bool(string):
    """Converts a the strings TRUE & FALSE in any format to bool"""
    if string.upper() == "FALSE":
        return False
    return True


def roll_under(value, die=100):
    """Does a die roll (defaulting to %), returns True if less than or equal to value"""
    roll = randint(1, die)
    if roll <= value:
        return True
    return False


def convert_list_to_string(data):
    """turns a list of strings into a comma separated list"""
    string = ""
    for i in range(len(data)):
        string += data[i]
        if i != len(data) - 1:
            string += ", "
    return string


def split_into_lines(string, line_length):
    """Given a string and a line length in characters returns a list of lines with less than line_length"""
    split_lines = string
    if len(string) > line_length:
        words = string.split(' ')
        lines = [""]
        current_line = 0
        for word in words:
            if len(lines[current_line]) >= line_length:
                current_line += 1
                lines.append(word)
            else:
                lines[current_line] = lines[current_line] + word + " "
        split_lines = ""
        for line in lines:
            split_lines += line + "\n"

    return split_lines


def get_stripped_list(string):
    string_list = string.split(',')
    return [entry.strip() for entry in string_list]


def get_random_list_items(list_data, num_items):
    if num_items > len(list_data) - 1:
        messagebox.showinfo(title="Oops!", message=f"ERROR: list does not contain enough items!")
        return list_data
    else:
        temp_list = list_data.copy()
        random_items = []
        for n in range(num_items):
            item = choice(temp_list)
            random_items.append(item)
            temp_list.remove(item)
        return random_items


def get_random_item(string, divisor):
    """Splits a string into a list of items separated by the divisor and returns a random one"""
    items = string.split(divisor)
    return choice(items)


def get_dictionary_as_string(data, line_length, exclude_keys=[], do_not_split=[]):
    """creates a string with each key & value on a new line, will omit to print any keys in exclude_keys, and won't line split any values which are in do_not_split"""
    text = ""
    for key, value in data.items():
        if key not in exclude_keys:
            if key in do_not_split:
                text += f"{key}: {value}\n"
            else:
                text += f"{key}: {split_into_lines(value, line_length)}\n"
        else:
            text += f"{split_into_lines(value, line_length)}\n"
    return text


def cap_number(num, num_min, num_max):
    """Returns the min if number less than min, max if greater than max, otherwise returns the number"""
    if num < num_min:
        return num_min
    if num > num_max:
        return num_max
    return num


def get_first_word(text, divisor="("):
    """Returns the text before the divisor, removing trailing space"""
    words = text.split(divisor)
    return words[0].strip()


#  TODO: I wrote this then didn't use it, possibly remove or delete this comment 4-11-22
def get_chance_list(data, data_chance_key, chance_key, data_keys, keys):
    """For creating a list of dictionaries each of which has a chance tuple  (above_this, below_or_equal_this) and
    another set of values (keys) keyed to (data_keys) which are provided as lists"""
    if len(data_keys) != len(keys):
        messagebox.showinfo(title="Oops!", message=f"ERROR: create_chance_dictionary: data_keys {len(data_keys)} not equal to "
                                                   f"keys {len(keys)}, data_chance_key = {data_chance_key}, chance_key= {chance_key}")
        return
    else:
        chance_list = []
        chance_low = 0
        for entry in data:
            chance_high = chance_low + entry[data_chance_key]
            chance = (chance_low, chance_high)
            chance_low = chance_high
            chance_entry = {chance_key: chance}
            for i in range(len(data_keys)):
                chance_entry[keys[i]] = data_keys[i]
            chance_list.append(chance_entry)
        return chance_list
