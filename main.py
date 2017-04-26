import requests, csv, os

BASE_URL = "http://gradedistribution.registrar.indiana.edu/exportToSpreadsheet.php"
"""
term: http://gradedistribution.registrar.indiana.edu/exportToSpreadsheet.php?&term[]=4168&c=desc&r=gradedist%20target=
dept: http://gradedistribution.registrar.indiana.edu/exportToSpreadsheet.php?&dept=AAAD&c=desc&r=gradedist%20target=
course-subj: http://gradedistribution.registrar.indiana.edu/exportToSpreadsheet.php?&subject=AAAD-A&c=desc&r=gradedist%20target=
class: http://gradedistribution.registrar.indiana.edu/exportToSpreadsheet.php?&subject=AAAD-A&crse=100&c=desc&r=gradedist%20target=
prof: http://gradedistribution.registrar.indiana.edu/exportToSpreadsheet.php?&instrname=ROSA,IRIS&c=desc&r=gradedist%20target=
"""

def getChronologicalName(term_name):
    return ' '.join(sorted(term_name.split(' ')))

def readTermKeysToDict(file):
    sem_keys = {}
    with open(file, "r") as handle:
        sem_keys_reader = csv.reader(handle)
        for row in sem_keys_reader:
            k = row[0]
            sem_keys[k] = row[1]
    return sem_keys

def downloadTermTable(directory, term, term_name):
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
        csv = requests.get(BASE_URL, params=req_params, stream=True)
        if not csv.ok:
            print("Error writing " + os.path.join(directory, term_name + ".csv"))

        for block in csv.iter_content(1024):
            handle.write(block)

def downloadAllTermTables(directory=os.path.join("data", "orig")):
    sem_keys = readTermKeysToDict("sem_keys.csv")
    for term_key, term_name in sem_keys.items():
        downloadTermTable(directory, term_key, getChronologicalName(term_name))

def readTable(directory, term_name):
    with open(os.path.join(directory, term_name + ".csv"), "r") as handle:
        table = csv.DictReader(handle)
        for row in table:
            print(row)

def mergeTables(directory, out_file):
    with open(out_file, 'w') as handle:
        for (i, table) in enumerate(os.listdir(directory)):
            for (j, line) in enumerate(open(os.path.join(directory, table), 'r')):
                if line == "\n" or j == 0 and i != 0:
                    continue
                handle.write(line)
    print("Done writing to " + out_file)

def printHeaders(directory, out_file):
    with open(out_file, 'w') as handle:
        for table in os.listdir(directory):
            with open(os.path.join(directory, table), 'r') as table_file:
                handle.write(table + ',' + table_file.__next__())
# downloadAllTermTables()

# readTable(os.path.join("data", "orig"), "2016 Fall")
mergeTables(os.path.join("data", "orig"), "merged.csv")
# printHeaders(os.path.join("data", "orig"), "headers.csv")
