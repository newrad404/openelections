import csv
import datetime
from ballot.models import Ballot
from openelections.issues.models import Issue
from openelections.ballot.models import VoteRecord
from django.core.management.base import LabelCommand


class Command(LabelCommand):
    def handle_label(self, label, **options):
        #self.getTimeSeriesData()
        self.getExecSlateData()

    def getExecSlateData(self):
        print "---- STEWART ----"
        self.getTimeSeriesData("assu")
        print "---- ZIMBROFF ----"
        self.getTimeSeriesData("zimbroff-wagstaff")

    def getTimeSeriesData(self,slateName=None):
        students = getStudentDict()

        starttime = datetime.datetime(2012,4,12)
        granularity = datetime.timedelta(minutes=2)
        endtime = datetime.datetime(2012,4,14)
        currenttime = starttime

        slate = None
        if slateName:
            slate = Issue.objects.get(slug=slateName)
            print slate

        print "Time\tTotal vote entries\tUndergrad vote entries\tGrad vote entries\tCoterm vote entries\tFrosh vote entries\tSophomore votes\tJunior vote entries\tSenior vote entries\tInvalid vote entries"

        total_votes = 0
        frosh_votes = 0
        soph_votes = 0
        jun_votes = 0
        sen_votes = 0
        grad_votes = 0
        invalid_votes = 0
        coterm_votes = 0

        firstTime = True
        considered = set()

        while currenttime < endtime:
            if not firstTime:
                votes = VoteRecord.objects.filter(type='success-vote',datetime__lte=currenttime,datetime__gt=currenttime - granularity)
            else:
                votes = VoteRecord.objects.filter(type='success-vote',datetime__lte=currenttime)
                firstTime = False

            for vote in votes:
                if vote.sunetid in considered:
                    continue
                else:
                    considered.add(vote.sunetid)
                if slate:
                    ballot = Ballot.objects.get(voter_id=vote.sunetid)
                    if ballot.vote_exec1 is None:
                        continue
                    elif ballot.vote_exec1.pk == slate.pk:
                        pass
                    else:
                        continue

                total_votes += 1
                print vote.sunetid

                if vote.sunetid not in students:
                    invalid_votes += 1
                    continue


                if 'undergrad-2' in students[vote.sunetid]:
                    frosh_votes += 1
                if 'undergrad-3' in students[vote.sunetid]:
                    soph_votes += 1
                if 'undergrad-4' in students[vote.sunetid]:
                    jun_votes += 1
                if 'undergrad-5plus' in students[vote.sunetid]:
                    sen_votes += 1
                if 'graduate' in students[vote.sunetid]:
                    grad_votes += 1
                if 'coterm' in students[vote.sunetid]:
                    coterm_votes += 1

            undergrad_votes = frosh_votes + soph_votes + jun_votes + sen_votes
            print "%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d" % (currenttime,total_votes,undergrad_votes,grad_votes,coterm_votes,frosh_votes,soph_votes,jun_votes,sen_votes,invalid_votes)

            currenttime += granularity



assu_pops = {
    '1- Undergraduate Student': 'undergrad',
    '2 - Coterm': 'coterm',
    '3 - Graduate Student': 'graduate',
    }
class_years = {
    '5 - Fifth year or more Senior': 'undergrad-5plus',
    '4 - Senior Class Affiliation': 'undergrad-5plus',
    '3 - Junior Class Affiliation': 'undergrad-4',
    '2 - Sophomore Class Affiliation': 'undergrad-3',
    '1 - Freshman Class Affiliation': 'undergrad-2',
    }

def getStudentDict():
    students = {}
    students_path = 'students.csv'
    students_csv = csv.DictReader(open(students_path,'rU'))

    for row in students_csv:
        sunetid = row['SUNetID']
        group = []
        groups = map(str.strip, row['Class Level'].split(','))
        for g in groups:
            if g in assu_pops:
                group.append(assu_pops[g])
            if g in class_years:
                group.append(class_years[g])
        students[sunetid] = group

    return students