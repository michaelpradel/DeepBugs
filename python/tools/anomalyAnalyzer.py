import os
import sys
import argparse
import termios
import tty
import json
from collections import Counter

INSPECTED_FILE = 'inspected.txt'
INSPECTED_NOW_FILE = 'inspected_now.txt'
RANKED_WARNINGS = 'ranked.txt'
BLUE = '\033[94m'
DEFAULT = '\033[0m'

def readChar():
    attr = termios.tcgetattr( sys.stdin )
    tty.setraw( sys.stdin )
    d = sys.stdin.read(1)
    termios.tcsetattr( sys.stdin, termios.TCSADRAIN, attr )
    return d

class Anomaly(object):
    def __init__(self, score, src, details, is_bug="?", comment=""):
        self.score = score
        self.src = src
        self.details = details
        self.is_bug = is_bug
        self.comment = comment
        
        # check parsing
        self.src.split(' : ')[1]
        self.score.split(" : ")[1]
        
    def as_string(self):
        elements = [self.score, self.src]
        elements += self.details
        elements += [self.is_bug, self.comment]
        return " | ".join(elements)
    
    def search_in(self, anomalies): 
        for a in anomalies:
            if self.src == a.src and self.details == a.details:
                return a
        return None
    
    def src_details(self):
        file_name, linenos = self.src.split(' : ')
        s_lineno, e_lineno = linenos.split(' - ')
        return [file_name, linenos, s_lineno, e_lineno]
    
    def numeric_score(self):
        return float(self.score.split(" : ")[1])
    

def read_inspected():
    inspected_anomalies = []
    with open(INSPECTED_FILE, 'r') as f:
        for line in f:
            score, src, *details, is_bug, comment = line.split(' | ')
            inspected_anomalies.append(Anomaly(score, src, details, is_bug, comment))
    return inspected_anomalies

def read_x_to_calls(file):
    with open(file, 'r') as f:
        x_to_calls = json.load(f)
    return x_to_calls

def read_anomalies(anomalies_file):
    anomalies = []
    ctr = 0
    with open(args.anomalies_file, 'r') as f:
        for anomaly_string in f:
            try:
                ctr += 1
                anomaly_string = anomaly_string.lstrip().rstrip()
                score, src, *details = anomaly_string.split(' | ')
                anomaly = Anomaly(score, src, details)
                anomalies.append(anomaly)
            except ValueError:
                print("Value problem reading line "+str(ctr)+" -- will ignore it")
            except IndexError:
                print("Index problem reading line "+str(ctr)+" -- will ignore it")
    return anomalies

def density_normalized_score_rank_of_anomaly(anomaly, file_to_calls, file_to_warnings):
    file_name, *_ = anomaly.src_details()
    warning_density = file_to_warnings[file_name] / file_to_calls[file_name]
    return anomaly.numeric_score() / warning_density

def rank_anomalies_by_density_normalized_score(anomalies, file_to_calls):
    file_to_warnings = Counter()
    for a in anomalies:
        file_name, *_ = a.src_details()
        file_to_warnings[file_name] += 1
    anomalies.sort(key=lambda a: density_normalized_score_rank_of_anomaly(a, file_to_calls, file_to_warnings), reverse=True)

def callee_frequency_normalized_score_rank_of_anomaly(anomaly, callee_to_calls):
    callee = anomaly.details[0]
    frequency_of_callee = callee_to_calls[callee]
    return anomaly.numeric_score() * frequency_of_callee

def rank_anomalies_by_callee_frequency_normalized_score(anomalies, callee_to_calls):
    anomalies.sort(key=lambda a: callee_frequency_normalized_score_rank_of_anomaly(a, callee_to_calls), reverse=True)

def filter_by_score(anomalies, min_score):
    return list(filter(lambda a: a.numeric_score() > min_score, anomalies))

def cluster_by_callee(anomalies):
    callee_to_warnings = dict()
    for a in anomalies:
        callee = a.details[0]
        callee_to_warnings.setdefault(callee, []).append(a)
    for callee, warnings in callee_to_warnings.items():
        print(callee + ": " + str(len(warnings)))
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--inspected', default=None, type=str, dest='inspected_file_name', help='File with previously inspected warnings')
    parser.add_argument('--file_to_calls', default=None, type=str, dest='file_to_calls_file_name', help='File that maps file names to nb. of calls')
    parser.add_argument('--callee_to_calls', default=None, type=str, dest='callee_to_calls_file_name', help='File that maps callees to nb. of calls')
    parser.add_argument('--focus_callee', default=None, type=str, dest='focus_callee', help='Callee to focus on (skips all other warnings)')
    parser.add_argument('--excluded_callees', default=None, type=str, dest='excluded_callees', help='Callees to  skip (separated by |)')
    parser.add_argument('--min_score', default=0.99, type=float, dest='min_score', help='Minimum score of inspected anomalies (default: 0.99)')
    parser.add_argument('anomalies_file', action="store", help="File containing list of possible anomalies", type=str)
    args = parser.parse_args()

    if args.file_to_calls_file_name != None:
        file_to_calls = read_x_to_calls(args.file_to_calls_file_name)
        
    if args.callee_to_calls_file_name != None:
        callee_to_calls = read_x_to_calls(args.callee_to_calls_file_name)
        
    if args.excluded_callees != None:
        excluded_callees = set(args.excluded_callees.split("|"))

    if args.inspected_file_name != None:
        INSPECTED_FILE = args.inspected_file_name
    
    inspected_anomalies = read_inspected()
    
    inspected_callees = set() # inspect only one example per callee to speed up inspection
    for a in inspected_anomalies:
        callee = a.details[0]
        inspected_callees.add(callee)

    inspected_file = open(INSPECTED_FILE, 'a')
    inspected_now_file = open(INSPECTED_NOW_FILE, 'w')
    ranked_file = open(RANKED_WARNINGS, 'w')

    anomalies = read_anomalies(args.anomalies_file)
    if args.file_to_calls_file_name != None: # rank by score normalized by per-file warning density
        rank_anomalies_by_density_normalized_score(anomalies, file_to_calls)
        
    if args.callee_to_calls_file_name != None: # rank by score normalized by nb of calls per callee
        rank_anomalies_by_callee_frequency_normalized_score(anomalies, callee_to_calls)
    
    anomalies = filter_by_score(anomalies, args.min_score)
#     cluster_by_callee(anomalies)
#     sys.exit(0)
    
    # before actual inspection, write file with ranked anomalies (including any known classification+comments)
    for anomaly in anomalies:
        known_anomaly = anomaly.search_in(inspected_anomalies)
        if known_anomaly != None:
            ranked_file.write(known_anomaly.as_string() + "\n")
        else:
            ranked_file.write(anomaly.as_string() + "\n")
    ranked_file.flush()
    
    anomaly_no = 0     
    for anomaly in anomalies:
        anomaly_no += 1
        file_name, linenos, s_lineno, e_lineno = anomaly.src_details()
        
        # specific to swapped args:
        callee = anomaly.details[0]
        
        if args.focus_callee != None and not (callee == args.focus_callee): # focus on particular function for faster inspection
            continue
        
        if args.excluded_callees != None and callee in excluded_callees: # skip some callees for faster inspection
            continue

        # Check if we already inspected the anomaly
        known_anomaly = anomaly.search_in(inspected_anomalies)
        if known_anomaly != None:
            inspected_now_file.write(known_anomaly.as_string() + "\n")
            inspected_now_file.flush()
            continue

        # Inspect
        with open('/tmp/current_anomaly', 'w+') as tmp_f:
            tmp_f.write(anomaly.as_string() + "\n")

        cmd = "vim -o +{} '{}' /tmp/current_anomaly".format(s_lineno, file_name)
        os.system(cmd)
        print(BLUE + "\r  [+] Anomaly : {} : Is this a real anomaly? [y/n/q] ".format(anomaly_no), end='')
        sys.stdout.flush()
        inp = readChar()
        while inp not in ['y', 'n', 'q']:
            print(BLUE + "\r  [+] Anomaly : {} : Is this a real anomaly? [y/n/q] ".format(anomaly_no), end='')
            sys.stdout.flush()
            inp = readChar()

        print('\r' + inp)
        if inp == 'y' or inp == 'n':
            print(DEFAULT + "Comment : ", end='')
            anomaly.is_bug = inp
            anomaly.comment = input()
            inspected_file.write(anomaly.as_string() + "\n")
            inspected_file.flush()
            inspected_now_file.write(anomaly.as_string() + "\n")
            inspected_now_file.flush()
        
        inspected_callees.add(callee)
            
        if inp == 'q':
            break
         

