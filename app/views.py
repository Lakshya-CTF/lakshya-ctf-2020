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
from .models import Questions, Team, Events, SolvedTimestamps, Machines, SolvedQuestions, SolvedMachines,TakenQuestionHint
import CTFFinal.settings as settings 
from django.utils import timezone
from constance import config
from django.views.decorators.cache import cache_page


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
			login(request, team)
			if not 'time' in request.session:
				request.session['time'] = timezone.localtime().timestamp()
				request.session.save()

			return redirect("/quest")

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
			messages.error(request, "Invalid form submission!")
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
@login_required(login_url="/login/")
def machine(request,id = 1):

	if timezone.localtime().timestamp() < config.START_TIME.timestamp():
		return render(request, "app/instructions.html")

	if timezone.localtime().timestamp() > config.END_TIME.timestamp():
		return render(request,"app/leaderboard.html")



	machine = Machines.objects.get(machineId = id)

	
	if request.method == "POST":
		rating = request.POST.get("radio_btn")
		flag = request.POST.get("flag")
		solved = SolvedMachines.objects.filter(machine = machine,user=request.user)

		if machine.userFlag == flag:
			if not solved:
				
				request.user.points += int((0.4) * machine.machinePoints)

				request.user.save()
				SolvedMachines(machine = machine, user = request.user).save()
				SolvedTimestamps(username=request.user,points=request.user.points).save()
			else:
				messages.error(request,"Already solved!")

		elif machine.rootFlag == flag:
			if isinstance(solved,SolvedMachines):
				if not solved.root:
					
					solved.root = True
					machine.machineSolvers += 1

					if rating == "EA":
						machine.easyRating += 1

					elif rating == "ME":
						machine.mediumRating += 1 

					elif rating == "HA":
						machine.hardRating += 1

					request.user.points += int((0.6) * machine.machinePoints)

					request.user.save()
					machine.save()
					solved.save()
					SolvedTimestamps(username=request.user,points=request.user.points).save()
				else:
					messages.error(request,"Already solved!")

		else:
			messages.error(request,"Invalid flag!")
		

	return render(request,"app/machine.html", {'machine': machine })

def teamlogout(request):
	request.user.timeRequired = timezone.localtime().timestamp() - request.session.get("time")
	request.user.save()
	logout(request)
	return redirect("/leaderboard")


@gzip_page
@login_required(login_url="/login/")
@cache_page(60 * 1)
def quest(request):

	if timezone.localtime().timestamp() < config.START_TIME.timestamp():
		return render(request,"app/instructions.html")

	if timezone.localtime().timestamp() > config.END_TIME.timestamp():
		return render(request,"app/leaderboard.html")

	questions = Questions.objects.all().order_by('questionId')
	machines = Machines.objects.all().order_by('machineId')

	if request.method == "POST":

		flag = request.POST.get("flag")
		flag_id = int(request.POST.get("qid"))
		rating = request.POST.get("radio_btn")
		question = Questions.objects.get(questionId=flag_id)
		solved = SolvedQuestions.objects.filter(question=question,user=request.user)

		if flag == question.questionFlag:
			if not solved:

				request.user.points += question.questionPoints
				
				question.questionSolvers += 1

				if rating == "EA":
					question.easyRating += 1

				elif rating == "ME":
					question.mediumRating += 1

				elif rating == "HA":
					question.hardRating += 1

				messages.success(request, "Flag is correct!")
				 
				question.save()
				request.user.save()
				SolvedQuestions(question = question, user = request.user).save()
				SolvedTimestamps(username = request.user,points = request.user.points).save()
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
			"total_count": len(questions) + len(machines),
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
	''' TODO: Logout from backend '''
	if request.method == "GET":
		difference = int(config.END_TIME.timestamp() - timezone.localtime().timestamp())
		if difference == 0:
			request.user.timeRequired = timezone.localtime().timestamp() - request.session.get("time")
			request.user.save()
			logout(request)
		return HttpResponse(difference)


@csrf_protect
def hint(request):
	if request.method == "POST":

		hint_id = int(request.POST.get("hintid"))
		question = Questions.objects.get(questionId=hint_id)
		taken = TakenQuestionHint.objects.get(question = question, user = request.user)

		questionHint = question.questionHint
		questionPoints = question.questionPoints

		if not taken:

			request.user.points -= int(0.1 * questionPoints)
			request.user.save()
			TakenQuestionHint(question = question,user = request.user, hint = True).save()
		
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
