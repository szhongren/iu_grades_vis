import os
import csv
import requests

BASE_URL = "http://gradedistribution.registrar.indiana.edu/exportToSpreadsheet.php"
"""
term: ?&term[]=4168&c=desc&r=gradedist%20target=
dept: ?&dept=AAAD&c=desc&r=gradedist%20target=
course-subj: ?&subject=AAAD-A&c=desc&r=gradedist%20target=
class: ?&subject=AAAD-A&crse=100&c=desc&r=gradedist%20target=
prof: ?&instrname=ROSA,IRIS&c=desc&r=gradedist%20target=
"""

def get_chronological_name(term_name):
    return ' '.join(sorted(term_name.split(' ')))

def read_term_keys_to_dict(file):
    sem_keys = {}
    with open(file, "r") as handle:
        sem_keys_reader = csv.reader(handle)
        for row in sem_keys_reader:
            k = row[0]
            sem_keys[k] = row[1]
    return sem_keys

def download_term_table(directory, term, term_name):
    req_params = {
        "term[]": term,
        "dept": "",
        "subject": "",
        "crse": "",
        "instrname": "",
        "c": "desc",
        "r": "gradedist%20target="
    }
    print("Downloading grade data for " + term_name)
    with open(os.path.join(directory, term_name + ".csv"), 'wb') as handle:
        downloaded_csv = requests.get(BASE_URL, params=req_params, stream=True)
        if not downloaded_csv.ok:
            print("Error writing " + os.path.join(directory, term_name + ".csv"))

        for block in downloaded_csv.iter_content(1024):
            handle.write(block)

def download_all_term_tables(directory=os.path.join("data", "orig")):
    sem_keys = read_term_keys_to_dict("sem_keys.csv")
    for term_key, term_name in sem_keys.items():
        download_term_table(directory, term_key, get_chronological_name(term_name))

def read_table(directory, term_name):
    with open(os.path.join(directory, term_name + ".csv"), "r") as handle:
        table = csv.DictReader(handle)
        for row in table:
            print(row)

def handle_name(row):
    pos = 9
    col = row[pos]
    if col == 'INSTRUCTOR NAME':
        row[pos] = 'LAST NAME,FIRST NAME,MIDDLE NAME'
    elif ',' in col:
        names = []
        parts = col.split(',')
        i = parts[1].find(' ')
        names.append(parts[0])
        if i == -1:
            names.append(parts[1])
            names.append('')
        else:
            names.append(parts[1][:i])
            names.append(parts[1][i + 1:])
        row[pos] = ','.join(names)
    else:
        names = []
        names.append(col[:-1])
        names.append(col[-1:])
        names.append('')
        row[pos] = ','.join(names)

def handle_class(row):
    subj, course = 5, 6
    if row[subj] == 'SUBJECT' and row[course] == 'COURSE':
        return
    else:
        if row[course][0].isdigit():
            return
        row[subj] += '-' + row[course][0]
        row[course] = row[course][1:]

def handle_line(line):
    row = line.split('","')
    handle_class(row)
    handle_name(row)
    return ','.join(row).upper()[1:-3] + '\n'

def merge_and_normalize_tables(directory, out_file):
    with open(out_file, 'w') as handle:
        for (i, table) in enumerate(os.listdir(directory)):
            for (j, line) in enumerate(open(os.path.join(directory, table), 'r')):
                if line == "\n" or j == 0 and i != 0:
                    continue
                handle.write(handle_line(line))
    print("Done writing to " + out_file)

def print_headers(directory, out_file):
    with open(out_file, 'w') as handle:
        for table in os.listdir(directory):
            with open(os.path.join(directory, table), 'r') as table_file:
                handle.write(table + ',' + table_file.__next__())

if __name__ == "__main__":
    # download_all_term_tables()
    # readTable(os.path.join("data", "orig"), "2016 Fall")
    merge_and_normalize_tables(os.path.join("data", "orig"), "merged.csv")
    # printHeaders(os.path.join("data", "orig"), "headers.csv")
