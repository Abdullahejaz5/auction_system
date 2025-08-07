from django.shortcuts import render
from django.http import HttpResponse
from .models import Members
from django.contrib import messages

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
            
            return decision(request,record.member_id)
        else:
            messages.error(request,'No User Found')
            return render(request,'accounts/login.html')
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
            messages.error(request,'user already exists')
            return render(request,'accounts/signup.html')
        else:
            record=Members(name=name,email=email,contact=contact,password=p1,role=role)
            record.save()
            messages.success(request,'Account created Successfully')
            return render(request,'accounts/signup.html')
 
    return render(request,'accounts/signup.html')

def decision(request,member_id):
    record=Members.objects.filter(member_id=member_id)[0]
    if record.role=='admin':
        return HttpResponse(f'hey from {record} as a Admin')
    if record.role=='seller':
        return HttpResponse(f'hey from {record} as a Seller')
    if record.role=='bidder':
        return HttpResponse(f'hey from {record} as a Bidder')
    return HttpResponse(Members.objects.get(member_id=member_id))


