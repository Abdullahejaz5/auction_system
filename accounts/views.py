from django.shortcuts import render
from django.http import HttpResponse
from .models import Members
def landing(request):
    return render(request,'accounts/homepage.html')

def login(request):
    if request.method=='POST':
        email=request.POST.get('email','')
        p=request.POST.get('password','')
        role=request.POST.get("role",'')
        members=Members.objects.filter(email=email,password=p,role=role)
        if len(members)>0:
            record=members[0]
            return HttpResponse(f'{record.name} has {record.member_id} id ')
        else:
            return HttpResponse('No user found (#debugging)')
    return render(request,'accounts/login.html')

def signup(request):
    if request.method=='POST':
        name=request.POST.get('fullName','')
        email=request.POST.get('email','')
        contact=request.POST.get('phoneNumber','')
        p1=request.POST.get('password','')
        p2=request.POST.get('confirmPassword','')
        role=request.POST.get('role','')

        members=Members.objects.filter(email=email)
        if len(members)>0:
            return HttpResponse('user already exists (#debugging)')
        else:
            record=Members(name=name,email=email,contact=contact,password=p1,role=role)
            record.save()
            return HttpResponse('submitted (#debugging)')
 
    return render(request,'accounts/signup.html')
