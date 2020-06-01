from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.gzip import gzip_page
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from .models import Questions, Team, Events, SolvedTimestamps, Machines
import time
import CTFFinal.settings as settings 


from django.views.decorators.cache import cache_page

challenges = 14
event_time = 2700

# Create your views here.


def handler404(request, exception, *args, **kwargs):
    response = render(None,"404.html")
    response.status_code = 404
    return response

def handler500(request):
    response = render(None,"500.html")
    response.status_code = 500
    return response

@gzip_page
def teamlogin(request):
    ''' TODO: Do not permit multiple sessions '''
    if request.method == "POST":
        username = request.POST.get("teamname")
        password = request.POST.get("password")
        team = authenticate(username=username, password=password)
        if team is not None:
            if team.played == False:
                login(request, team)
                return redirect("/quests")
            else:
                messages.error(request, "Already played!")
        else:
            messages.error(request, "Invalid credentials!")
    return render(request, "app/login.html")


@gzip_page
def register(request):
    team = Team()
    if request.method == "POST":

        receiptid = request.POST.get("receiptid")
        team.username = request.POST.get("teamname")
        team.password = make_password(request.POST.get("passwd"))
        
        if settings.MODE == 'production':
            query_count = (Events.objects.using("receipts").filter(
            receiptid = receiptid).count())

        elif settings.MODE == 'development':
            query_count = (Events.objects.filter(receiptid = receiptid).count())
        
        try:
            if query_count == 0:
                raise TypeError

            team.clean_fields()
            team.save()
        except Exception as e:
            messages.error(request, "Invalid form submission! ")
            return render(request, "app/register.html")
        login(request, team)
        return render(request, "app/instructions.html")
    return render(request, "app/register.html")


@gzip_page
def index(request):
    return render(request, "app/index.html")


@gzip_page
def instructions(request):
    return render(request, "app/instructions.html")


@gzip_page
def about(request):
    return render(request, "app/about.html")

@gzip_page
def machine(request,id = 1):

    machine = Machines.objects.get(id = id)
    return render(request,"app/machine.html", {'machine': machine })

def teamlogout(request):
    request.user.timeRequired = time.time() - request.session.get("timer")
    request.user.played = True
    request.user.save()
    logout(request)
    return redirect("/leaderboard")


@gzip_page
@login_required(login_url="/login/")
@cache_page(60 * 1)
def quest(request):
    if "hints" not in request.session and "solved" not in request.session:
        request.session["timer"] = time.time()
        request.session["solved"] = [0 for i in range(challenges)]
        request.session["hints"] = [0 for i in range(challenges)]

    questions = Questions.objects.all()
    machines = Machines.objects.all()
    if request.method == "POST":
        flag = request.POST.get("flag")
        flag_id = int(request.POST.get("qid"))
        rating = request.POST.get("radio_btn")
        question = Questions.objects.get(questionId=flag_id)
        if flag == question.questionFlag:
            if not request.session["solved"][flag_id]:
                request.user.points += question.questionPoints
                messages.success(request, "Flag is correct!")
                request.user.timeRequired = time.time() - request.session.get(
                    "timer")
                request.session["solved"][flag_id] = 1
                question.questionSolvers += 1

                if rating == "EA":
                    question.easyRating += 1

                elif rating == "ME":
                    question.mediumRating += 1

                elif rating == "HA":
                    question.hardRating += 1

                SolvedTimestamps(username=request.user,points=request.user.points).save() 
                question.save()
                request.user.save()
                request.session.save()
            else:
                messages.error(request, "Already solved!")
        else:
            messages.error(request, "Invalid flag!")

    return render(
        request,
        "app/quests.html",
        context={
            "challenges": questions,
            "num_challenges": len(questions),
            "machines": machines,
        },
    )


@gzip_page
@cache_page(60 * 5)
def leaderboard(request):
    teams = (Team.objects.all().exclude(timeRequired=0.0).order_by(
        "-points", "timeRequired")[:10])
    leaderboard = list()
    for rank, team in zip(range(1, len(teams) + 1), teams):
        leaderboard.append((rank, team))


    usernames = list()
    for team in teams:
        data = SolvedTimestamps.objects.filter(username = team)
        usernames.append({'name': team.username,'data': data})

    return render(request, "app/leaderboard.html",
                  {"leaderboard": leaderboard,"usernames":usernames})


@login_required(login_url="/login/")
def timer(request):
    if request.method == "GET":
        return HttpResponse(event_time -
                            int(time.time() - request.session.get("timer")))


@csrf_protect
def hint(request):
    if request.method == "POST":

        hint_id = int(request.POST.get("hintid"))
        question = Questions.objects.get(questionId=hint_id)
        questionHint = question.questionHint
        questionPoints = question.questionPoints

        if not request.session["hints"][hint_id]:

            request.session["hints"][hint_id] = 1
            request.user.points -= int(0.1 * questionPoints)

        request.user.save()
        request.session.save()
        return JsonResponse({
            "hint": questionHint,
            "points": request.user.points
        })


def validate_username(request):

    teamname = request.GET.get("teamname", None)
    data = {
        "is_taken": Team.objects.filter(username__iexact=teamname).exists()
    }
    if data["is_taken"]:
        data["error_message"] = "A user with this username already exists."
    return JsonResponse(data)
