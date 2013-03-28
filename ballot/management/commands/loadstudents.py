import re, csv, os
from django.core.management.base import LabelCommand
from openelections.ballot.models import Ballot
from issues.models import Electorate

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
    'Undergrad': ['undergrad'],
    'Coterm': ['undergrad','graduate'],
    'Grad': ['graduate'],
}

class_years = {
    'Senior': 'undergrad-5plus',
    'Junior': 'undergrad-4',
    'Sophomore': 'undergrad-3',
    'Freshman': 'undergrad-2',
}

def get_ballot(sunetid):
    b, created = Ballot.get_or_create_by_sunetid(sunetid)
    return b
def elec(slug):
    if slug is None: return None
    return Electorate.objects.get(slug=slug)

class Command(LabelCommand):
    def handle_label(self, label, **options):
        output = []
        
        students_path = os.path.join(label, 'students.csv')
        students = csv.DictReader(open(students_path,'rU'))
    
        for row in students:
            sunetid = row['SUNetID']
            b = get_ballot(sunetid)
            class_level = row['Class Level'].strip()
            if class_level in class_years:
                b.undergrad_class_year = elec(class_years[class_level])
                b.assu_populations = map(elec, assu_pops['Undergrad'])
            else:
                b.assu_populations = map(elec, assu_pops['Grad'])

            print "%s\t%s" % (sunetid, b)
            b.save()
