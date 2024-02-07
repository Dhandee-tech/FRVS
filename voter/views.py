from django.shortcuts import render
from django.contrib import messages
from EC_Admin.models import Voters, Candidates, Election, Votes, Reports
from django.contrib.auth.models import User, auth
from django.http import JsonResponse
import requests
import datetime
from .models import Voted, Complain
from django.contrib.auth.decorators import login_required
from Digital_Voting.settings import BASE_DIR
from django.core.mail import send_mail
import math, random

import cv2,os
import numpy as np
from PIL import Image
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import itertools

# Create your views here.

def register_vid(request):
    if (request.method == 'POST'):
        voterid = request.POST['vid']
        if (User.objects.filter(username=voterid)).exists():
            messages.info(request, 'Voter already registered')
            return render(request, 'registervid.html')
        else:
            if Voters.objects.filter(voterid_no=voterid):
                register_vid.v = Voters.objects.get(voterid_no=voterid)
                user_phone = str(register_vid.v.mobile_no)
                url = "http://2factor.in/API/V1/77356882-7c4f-11ee-8cbb-0200cd936042/SMS/" + user_phone + "/AUTOGEN"
                response = requests.request("GET", url)
                data = response.json()
                request.session['otp_session_data'] = data['Details']
                messages.info(request, 'an OTP has been sent to registered mobile number ending with')
                mobno = user_phone[6:]
                return render(request, 'otp.html', {'mno': mobno})
            else:
                messages.info(request, 'Invalid Voter ID')
                return render(request, 'registervid.html')

def otp(request):
    if (request.method == "POST"):
        userotp = request.POST['otp']
        url = "http://2factor.in/API/V1/77356882-7c4f-11ee-8cbb-0200cd936042/SMS/VERIFY/" + request.session[
            'otp_session_data'] + "/" + userotp
        response = requests.request("GET", url)
        data = response.json()
        if data['Status'] == "Success":
            response_data = {'Message': 'Success'}
            return render(request, './register.html',
                          {'voterid_no': register_vid.v.voterid_no, 'name': register_vid.v.name,
                           'surname': register_vid.v.surname, 'gender': register_vid.v.gender,
                           'dateofbirth': register_vid.v.dateofbirth, 'address': register_vid.v.address,
                           'mobile_no': register_vid.v.mobile_no, 'state': register_vid.v.state,
                           'pincode': register_vid.v.pincode, 'lga': register_vid.v.lga,
                           'ward': register_vid.v.ward, 'voter_image': register_vid.v.voter_image})
        else:
            messages.info(request, 'Invalid OTP')
            return render(request, 'otp.html')


def register(request):
    if (request.method == 'POST'):
        voter_id = request.POST.get('v_id')
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        vidfile = request.FILES['vidfile']
        v=Voters.objects.get(voterid_no=voter_id)
        Id=str(v.id)
        folder=BASE_DIR+"/DatasetVideo/"
        fs=FileSystemStorage(location=folder)
        vidfilename=Id+vidfile.name
        filename=fs.save(vidfilename,vidfile)
        name=v.voterid_no
        faceDetect = cv2.CascadeClassifier(BASE_DIR + "/haarcascade_frontalface_default.xml")
        cam = cv2.VideoCapture(folder+"/"+vidfilename)
        sampleNum = 0
        while (True):
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = faceDetect.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                sampleNum = sampleNum + 1
                cv2.imwrite(BASE_DIR + "/TrainingImage/"+ name +"."+ Id + '.' + str(sampleNum) + ".jpg",gray[y:y + h, x:x + w])
                cv2.imshow("Face", img)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            elif sampleNum > 60:
                break
        cam.release()
        cv2.destroyAllWindows()

        # Train
        recognizer = cv2.face.LBPHFaceRecognizer_create()

        def getImagesAndLabels(path):
            imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
            faces = []
            Ids = []
            for imagePath in imagePaths:
                pilImage = Image.open(imagePath).convert('L')
                imageNp = np.array(pilImage, 'uint8')
                Id = int(os.path.split(imagePath)[-1].split('.')[1])
                faces.append(imageNp)
                Ids.append(Id)
            return faces, Ids
        faces, Id = getImagesAndLabels(BASE_DIR + "/TrainingImage/")
        recognizer.train(faces, np.array(Id))
        recognizer.save(BASE_DIR + "/TrainingImageLabel/Trainner.yml")
        if password1 == password2:
            add_user = User.objects.create_user(username=voter_id, password=password1, email=email)
            add_user.save()
            messages.info(request, 'Voter Registered')
            return render(request, 'index.html')


@login_required(login_url='home')
def vhome(request):
    vhome.username=request.session['v_id']
    v = Voters.objects.get(voterid_no=vhome.username)
    vhome.image=v.voter_image
    return render(request,'voter/vhome.html',{'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vprocess(request):
    return render(request,'voter/votingprocess.html',{'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vprofile(request):
    v_id = request.session['v_id']
    v = Voters.objects.get(voterid_no=v_id)
    vemail = User.objects.get(username=v_id)
    return render(request, 'voter/voter profile.html', {'voterid_no': v.voterid_no, 'name': v.name,
                                                  'surname': v.surname, 'gender': v.gender,
                                                  'dateofbirth': v.dateofbirth, 'address': v.address,
                                                  'mobile_no': v.mobile_no, 'state': v.state,
                                                  'pincode': v.pincode, 'lga': v.lga,
                                                  'ward': v.ward, 'voter_image': v.voter_image,
                                                  'email': vemail.email,'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vchangepassword(request):
    return render(request, 'voter/vchangepassword.html',{'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vchange_password(request):
    if request.method == "POST":
        v_id = request.session['v_id']
        oldpass = request.POST['oldpass']
        newpass = request.POST['password1']
        newpass2 = request.POST['password2']
        u=auth.authenticate(username=v_id,password=oldpass)
        if u is not None:
            u=User.objects.get(username=v_id)
            if oldpass!=newpass:
                if newpass == newpass2:
                    u.set_password(newpass)
                    u.save()
                    messages.info(request, 'Password Changed')
                    return render(request, 'voter/vchangepassword.html',{'username':vhome.username,'image':vhome.image})
            else:
                messages.info(request, 'New password is same as old password')
                return render(request, 'voter/vchangepassword.html',{'username':vhome.username,'image':vhome.image})
        else:
            messages.info(request, 'Old Password not matching')
            return render(request, 'voter/vchangepassword.html',{'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vviewcandidate(request):
    return render(request, 'voter/view candidate.html',{'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vview_candidate(request):
    if request.method == 'POST':
        state = request.POST['states']
        constituency1 = request.POST['constituency1']
        constituency2 = request.POST['constituency2']
        if constituency1 == 'lga':
            candidates = Candidates.objects.filter(state=state, constituency=constituency1, lga=constituency2)
            if candidates:
                return render(request, 'voter/view candidate.html', {'constituency':constituency2,'candidates': candidates,'username':vhome.username,'image':vhome.image})
            else:
                messages.info(request, 'No Candidate Found')
                return render(request, 'voter/view candidate.html',{'username':vhome.username,'image':vhome.image})
        else:
            candidates = Candidates.objects.filter(state=state, constituency=constituency1, ward=constituency2)
            if candidates:
                return render(request, 'voter/view candidate.html', {'constituency':constituency2,'candidates': candidates,'username':vhome.username,'image':vhome.image})
            else:
                messages.info(request, 'No Candidate Found')
                return render(request, 'voter/view candidate.html',{'username':vhome.username,'image':vhome.image})

@login_required(login_url='home')
def velection(request):
    v_id = request.session.get('v_id')
    
    if not v_id:
        # Handle the case where 'v_id' is not present in the session
        return render(request, 'voter/vnoelection.html', {'username': vhome.username, 'image': vhome.image})

    try:
        vdetail = Voters.objects.get(voterid_no=v_id)
    except Voters.DoesNotExist:
        # Handle the case where voter details are not found
        return render(request, 'voter/vnoelection.html', {'username': vhome.username, 'image': vhome.image})

    status = 'active'
    
    try:
        velection.e = Election.objects.get(state=vdetail.state, status=status)
    except Election.DoesNotExist:
        # Handle the case where no active election is found
        return render(request, 'voter/vnoelection.html', {'username': vhome.username, 'image': vhome.image})

    now = datetime.datetime.now()
    nowdate = now.strftime("%G-%m-%d")
    nowtime = now.strftime("%X")
    
    sdate = str(velection.e.start_date)

    if nowdate == sdate:
        stime = str(velection.e.start_time)
        etime = str(velection.e.end_time)

        if stime <= nowtime <= etime:
            if velection.e.election_type == 'President':
                vlga = vdetail.lga
                candidates = Candidates.objects.filter(lga=vlga)
                return render(request, 'voter/velection.html', {'candidate': candidates, 'username': vhome.username, 'image': vhome.image})
            elif velection.e.election_type == 'Governor':
                vward = vdetail.ward
                candidates = Candidates.objects.filter(ward=vward)
                return render(request, 'voter/velection.html', {'candidate': candidates, 'username': vhome.username, 'image': vhome.image})

    # If none of the above conditions are met, display "No Elections Running" message
    messages.info(request, 'No Elections Running')
    return render(request, 'voter/vnoelection.html', {'username': vhome.username, 'image': vhome.image})

@login_required(login_url='home')
def vote(request):
    if request.method == "POST":
        v_id = request.session['v_id']
        vote.v = Voted.objects.get(election_id=velection.e.election_id, voter_id=v_id)
        if vote.v.has_voted == 'no':
            vote.candidateid = request.POST['can']
            vmob = Voters.objects.get(voterid_no=v_id)
            vmobno = str(vmob.mobile_no)
            url = "http://2factor.in/API/V1/77356882-7c4f-11ee-8cbb-0200cd936042/SMS/" + vmobno + "/AUTOGEN"
            response = requests.request("GET", url)
            data = response.json()
            request.session['otp_session_data'] = data['Details']
            response_data = {'Message': 'Success'}
            messages.info(request, 'An OTP has been sent to the registered mobile number ending with')
            mobno = vmobno[6:]
            return render(request, 'voter/voteotp.html', {'mno': mobno, 'username': vhome.username, 'image': vhome.image})
        else:
            messages.info(request, 'Already Voted')
            return render(request, 'voter/votesub.html', {'username': vhome.username, 'image': vhome.image})


@login_required(login_url='home')
def subvoteotp(request):
    if (request.method == "POST"):
        userotp = request.POST['otp']
        url = "http://2factor.in/API/V1/77356882-7c4f-11ee-8cbb-0200cd936042/SMS/VERIFY/" + request.session['otp_session_data'] + "/" + userotp
        response = requests.request("GET", url)
        data = response.json()
        if data['Status'] == "Success":
            v_id = request.session['v_id']
            vemail=User.objects.get(username=v_id)
            email=vemail.email
            string="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            length=len(string)
            subvoteotp.otp=""
            for i in range(6):
                subvoteotp.otp+=string[math.floor(random.random()*length)]
            send_mail(
                'OTP from Digital_Voting',
                'The following is the 6 digit alphanumeric email OTP to be entered for vote submission '+subvoteotp.otp,
                settings.EMAIL_HOST_USER,
                [email]
                )
            emailstart=email[0:3]
            emailend=email[-13:]
            emailid=emailstart+'*****'+emailend
            messages.info(request,'an 6 digit alphanumeric OTP has been sent to your registered email address ')
            return render(request, 'voter/voteemailotp.html', {'username':vhome.username,'image':vhome.image,'email':emailid})
        else:
            messages.info(request, 'Invalid OTP')
            return render(request, 'voter/voteotp.html',{'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def subvoteemailotp(request):
    if request.method=="POST":
        emailotp=request.POST['emailotp']
        if subvoteotp.otp==emailotp:
            votecan = Votes.objects.get(election_id=velection.e.election_id, candidate_id=vote.candidateid)
            votecan.online_votes += 1
            votecan.save()
            vote.v.has_voted = 'yes'
            vote.v.where_voted = 'online'
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ipaddress = x_forwarded_for.split(',')[-1].strip()
            else:
                ipaddress = request.META.get('REMOTE_ADDR')
            vote.v.ipaddress = ipaddress
            vote.v.datetime = datetime.datetime.now()
            vote.v.save()
            messages.info(request, 'Vote submitted to ')
            return render(request, 'voter/votesub.html', {'votesub': votecan.candidate_name,'username':vhome.username,'image':vhome.image})
        else:
            messages.info(request, 'Invalid OTP')
            return render(request, 'voter/voteemailotp.html',{'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vviewresult(request):
    elections = Election.objects.all()
    return render(request, 'voter/viewresult.html', {'elections': elections,'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vview_result(request):
    if request.method=="POST":
        election_id = request.POST['e_id']
        resulttype = request.POST['resulttype']
        e=Election.objects.get(election_id=election_id)
        estate=e.state
        if resulttype=="partywise":
            result = Votes.objects.filter(election_id=election_id)
            v=Votes.objects.filter(election_id=election_id)
            constituencies=[]
            for i in v:
                if i.constituency not in constituencies:
                    constituencies.append(i.constituency)
            d=[]
            for i in constituencies:
                resultcon=Votes.objects.filter(election_id=election_id,constituency=i)
                maxi=0
                for i in resultcon:
                    if i.total_votes>maxi:
                        maxi=i.total_votes
                        d.append(i.candidate_party)
            parties=[]
            for k in v:
                if k.candidate_party not in parties:
                    parties.append(k.candidate_party)
            final={}
            for i in parties:
                c=d.count(i)
                final.update({i:c})
            par=[]
            won=[]
            for k,v in final.items():
                par.append(k)
                won.append(v)
            parwon=zip(par,won)
            total=0
            for i in won:
                total+=i
            return render(request, 'voter/viewpartywise.html', {'total':total,'parwon':parwon,'electionid': election_id,'state':estate,'username':vhome.username,'image':vhome.image})
        elif resulttype=="constituencywise":
            v=Votes.objects.filter(election_id=election_id)
            constituencies=[]
            for i in v:
                if i.constituency not in constituencies:
                    constituencies.append(i.constituency)
            return render(request, 'voter/viewresultconwise.html', {'electionid':election_id,'state':estate,'constituency':constituencies,'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vview_result_filter(request):
    if request.method=="POST":
        election_id = request.POST['e_id']
        constituency = request.POST['constituency']
        e=Election.objects.get(election_id=election_id)
        estate=e.state
        v=Votes.objects.filter(election_id=election_id)
        result = Votes.objects.filter(election_id=election_id, constituency=constituency)
        constituencies=[]
        for i in v:
            if i.constituency not in constituencies:
                constituencies.append(i.constituency)
        totalvotes=0
        totalonline=0
        totalevm=0
        for i in result:
            totalvotes+=i.total_votes
            totalonline+=i.online_votes
            totalevm+=i.evm_votes
        perofvotes=[]
        for i in result:
            per=(i.total_votes/totalvotes)*100
            percentage=float("{:.2f}".format(per))
            perofvotes.append(percentage)
        finalresult=zip(result,perofvotes)
        return render(request, 'voter/viewresultconwise.html', {'totalonline':totalonline,'totalevm':totalevm,'totalvotes':totalvotes,'result':finalresult,'electionid':election_id,'state':estate,'constituency':constituencies,'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vviewreport(request):
    elections = Election.objects.all()
    return render(request, 'voter/viewreport.html', {'elections': elections,'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vview_report(request):
    election_id = request.POST['e_id']
    constituency = request.POST['constituency2']
    report = Reports.objects.filter(election_id=election_id, constituency=constituency)
    elections = Election.objects.all()
    return render(request, 'voter/viewreport.html', {'report': report, 'elections':elections,'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vcomplain(request):
    v_id = request.session['v_id']
    complain=Complain.objects.filter(voterid_no=v_id,viewed=True,replied=True)
    return render(request, 'voter/vcomplain.html',{'voterid_no': v_id, 'reply':complain,'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def submitcomplain(request):
    if (request.method == 'POST'):
        v_id = request.session['v_id']
        complain = request.POST['complain']
        addcomplain = Complain(voterid_no=v_id, complain=complain)
        addcomplain.save()
        messages.info(request, 'complain submitted')
        return render(request, 'voter/vcomplain.html',{'username':vhome.username,'image':vhome.image})

