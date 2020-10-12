import argparse
from os import listdir
from os.path import isfile, join
import numpy as np
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser()
parser.add_argument(
    '--warnings', help='Files with warnings reported by BugFind.py', nargs="+")


bug_patterns = ["SwappedArgs", "BinOperator", "IncorrectBinaryOperand", "IncorrectAssignment"]
embeddings_to_color = {
    "FT_orig": "red",
    "counterfitted2": "green"
}
embeddings = embeddings_to_color.keys()

ground_truth_dir_prefix = "./data/known_bugs/js_data_relevant_"
plot_dir = "./data/known_bugs/plots"


def find_warning_files(warning_files, bug_pattern, embedding):
    buggy_file = None
    fixed_file = None
    for f in warning_files:
        if bug_pattern in f and embedding in f:
            if "_buggy_" in f:
                assert buggy_file == None
                buggy_file = f
            if "_fixed_" in f:
                assert fixed_file == None
                fixed_file = f
    assert buggy_file is not None and fixed_file is not None
    return buggy_file, fixed_file


def read_warnings(warning_file):
    print(f"Reading warnings from {warning_file}")
    probabs = []
    with open(warning_file) as fp:
        lines = fp.readlines()
    for line in lines:
        if line.startswith("Prediction : "):
            probab = float(line.split(" | ")[0].split(" : ")[1])
            probabs.append(probab)
    return probabs


def read_ground_truth(bug_pattern):
    ground_truth_dir = f"{ground_truth_dir_prefix}{bug_pattern}"
    files = [f for f in listdir(ground_truth_dir)
             if isfile(join(ground_truth_dir, f))]
    nb_buggy = len([f for f in files if "_buggy.json" in f])
    nb_fixed = len([f for f in files if "_fixed.json" in f])
    return nb_buggy, nb_fixed


def compute_precision_recall(nb_buggy, nb_fixed, buggy_warnings_probabs, fixed_warnings_probabs):
    threshold_to_precision_recall_bugs = {}
    print(f"Buggy warnings probabs: {buggy_warnings_probabs}")
    print(f"Fixed warnings probabs: {fixed_warnings_probabs}")
    for t in np.arange(0.5, 1, 0.05):
        all_warnings = 0
        correct_warnings = 0
        for p in buggy_warnings_probabs:
            if p >= t:
                all_warnings += 1
                correct_warnings += 1
        for p in fixed_warnings_probabs:
            if p >= t:
                all_warnings += 1

        precision = correct_warnings / all_warnings if all_warnings > 0 else 0
        recall = correct_warnings / nb_buggy

        print(f"At t={t}, {correct_warnings}/{all_warnings} warnings are correct; p={round(precision, 2)}, r={round(recall, 2)}")

        threshold_to_precision_recall_bugs[t] = [precision, recall, nb_buggy]

    return threshold_to_precision_recall_bugs


def plot_precision_recall(embedding_to_results, bug_pattern):
    nb_bugs = -1
    for embedding, threshold_to_precision_recall_bugs in embedding_to_results.items():
        thresholds = []
        precisions = []
        recalls = []
        for t, prb in threshold_to_precision_recall_bugs.items():
            thresholds.append(t)
            precisions.append(prb[0])
            recalls.append(prb[1])
            nb_bugs = prb[2]

        plt.plot(thresholds, precisions,
                 label=f"Precision of {embedding}", color=embeddings_to_color[embedding])
        plt.plot(thresholds, recalls, label=f"Recall of {embedding}",
                 linestyle="dashed", color=embeddings_to_color[embedding])

    plt.legend()
    plt.xlabel("Threshold for reporting bugs")
    plt.ylabel("Precision and recall")
    plt.title(f"{bug_pattern} ({nb_bugs} bugs)")
    plt.tight_layout()
    out_filename = f"{plot_dir}/precision_recall_{bug_pattern}.png"
    plt.savefig(out_filename)
    plt.close()


if __name__ == "__main__":
    args = parser.parse_args()
    warning_files = args.warnings
    for bug_pattern in bug_patterns:
        embedding_to_results = {}
        for embedding in embeddings:
            print(f"\n== {embedding}: ==")
            buggy_warning_file, fixed_warning_file = find_warning_files(
                warning_files, bug_pattern, embedding)
            buggy_warnings = read_warnings(buggy_warning_file)
            fixed_warnings = read_warnings(fixed_warning_file)
            nb_buggy, nb_fixed = read_ground_truth(bug_pattern)
            threshold_to_precision_recall_bugs = compute_precision_recall(
                nb_buggy, nb_fixed, buggy_warnings, fixed_warnings)
            embedding_to_results[embedding] = threshold_to_precision_recall_bugs
        plot_precision_recall(embedding_to_results, bug_pattern)
