import random
from datetime import datetime
from django.http import HttpResponseRedirect, QueryDict, HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from issues.models import Electorate
from openelections.petitions.models import Signature
from openelections.petitions.forms import SignatureForm
from openelections.issues.models import Issue
from django.contrib.auth.decorators import login_required, permission_required
from petitions.models import PaperSignature, ValidationResult
from petitions.forms import ValidationForm
import math
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import openelections.constants as oeconstants
from petitions.student_loader import loadStudentDict

def index(request):
    return HttpResponseRedirect('/issues/petitioning')

@login_required
def detail(request, issue_slug):
    issue = get_object_or_404(Issue, slug=issue_slug).get_typed()
    
    sunetid = request.user.webauth_username
    can_manage = issue.sunetid_can_manage(sunetid)

    if not issue.public and not can_manage:
        return render_to_response('issues/not_public.html',{'issue': issue}, context_instance=RequestContext(request))
    
    signatures = Signature.objects.filter(issue=issue).order_by('-id') #signatures are public
    newsig = Signature()
    newsig.issue = issue
    newsig.sunetid = sunetid
    form = None
    if not issue.signed_by_sunetid(sunetid) and issue.petition_open():
        form = SignatureForm(issue, instance=newsig)
    return render_to_response('petitions/detail.html', {
        'issue': issue,
        'form': form,
        'can_manage': can_manage,
        'signatures': signatures,
        'sunetid': sunetid
    }, context_instance=RequestContext(request))

@login_required
def sign(request, issue_slug):
    issue = get_object_or_404(Issue, slug=issue_slug).get_typed()
    
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('openelections.petitions.views.detail', None, [issue_slug]))
    
    sunetid = request.user.webauth_username
    attrs = request.POST.copy()
    attrs['sunetid'] = sunetid
    attrs['issue'] = issue.id
    attrs['ip_address'] = request.META['REMOTE_ADDR']
    attrs['signed_at'] = datetime.now()
    form = SignatureForm(issue, attrs)
    if form.is_valid() and issue.petition_open():
        form.save()
        return HttpResponseRedirect(reverse('openelections.petitions.views.detail', None, [issue_slug])+'#sign-form')
    else:
        return render_to_response('petitions/detail.html',
                                  {
                                    'issue': issue, 
                                    'form': form, 
                                    'jumptosign':True
                                  }, context_instance=RequestContext(request))

def api_count(request, issue_slug):
    issue = get_object_or_404(Issue, slug=issue_slug).get_typed()
    sig_count = Signature.objects.filter(issue=issue).count()
    response = HttpResponse(sig_count)
    response['Access-Control-Allow-Origin'] = '*'
    return response

@permission_required('signature.can_add')
def add_signatures(request,issue_slug):
    issue = get_object_or_404(Issue,slug=issue_slug).get_typed()

    if request.method != "POST":
        return render_to_response('petitions/admin_entersig.html',
                                    {'issue': issue,
                                  }, context_instance=RequestContext(request))

    signatures = request.POST.getlist('suid')
    responsetext = ""
    num_added = 0
    for signature in signatures:
        if signature is not None and signature != "":
            papersig = PaperSignature()
            papersig.sunetid = signature
            papersig.entered_by = request.user
            papersig.issue = issue
            papersig.save()
            responsetext += "Entered '%s'<br /> " % signature
            num_added += 1
    return render_to_response('petitions/admin_entersig.html',
                                    {'issue': issue, 'responsetext': responsetext, 'num_added': num_added
                                  }, context_instance=RequestContext(request))

@permission_required('signature.can_add')
def view_signatures(request,issue_slug):
    issue = get_object_or_404(Issue,slug=issue_slug).get_typed()
    signatures = issue.papersignature_set.all()

    considered_set = set()
    problem_set = (list(),list(),list()) # 0 = duplicate online, 1 = duplicate on paper, 2 = clean
    for signature in signatures:
        if signature.sunetid in considered_set:
            problem_set[1].append(signature)
            continue

        if Signature.objects.filter(sunetid=signature.sunetid,issue=issue).count() > 0:
            problem_set[0].append(signature)
        else:
            problem_set[2].append(signature)
        considered_set.add(signature.sunetid)
        

    return render_to_response('petitions/admin_viewsig.html',
                                    {'issue': issue,
                                     'problem_set': problem_set,
                                     'considered': considered_set,
                                     'total': len(signatures)
                                  }, context_instance=RequestContext(request))

def randomString(length):
    alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMONPQRSTUVWXYZ'
    string = ''
    for x in range(0,length):
        string += random.sample(alphabet, 1)[0]
    return string

@permission_required('signature.can_add')
def setup_validate(request):
    TEST_PERCENT = 0.05

#--Select 20% of grad petitions for exec races
#--Select 10% of non-grad petitions for exec races
#--Select 15 people for each Senator
#--Select 10% for each class president
#--Select 20% for each paper special fees petition
#--Select 10% for each online special fees petition

    electorate_ug = Electorate.objects.get(slug="undergrad")
    electorate_coterm = Electorate.objects.get(slug="coterm")
    electorate_grad = Electorate.objects.get(slug="graduate")

    # Special Fees
    for issue in Issue.objects.filter(kind=oeconstants.ISSUE_SPECFEE).filter(public=True):
        if not issue.needs_petition():
            continue

        # online signatures
        osigs = Signature.objects.filter(issue=issue)
        if len(osigs) <= 1:
            continue
        num_tested = int(math.ceil(float(len(osigs)) * .10))
        selected = random.sample(osigs,num_tested)
        for signature in selected:
            addValidationNeeded(issue,signature,'online')

        # paper sigs
        psigs = PaperSignature.objects.filter(issue=issue)
        if len(psigs) <= 1:
            continue
        num_tested = int(math.ceil(float(len(psigs)) * .20))
        selected = random.sample(psigs,num_tested)
        for signature in selected:
            addValidationNeeded(issue,signature,'paper')

    # Exec
    for issue in Issue.objects.filter(kind=oeconstants.ISSUE_EXEC).filter(public=True):
        if not issue.needs_petition():
            continue

        # online signatures: undergrad
        osigs = Signature.objects.filter(issue=issue).filter(electorate__in=[electorate_ug])
        if len(osigs) <= 1:
            continue
        num_tested = int(math.ceil(float(len(osigs)) * .10))
        selected = random.sample(osigs,num_tested)
        for signature in selected:
            addValidationNeeded(issue,signature,'online')

        # online signatures: grad
        osigs = Signature.objects.filter(issue=issue).filter(electorate__in=[electorate_grad,electorate_coterm])
        if len(osigs) <= 1:
            continue
        num_tested = int(math.ceil(float(len(osigs)) * .20))
        selected = random.sample(osigs,num_tested)
        for signature in selected:
            addValidationNeeded(issue,signature,'online')

        # paper sigs
        psigs = PaperSignature.objects.filter(issue=issue)
        if len(psigs) <= 1:
            continue
        num_tested = int(math.ceil(float(len(psigs)) * .20))
        selected = random.sample(psigs,num_tested)
        for signature in selected:
            addValidationNeeded(issue,signature,'paper')

    # Class Presidents
    for issue in Issue.objects.filter(kind=oeconstants.ISSUE_CLASSPRES).filter(public=True):
        if not issue.needs_petition():
            continue

        # online signatures
        osigs = Signature.objects.filter(issue=issue)
        if len(osigs) <= 1:
            continue
        num_tested = int(math.ceil(float(len(osigs)) * .10))
        selected = random.sample(osigs,num_tested)
        for signature in selected:
            addValidationNeeded(issue,signature,'online')

        # paper sigs
        psigs = PaperSignature.objects.filter(issue=issue)
        if len(psigs) <= 1:
            continue
        num_tested = int(math.ceil(float(len(psigs)) * .10))
        selected = random.sample(psigs,num_tested)
        for signature in selected:
            addValidationNeeded(issue,signature,'paper')

    # Senator
    # Special Fees
    for issue in Issue.objects.filter(kind=oeconstants.ISSUE_SPECFEE).filter(public=True):
        if not issue.needs_petition():
            continue

        # online signatures
        osigs = Signature.objects.filter(issue=issue)
        if len(osigs) <= 1:
            continue
        num_tested = 15
        selected = random.sample(osigs,min([num_tested,len(osigs)]))
        for signature in selected:
            addValidationNeeded(issue,signature,'online')

        # paper sigs
        psigs = PaperSignature.objects.filter(issue=issue)
        if len(psigs) <= 1:
            continue
        num_tested = 15
        selected = random.sample(psigs,min([num_tested,len(psigs)]))
        for signature in selected:
            addValidationNeeded(issue,signature,'paper')

    return HttpResponse("Completed setup.")

def addValidationNeeded(issue,signature,type='online'):
    validation = ValidationResult()
    validation.sunetid = signature.sunetid
    validation.issue = issue
    validation.location = type
    validation.key = randomString(64)
    validation.save()

@permission_required('signature.can_add')
def validate_send(request,start):
    PER_BATCH = 40

    signatures = ValidationResult.objects.filter(pk__gt=start)[:PER_BATCH]
    response = ""
    for signature in signatures:
        success = sendValidationMessage(signature)
        if success:
            response += " / Successfully sent to " + signature.sunetid
            signature.sent = True
            signature.save()
        else:
            response += "<br />FAILED TO SEND to " + signature.sunetid + "<br />"
    last = signatures[len(signatures)-1].pk
    url = reverse('openelections.petitions.views.validate_send',None,[last])
    response = "<a href = '%s'>Send next</a><br />" % url + response
    return HttpResponse(response)

smtpConnection = None
def sendValidationMessage(signature):
    global smtpConnection
    fromAddr = "Adam Adler (ASSU Elections Commission) <ajadler@elections.stanford.edu>"
    login = "trusheim"
    password = ""

    toAddress = signature.sunetid + "@stanford.edu"

    message = MIMEMultipart()
    message['Subject'] = "Your petition signature for %s" % signature.issue.title
    message['To'] = toAddress
    message['Reply-To'] = "elections@elections.stanford.edu"
    message['From'] = fromAddr

    link = "http://petitions.stanford.edu/petitions/validate/%s/" % signature.key

    html = """<p>Hello,</p>
    <p>The ASSU Elections Commission needs your help to validate the petition for %s, a candidate for %s.</p>
    <p>Our records indicate that you signed a petition for this candidate/group. Your signature on this petition has been randomly selected for verification to ensure that
    it was not forged, and that it was not solicited in violation of elections regulations.</p>
    <p><strong>Please <a href = "%s">fill out the form located at the Elections Commission's website</a>
    to complete this validation within 24 hours.</strong> Your support is essential in this process.</p><br />
    <p>The ASSU Elections Commission is always open to hear your comments or concerns about the elections process. Please contact us at
    elections@elections.stanford.edu, or online at http://elections.stanford.edu.</p>
    <p>Cheers,<br/>Adam Adler<br />ASSU Elections Commissioner<br />ajadler@elections.stanford.edu / (650) 741-3337</p>

    <hr />
    <p>This is an official communication from the ASSU Elections Commission: elections@elections.stanford.edu.</p>
    """ % (signature.issue.title,oeconstants.ISSUE_TYPES_DICT[signature.issue.kind],link)

    print html

    messagePart = MIMEText(html.encode('UTF-8'),'html','UTF-8')
    message.attach(messagePart)

    if smtpConnection is None:
        smtpConnection = SMTP("smtp.stanford.edu",587,timeout=10)
        smtpConnection.starttls()
        smtpConnection.login(login,password)
    try:
        smtpConnection.sendmail(fromAddr,toAddress,message.as_string())
        return True
    except Exception,e:
        smtpConnection = None
        return False


def validate(request,key):
    signature = get_object_or_404(ValidationResult,key=key)

    if signature.completed:
        return render_to_response('petitions/validate_complete.html', context_instance=RequestContext(request))

    signature.started = True
    signature.save()

    form = ValidationForm()
    if request.method == "POST":
        form = ValidationForm(request.POST)

    if form.is_valid():
        signature.extra = form.cleaned_data['extra']
        signature.did_sign = form.cleaned_data['did_sign']
        signature.undergraduate = form.cleaned_data['undergrad']
        signature.class_petition = form.cleaned_data['class_petition']
        signature.provided_name = form.cleaned_data['name']
        signature.completed = True
        signature.save()
        return render_to_response('petitions/validate_complete.html', context_instance=RequestContext(request))

    return render_to_response('petitions/validate.html',
                                    {'signature': signature,
                                     'form': form,
                                  }, context_instance=RequestContext(request))

@permission_required('signature.can_add')
def validate_results(request):
    vresults = []
    for issue in Issue.objects.all():
        if not issue.public:
            continue
        verifications = ValidationResult.objects.filter(issue=issue)
        num = 0
        num_submitted = 0
        num_valid = 0
        invalid = []
        for verification in verifications:
            num += 1
            if verification.is_valid():
                num_valid += 1
            if verification.completed:
                num_submitted += 1
                if not verification.is_valid():
                    invalid.append(verification)
        vresults.append((issue,num,num_submitted,num_valid,invalid))
    return render_to_response('petitions/validate_results.html',
                                    {'results': vresults
                                  }, context_instance=RequestContext(request))

@permission_required('signature.can_add')
def validate_students(request):
    vresults = []
    try:
        real_students = loadStudentDict()
    except Exception as e:
        return HttpResponseNotFound("Student CSV cannot be loaded. Check it's in the right place, and that it has columns named 'SUNetID' and 'Class Level' :(.<br /> Error: %s" % e)

    for issue in Issue.objects.filter(public=True):
        signatures = Signature.objects.filter(issue=issue)
        signed_num = len(signatures)
        valid_num = 0
        invalid_num = 0
        invalid_set = []

        for signature in signatures:
            if signature.sunetid in real_students:
                valid_num += 1
            else:
                invalid_num += 1
                invalid_set.append(signature.sunetid)

        vresults.append((issue,'Online',signed_num,valid_num,invalid_num,', '.join(invalid_set)))

        signatures = PaperSignature.objects.filter(issue=issue)
        signed_num = len(signatures)
        valid_num = 0
        invalid_num = 0
        invalid_set = []
        for signature in signatures:
            if signature.sunetid in real_students:
                valid_num += 1
            else:
                invalid_num += 1
                invalid_set.append(signature.sunetid)

        vresults.append((issue,'Paper',signed_num,valid_num,invalid_num,', '.join(invalid_set)))

    return render_to_response('petitions/validate_students.html',
            {'results': vresults }, context_instance=RequestContext(request))