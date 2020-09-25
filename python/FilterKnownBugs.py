import argparse
import json
import subprocess
import sys
from os import listdir
from os.path import isfile, join


parser = argparse.ArgumentParser()
parser.add_argument(
    '--changes', help='JSON file with single-line code changes', required=True)

js_data_dir = "data/known_bugs/js_data/"
data_kinds = ["assignments", "swappedArgs", "binOps"]
js_data_dir_calls = "data/known_bugs/js_data_relevant_swapped_args/"
js_data_dir_bin_operators = "data/known_bugs/js_data_relevant_bin_operator/"
js_data_dir_bin_operands = "data/known_bugs/js_data_relevant_bin_operand/"
js_data_dir_assignments = "data/known_bugs/js_data_relevant_assignment/"


def invoke_cmd(cmd, cwd="."):
    try:
        out = subprocess.check_output(
            cmd.split(" "), cwd=cwd, stderr=subprocess.STDOUT)
        out = out.decode(sys.stdout.encoding)
    except subprocess.CalledProcessError as e:
        # handle non-zero exit codes
        out = e.output.decode(sys.stdout.encoding)
    return out


def get_parent_commit(repo_dir, commit):
    cmd = f"git log --pretty=%P -n 1 {commit}"
    out = invoke_cmd(cmd, repo_dir)
    return out.split("\n")[0]


def read_changes(changes_file):
    code_changes = []
    with open(changes_file) as fp:
        raw_changes = json.load(fp)
        for raw_change in raw_changes:
            repo_dir = raw_change["local_repo_path"]
            repo_dir = repo_dir.replace(
                "../results/top_JS_repos", "./data/top_JS_repos")
            file = repo_dir + "/" + raw_change["buggy_file_path"]
            commit = raw_change["commit_hash"]
            line = raw_change["fix_line"].split("-")[0]
            code_changes.append([repo_dir, commit, file, line])
    return code_changes


def extract_from_js(code_changes):
    file_pairs = []  # pairs of buggy and fixed file
    for repo_dir, commit, file, line in code_changes:
        try:
            for data_kind in data_kinds:
                # go to fixed commit
                subprocess.run(
                    f"git checkout -f {commit}".split(" "), cwd=repo_dir)
                # extract data from JS file
                subprocess.run(
                    f"node javascript/extractFromJS.js {data_kind} --files {file} --outfile tmp_data.json".split(" "))
                fixed_file = f"{js_data_dir}/{data_kind}_fixed_{commit}.json"
                subprocess.run(
                    f"mv tmp_data.json {fixed_file}".split(" "))

                # go to buggy commit
                parent_commit = get_parent_commit(repo_dir, commit)
                subprocess.run(
                    f"git checkout -f {parent_commit}".split(" "), cwd=repo_dir)
                # extract data from JS file
                subprocess.run(
                    f"node javascript/extractFromJS.js {data_kind} --files {file} --outfile tmp_data.json".split(" "))
                buggy_file = f"{js_data_dir}/{data_kind}_buggy_{commit}.json"
                subprocess.run(
                    f"mv tmp_data.json {buggy_file}".split(" "))

                file_pairs.append([buggy_file, fixed_file])
        except Exception:
            print(f"Something went wrong with commit {commit} - ignoring.")

    return file_pairs


def extract_commit_to_line(code_changes):
    result = {}
    for repo_dir, commit, file, line in code_changes:
        result[commit] = line
    return result


def get_line(js_data_item):
    return js_data_item["src"].split(" : ")[1].split(" - ")[0]


def is_relevant_change_swapped_args(buggy_candidate, fixed_candidate):
    if (buggy_candidate["base"] == fixed_candidate["base"]
            and buggy_candidate["callee"] == fixed_candidate["callee"]
            and len(buggy_candidate["arguments"]) == 2
            and len(fixed_candidate["arguments"]) == 2
            and buggy_candidate["arguments"][0] == fixed_candidate["arguments"][1]
            and buggy_candidate["arguments"][1] == fixed_candidate["arguments"][0]):
        print(
            f"Swapped arguments bug fix: {buggy_candidate['callee']}({buggy_candidate['arguments'][0]}, {buggy_candidate['callee'][1]}) --> {fixed_candidate['callee']}({fixed_candidate['arguments'][0]}, {fixed_candidate['callee'][1]})")
        return True
    return False


def is_relevant_change_bin_operator(buggy_candidate, fixed_candidate):
    if (buggy_candidate["left"] == fixed_candidate["left"]
            and buggy_candidate["right"] == fixed_candidate["right"]
            and buggy_candidate["leftType"] == fixed_candidate["leftType"]
            and buggy_candidate["rightType"] == fixed_candidate["rightType"]
            and buggy_candidate["op"] != fixed_candidate["op"]):
        print(
            f"Binary operator bug fix: {buggy_candidate['left']} {buggy_candidate['op']} {buggy_candidate['right']} --> {fixed_candidate['left']} {fixed_candidate['op']} {fixed_candidate['right']}")
        return True
    return False


def is_relevant_change_bin_operand(buggy_candidate, fixed_candidate):
    # left operand changes
    if (buggy_candidate["left"] != fixed_candidate["left"]
            and buggy_candidate["right"] == fixed_candidate["right"]
            and buggy_candidate["op"] == fixed_candidate["op"]):
        print(
            f"Binary operand bug fix: {buggy_candidate['left']} {buggy_candidate['op']} {buggy_candidate['right']} --> {fixed_candidate['left']} {fixed_candidate['op']} {fixed_candidate['right']}")
        return True
    # right operand changes
    elif (buggy_candidate["right"] != fixed_candidate["right"]
            and buggy_candidate["left"] == fixed_candidate["left"]
            and buggy_candidate["op"] == fixed_candidate["op"]):
        print(
            f"Binary operand bug fix: {buggy_candidate['left']} {buggy_candidate['op']} {buggy_candidate['right']} --> {fixed_candidate['left']} {fixed_candidate['op']} {fixed_candidate['right']}")
        return True
    return False


def is_relevant_change_assignment(buggy_candidate, fixed_candidate):
    if (buggy_candidate["lhs"] != fixed_candidate["lhs"]
            or buggy_candidate["rhs"] != fixed_candidate["rhs"]):
        print(
            f"Assignment bug fix: {buggy_candidate['lhs']} = {buggy_candidate['rhs']} --> {fixed_candidate['lhs']} = {fixed_candidate['rhs']}")
        return True
    return False


def find_relevant_changes(json_file_pairs, commit_to_line):
    print(f"{len(json_file_pairs)} pairs of candidate JSON file pairs")

    relevant_changes_swapped_args = []
    relevant_changes_bin_operator = []
    relevant_changes_bin_operand = []
    relevant_changes_assignment = []

    for buggy_file, fixed_file in json_file_pairs:
        with open(buggy_file) as fp:
            buggy_data = json.load(fp)
        with open(fixed_file) as fp:
            fixed_data = json.load(fp)

        data_kind, _, commit = buggy_file.split(
            "/")[-1].replace(".json", "").split("_")

        # filter candidates by line
        line = commit_to_line[commit]
        buggy_candidate = None
        for d in buggy_data:
            if get_line(d) == line and buggy_candidate is None:
                buggy_candidate = d
        fixed_candidate = None
        for d in fixed_data:
            if get_line(d) == line and fixed_candidate is None:
                fixed_candidate = d

        # filter candidates by whether they fit the bug pattern
        if buggy_candidate is not None and fixed_candidate is not None:
            if data_kind == "calls":
                if is_relevant_change_swapped_args(buggy_candidate, fixed_candidate):
                    relevant_changes_swapped_args.append(
                        [buggy_candidate, fixed_candidate, commit])
                    print(
                        f"Relevant swapped argument pair: {buggy_file} at line {line}")
            if data_kind == "binOps":
                if is_relevant_change_bin_operator(buggy_candidate, fixed_candidate):
                    relevant_changes_bin_operator.append(
                        [buggy_candidate, fixed_candidate, commit])
                    print(
                        f"Relevant binary operator pair: {buggy_file} at line {line}")
                if is_relevant_change_bin_operand(buggy_candidate, fixed_candidate):
                    relevant_changes_bin_operand.append(
                        [buggy_candidate, fixed_candidate, commit])
                    print(
                        f"Relevant binary operand pair: {buggy_file} at line {line}")
            if data_kind == "assignments":
                if is_relevant_change_assignment(buggy_candidate, fixed_candidate):
                    relevant_changes_assignment.append(
                        [buggy_candidate, fixed_candidate, commit])
                    print(
                        f"Relevant assignment pair: {buggy_file} at line {line}")

    print(
        f"Found {len(relevant_changes_swapped_args)} relevant changes for swapped args")
    write_to_dir(js_data_dir_calls, relevant_changes_swapped_args)
    print(
        f"Found {len(relevant_changes_bin_operator)} relevant changes for binary operators")
    write_to_dir(js_data_dir_bin_operators, relevant_changes_bin_operator)
    print(
        f"Found {len(relevant_changes_bin_operand)} relevant changes for binary operands")
    write_to_dir(js_data_dir_bin_operands, relevant_changes_bin_operand)
    print(
        f"Found {len(relevant_changes_assignment)} relevant changes for assignments")
    write_to_dir(js_data_dir_assignments, relevant_changes_assignment)


def find_json_file_pairs():
    result = []
    fixed_files = [f for f in listdir(js_data_dir) if isfile(
        join(js_data_dir, f)) and "fixed" in f]
    for fixed_file in fixed_files:
        if len([d for d in data_kinds if d in fixed_file]) == 0:
            continue

        buggy_file = fixed_file.replace("_fixed_", "_buggy_")
        if isfile(join(js_data_dir, buggy_file)):
            result.append([join(js_data_dir, buggy_file),
                           join(js_data_dir, fixed_file)])
    return result


def write_to_dir(dir, relevant_changes):
    for buggy, fixed, commit in relevant_changes:
        with open(join(dir, f"{commit}_buggy.json"), "w") as fp:
            json.dump([buggy], fp, indent=2)
        with open(join(dir, f"{commit}_fixed.json"), "w") as fp:
            json.dump([fixed], fp, indent=2)


if __name__ == "__main__":
    args = parser.parse_args()
    code_changes = read_changes(args.changes)

    # choose one of the following two:
    # json_file_pairs = extract_from_js(code_changes)
    json_file_pairs = find_json_file_pairs()

    commit_to_line = extract_commit_to_line(code_changes)
    find_relevant_changes(json_file_pairs, commit_to_line)
