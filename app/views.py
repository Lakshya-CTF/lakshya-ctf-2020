from django.shortcuts import render,redirect,HttpResponse,render_to_response 
from django.views.decorators.gzip import gzip_page
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from .models import Questions,Team 

import time 



challenges = 14
event_time = 2700

# Create your views here.


def handler404(request, exception, template_name="404.html"):
    response = render_to_response("404.html")
    response.status_code = 404
    return response


@gzip_page 
def teamlogin(request):
	if request.method == 'POST':
		username = request.POST.get('teamname')
		password = request.POST.get('password')
		team = authenticate(username=username,password=password)
		if team is not None:
			if team.played == False:
				login(request,team)
				return redirect('/quest')
			else:
				messages.error(request,'Already played!')
		else:
			messages.error(request,'Invalid credentials!')			
	return render(request,'app/login.html')


@gzip_page
def register(request):
	team = Team()
	if request.method == 'POST':

		reciept_id = request.POST.get('recieptid')
		team.username = request.POST.get('teamname')
		team.password = make_password(request.POST.get('password'))
		
		try:
			team.clean_fields()
			team.save()
		except Exception as e:
			messages.error(request,'Invalid form submission! ')
			return render(request,'app/register.html')
		login(request,team)
		return render(request,'app/instructions.html')
	return render(request,'app/register.html')


@gzip_page
def index(request):
	return render(request,'app/index.html')


@gzip_page
def instructions(request):
	return render(request,'app/instructions.html')


@gzip_page
def about(request):
	return render(request,'app/about.html')

def teamlogout(request):
	request.user.timeRequired = time.time() - request.session.get('timer')
	request.user.played = True
	request.user.save()
	logout(request)
	return redirect('/leaderboard')

@gzip_page
@login_required(login_url='/login/')
def quest(request):
	if 'hints' not in request.session and 'solved' not in request.session:
		request.session['timer'] = time.time()
		request.session['solved'] = [0 for i in range(challenges)]
		request.session['hints'] = [0 for i in range(challenges)]
	questions = Questions.objects.filter(questionCategory=request.user.category)
	if request.method == 'POST':
		flag = request.POST.get('flag')
		flag_id = int(request.POST.get('qid'))
		question = Questions.objects.get(questionId=flag_id,questionCategory=request.user.category)
		if flag == question.questionFlag:
			if not request.session['solved'][flag_id]:
				request.user.points+=question.questionPoints
				messages.success(request,'Correct!')
				request.user.timeRequired = time.time() - request.session.get('timer')
				request.session['solved'][flag_id] = 1
				question.questionSolvers+=1
				question.save()
				request.user.save()
				request.session.save()
			else:
				messages.error(request,'Already solved!')
		else: 
			messages.error(request,'Invalid flag!')
	return render(request,'app/quests.html',context = {'challenges':questions})

@login_required(login_url='/login/')
@gzip_page
def leaderboard(request):
	teams = Team.objects.filter(category=request.user.category).exclude(timeRequired=0.0).order_by('-points','timeRequired')[:10]
	leaderboard = list()
	for rank,team in zip(range(1,len(teams)+1),teams):
		leaderboard.append((rank,team))

	return render(request,'app/leaderboard.html',{'leaderboard':leaderboard})


@login_required(login_url='/login/')
def timer(request):
	if request.method == 'GET':
		return HttpResponse(event_time - int(time.time() - request.session.get('timer')))


@csrf_protect
def hint(request):
	if request.method == 'POST':
		hint_id = int(request.POST.get('hintid'))
		print(request.POST.get('hintid'))
		question = Questions.objects.get(questionId=hint_id,questionCategory=request.user.category)
		questionHint = question.questionHint
		print(hint_id,questionHint)
		questionPoints = question.questionPoints
		if not request.session['hints'][hint_id]:
			request.session['hints'][hint_id] = 1
			request.user.points-=int(0.1*questionPoints)
		request.user.save()
		request.session.save()
		return JsonResponse({'hint':questionHint,'points':request.user.points})

def validate_username(request):
    teamname = request.GET.get('teamname', None)
    data = {
        'is_taken': Team.objects.filter(username__iexact=teamname).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'A user with this username already exists.'
    return JsonResponse(data)




