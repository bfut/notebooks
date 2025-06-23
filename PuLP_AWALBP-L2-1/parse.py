# parse.py
# Copyright (c) 2025 Benjamin Futász
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
"""
Parse and validate parameter files from https://doi.org/10.1080/00207543.2012.751514
"""

import json
import pathlib

def read_file_to_int_list_with_split(file_path):
    with open(file_path, 'r') as file:
        content = file.readlines()
    return [list(map(int, line.strip().split())) for line in content if line.strip()]

names = [
    "number_of_tasks",
    "number_of_workstations",
    "accessibility_window_L",
    "accessibility_window_R",
    "size_of_workpiece_horizontal",
    "distance_between_right_borders",
    "intermediate_time_between_stages",
    "elementary_step_length",
    "tasks",

    "workstation_tasks_",

    "task_processing_time",
    "distance_to_right_border_of_workpiece",
    # "upper_bound_number_of_forward_steps",
]

def convert_to_dict_and_validate(fp: pathlib.Path|str, names: dict, verbose: bool = False) -> dict:
    res = read_file_to_int_list_with_split(fp)

    number_of_tasks = res[0][0]
    number_of_workstations = res[1][0]
    must_equal_zero_tk = int((number_of_tasks*(number_of_tasks + 1))/2)
    must_equal_zero_ws = number_of_workstations

    data = {}
    for i, line in enumerate(res):
        if i < 9:
            if verbose: print(i, names[i])
            data[names[i]] = line
        elif i < 9 + number_of_workstations:
            if verbose: print(i, "elif", f"{names[9]}{i-8}")
            data[f"{names[9]}{i-8}"] = line  # 1-based indexes
            must_equal_zero_tk -= sum(line)
            must_equal_zero_ws -= 1
        else:
            if verbose: print(i, "else", names[i-number_of_workstations+1])
            data[names[i-number_of_workstations+1]] = line
    if verbose: print()

    # validation
    if len(data[names[2]]) != number_of_workstations or len(data[names[3]]) != number_of_workstations:
        raise ValueError(f"{str(fp)}: Expected {number_of_workstations} accessibility windows, but got {len(data[names[2]])} for L and {len(data[names[3]])} for R.")
    if must_equal_zero_tk != 0:
        raise ValueError(f"{str(fp)}: Expected {must_equal_zero_tk} tasks to be assigned, but got {must_equal_zero_tk} remaining.")
    if must_equal_zero_ws != 0:
        raise ValueError(f"{str(fp)}: Expected {number_of_tasks} lines for tasks, but got {must_equal_zero_ws} remaining.")
    for el in data[names[-1]]:
        if el < 0 or el > data[names[4]][0]:
            raise ValueError(f"{str(fp)}: Invalid distance to right border of workpiece: {el}. Must be between 0 and {data[names[4]]}.")
    return data


if __name__ == "__main__":
    # parameters
    SCRIPT_PATH = pathlib.Path(__file__).parent.resolve()
    folder = "test_instances"
    pex = "A_12_m_5_N_50_1.txt"

    # workload
    fp = SCRIPT_PATH / folder / pex
    data = convert_to_dict_and_validate(fp, names, verbose=True)
    for key, value in data.items():
        print(f"{key}: {value}, len: {len(value)}")

    print()
    print(json.dumps(data, indent=None, ensure_ascii=False,))
