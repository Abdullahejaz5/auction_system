from django.shortcuts import render
from django.http import HttpResponse
from .models import Members,Products,Messages
from django.contrib import messages
import json
from django.core.paginator import Paginator


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
        name=record.name
        pendings=len(Products.objects.filter(product_owner=member_id,product_status='pending'))
        live=len(Products.objects.filter(product_owner=member_id,product_status='live'))
        sold=len(Products.objects.filter(product_owner=member_id,product_status='sold'))
        inactive=len(Products.objects.filter(product_owner=member_id,product_status='inactive'))
        messages=Messages.objects.filter(seller_id=member_id).order_by('time')
        if len(messages)>=5:
            messages=messages[:5]
        return render(request,'accounts/dashboard_seller.html',{'id':member_id,'pendings':pendings,'live':live,'sold':sold,'inactive':inactive,'name':name,'updates':messages})
    

    if record.role=='bidder':
        return HttpResponse(f'hey from {record} as a Bidder')
    

    return HttpResponse(Members.objects.get(member_id=member_id))


def new_auction(request,member_id):
    if request.method=='POST':
        name=request.POST.get('name','')
        category=request.POST.get('category','')
        description=request.POST.get('description','')
        starting_price=request.POST.get('starting_price','')
        reserve_price=request.POST.get('reserve_price','')
        buy_now_price=request.POST.get('buy_now_price','')
        image = request.FILES.get('images')
        checkbox_value = request.POST.get('checkbox', '')
        if checkbox_value:
            record=Products(product_name=name,product_category=category,product_desc=description,product_image=image,product_start_price=starting_price,product_current_price=starting_price,product_end_price=buy_now_price,product_mid_price=reserve_price,product_owner=member_id,product_winner=-1,product_bidders='',product_status='pending')
            record.save()
            messages.success(request,'Your Product has been sent to admin for approval!')
            return render(request,'accounts/form (1).html',{'id':member_id})
        else:
            messages.error(request,'Please mark thr checkbox ')
            return render(request,'accounts/form (1).html',{'id':member_id})

       
    return render(request,'accounts/form (1).html',{'id':member_id})


def live(request,member_id):
    records= Products.objects.filter(product_owner=member_id,product_status='live')
    total=[]
    for record in records:
        total.append(record.product_bids_count)
    
    if len(records)>0:
        bids=sum(total)
        good=True
    else:
        bids=0

        good=False


    return render(request,'accounts/live-auctions.html',{'records':records,'id':member_id,'good':good,'items':len(records),'bids':bids})


def inactive(request,member_id):
    records= Products.objects.filter(product_owner=member_id,product_status='inactive')
    if len(records)>0:
        good=True
    else:
        good=False
    return render(request,'accounts/inactive.html',{'records':records,'id':member_id,'good':good,'items':len(records)})

def pending(request,member_id):
    records= Products.objects.filter(product_owner=member_id,product_status='pending')
    return render(request,'accounts/pending-approval.html',{'records':records,'items':len(records),'id':member_id})

def sold(request,member_id):
    records= Products.objects.filter(product_owner=member_id,product_status='sold')
    total=[]
    for record in records:
        total.append(record.product_current_price)
    if len(records)>0:
        totals=sum(total)
        max1=max(total)
        avg=sum(total)/len(total)

        good=True
    else:
        totals=0
        max1=0
        avg=0
        good=False
    return render(request,'accounts/sold-items.html',{'id':member_id,'items':len(records),'revenue':totals,'max':max1,'avg':avg,'records':records,'good':good})

def withdraw(request,member_id,product_id):
    product=Products.objects.get(product_id=product_id)
    product.product_status='inactive'
    product.save()
    return render(request,'accounts/pending-approval.html',{'id':member_id,'success':True})

def delete(request,member_id,product_id,token):
    if token=='true':
        product=Products.objects.get(product_id=product_id)
        product.delete()
        return render(request,'accounts/live-auctions.html',{'id':member_id,'success':True})
    else:
        return render(request,'accounts/live-auctions.html',{'id':member_id,'confirm':True,'product_id':product_id})



    
    




