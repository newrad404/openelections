import csv
from django.conf import settings
from issues.models import Electorate

__author__ = 'stephen'

gsc_districts = {
    #'H&S': 'gsc-hs',
    'Medicine': 'gsc-med',
    'Engineer': 'gsc-eng',
    'EarthSci': 'gsc-earthsci',
    'Law': 'gsc-law',
    'Education': 'gsc-edu',
    'GSB': 'gsc-gsb',
    }
assu_pops = {
    '1- Undergraduate Student': ['undergrad'],
    '2 - Coterm': ['undergrad','graduate'],
    '3 - Graduate Student': ['graduate'],
    }
class_years = {
    '5 - Fifth year or more Senior': 'undergrad-5plus',
    '4 - Senior Class Affiliation': 'undergrad-5plus',
    '3 - Junior Class Affiliation': 'undergrad-4',
    '2 - Sophomore Class Affiliation': 'undergrad-3',
    '1 - Freshman Class Affiliation': 'undergrad-2',
    }

def elec(slug):
    if slug is None: return None
    return Electorate.objects.get(slug=slug)

def loadStudentDict():
        students = csv.DictReader(open(settings.STUDENT_CSV,'rU'))
        entries = {}

        for row in students:
            sunetid = row['SUNetID']
            student_entry = [None,None]
            groups = map(str.strip, row['Class Level'].split(','))
            for g in groups:
                if g in assu_pops:
                    student_entry[0] = map(elec, assu_pops[g])
                if g in class_years:
                    student_entry[1] = elec(class_years[g])
            entries[sunetid] = student_entry

        return entries