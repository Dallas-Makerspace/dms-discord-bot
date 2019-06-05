import re
import os
import sys
import yaml
import random
import discord
import logging as log
from datetime import datetime

def load_yaml(yaml_file_name):
    with open(os.path.join(sys.path[0], yaml_file_name), "r", encoding="utf8") as yaml_file:
        return yaml.safe_load(yaml_file)

def paginate(text):
    pages = []
    lines = text.split("\n")
    page = ""
    for line in lines:
        if len(page + line + "\n") < 1024:
            page = page + line + "\n"
        else:
            pages.append(page)
            page = line + "\n"
    pages.append(page)
    return pages

def sentence_case(text):
    return ". ".join(i.capitalize() for i in text.split(". "))

def chance(percent):
    return random.randint(0, 99) < percent

def replace_ignore_case(text, find, replace):
    pattern = re.compile(find, re.IGNORECASE)
    return pattern.sub(replace, text)

def ascii_only(text):
    stripped = (c for c in text if 0 < ord(c) < 127)
    return ''.join(stripped)

def time_since(date_time):
    return (datetime.utcnow() - date_time)

def time_until(date_time):
    return (date_time - datetime.utcnow())

def date_time_from_str(timestamp):
    timestamp = re.sub('[^0-9]','', timestamp)[:14]
    return datetime.strptime(timestamp[:19], "%Y%m%d%H%M%S")

def seconds_since(then):
    return abs((datetime.utcnow() - then).total_seconds())

log.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s", level=log.INFO, stream=sys.stdout)
config = load_yaml("config.yaml")
strings = load_yaml("strings.yaml")
