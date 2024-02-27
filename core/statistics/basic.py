import os
import json
from core.settings import home

path_stat = f"{home}/statistics/data/main_stat.json"


def set_statistic(fild: str):
    with open(path_stat, "r+") as f:
        data = json.load(f)
        try:
            data[fild] += 1
        except KeyError:
            data[fild] = 1
        f.seek(0)
        json.dump(data, f)


def get_statistic() -> dict:
    with open(path_stat, "r") as f:
        data = json.load(f)
    return data


def clean_statistic():
    with open(path_stat, "r+") as f:
        data = json.load(f)
        for i in data.keys():
            data[i] = 0
        json.dump(data, f)

