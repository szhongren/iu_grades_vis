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

def handle_name(name_col):
    if name_col == 'INSTRUCTOR NAME':
        return 'LAST NAME","FIRST NAME","MIDDLE NAME'
    elif name_col == '"':
        return '","","'
    elif ',' in name_col[1:]:
        names = []
        parts = name_col.split(',')
        names.append(parts[0])
        i = parts[1].find(' ')
        names.append(parts[1][:i])
        names.append(parts[1][i + 1:])
        return '","'.join(names)
    else:
        names = []
        names.append(name_col[:-1])
        names.append(name_col[-1:])
        names.append('')
        return '","'.join(names)

def handle_line(line):
    count_quotes = 0
    i = 0
    while count_quotes < 19:
        if line[i] == '"':
            count_quotes += 1
        i += 1
    new_i = i
    while count_quotes < 20:
        if line[new_i] == '"':
            count_quotes += 1
        new_i += 1
    return line[:i].upper() + handle_name(line[i:new_i - 1].upper()) + line[new_i - 1:].upper()
    # return '"' + handle_name(line[i:new_i - 1].upper()) + line[new_i - 1:].upper()

def merge_tables(directory, out_file):
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
    merge_tables(os.path.join("data", "orig"), "merged.csv")
    # printHeaders(os.path.join("data", "orig"), "headers.csv")
