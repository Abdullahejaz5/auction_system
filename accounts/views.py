from django.shortcuts import render
from django.http import HttpResponse
from .models import Members,Products,Messages
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg
from django.utils import timezone
from django.core.mail import send_mail

def landing(request):
    return render(request,'accounts/homepage.html')

def login(request):
    if request.method=='POST':
        email=request.POST.get('email','')
        email=email.lower()
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
        email=email.lower()
        contact=request.POST.get('phoneNumber','')
        p1=request.POST.get('password','')
        p2=request.POST.get('confirmPassword','')
        role=request.POST.get('role','')
 
        members=Members.objects.filter(email=email)
        if len(members)>0:
            messages.error(request,'user already exists')
            return render(request,'accounts/signup.html')
        elif len(name)<=0 or len(email)<=12 or len(contact)<11 or len(p1)<=6 or len(p2)<=6 or len(role)<5:
            messages.error(request,'Please fill all the details caerfully!')
            return render(request,'accounts/signup.html')
        elif p1!=p2:
            messages.error(request,'Please choose the password caerfully!')
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
        messages=Messages.objects.filter(seller_id=member_id).order_by('-time')
        if len(messages)>=5:
            messages=messages[:5]

        return render(request,'accounts/dashboard_seller.html',{'id':member_id,'pendings':pendings,'live':live,'sold':sold,'inactive':inactive,'name':name,'updates':messages})
    

    if record.role=='bidder':
        name=record.name
        live=len(Products.objects.filter(product_status='live'))
        win=len(Products.objects.filter(product_winner_id=member_id))
        messages=len(Messages.objects.filter(seller_id=member_id))
        print(live,win,messages)
        return render(request,'accounts/bidderDashboard.html',{'name':name,'id':member_id,'live':live,'winnings':win,'messages':messages})    


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


def categories(request,member_id):
    categories = Products.objects.filter(product_status="live").values_list('product_category', flat=True).distinct()
    categories_details=[]
    live=0
    for category in categories:
        cat=len(Products.objects.filter(product_status="live",product_category=category))
        live+=cat
        cat1=len(Products.objects.filter(product_category=category))
        avg_price = Products.objects.filter(product_category=category,product_status="live").aggregate(avg_price=Avg('product_current_price'))['avg_price']
        categories_details.append([category,cat,cat1,avg_price])
    members=len(Members.objects.filter(role='bidder'))
    return render(request,'accounts/allAuctions.html',{'id':member_id,'categories_count':len(categories),'categories':categories_details,'live':live,'members':members})

   

def live_to_show(request,member_id,category):
    print(member_id,category)
    live=Products.objects.filter(product_category=category,product_status='live')
    return render(request,'accounts/bidderCatagoryDetail.html',{'category':category,'id':member_id,'live':len(live),'products':live})


def winnings(request,member_id):
    products=Products.objects.filter(product_status='sold',product_winner_id=member_id)
    if len(products)>0:
        true=True
    else:
        true=False
    win=len(products)

    return render(request,'accounts/bidderWonAuctions.html',{'id':member_id,'win':win,'true':true,'products':products})

def messages_to_show(request,member_id):
    print(member_id)
    return HttpResponse('hey these are your messages')

def show_details(request,member_id,product_id):
    product=Products.objects.get(product_id=product_id)
    if request.method=='POST':
        bid=request.POST.get('bid_amount','')

        if int(bid)<=int(product.product_current_price):
            less=True
            return render(request,'accounts/product_details.html',{'id':member_id,'product':product,'less':less})


        elif int(bid)>int(product.product_end_price):
            won=True
            product.product_bidders=product.product_bidders+f',{member_id}'
            product.product_current_price=bid
            product.product_winner_id=member_id
            product.product_winner=Members.objects.get(member_id=member_id).name
            product.product_bids_count=product.product_bids_count+1
            product.product_status='sold'
            product.product_end_date=timezone.now().date()
            print(timezone.now().date())
            owner=Members.objects.get(member_id=product.product_owner).contact
            winner=Members.objects.get(member_id=member_id).email
            send_mail(subject='Auction Update',message=f'Congrats! You won the bid of product named {product.product_name} for ${int(bid)}. Kindly contact on {owner} 🎉',from_email='auctionsystem786@gmail.com',   recipient_list=[winner],fail_silently=False,)

            product.save()
            message=Messages(seller_id=member_id,time=timezone.now(),message_head='YOU WON THE BIT',message=f'Congratulations you have won the product,named {product.product_name}',type='winnings')
            message.save()
            customer=Members.objects.get(member_id=member_id).name
            msg=Messages(seller_id=product.product_owner,message_head='Sold Out',message=f'Your product named {product.product_name} has been sold out to {customer} for ${int(bid)}',type='sold')
            msg.save()
            return render(request,'accounts/product_details.html',{'id':member_id,'product':product,'won':won})

        elif int(bid)<int(product.product_end_price):
            save=True
            product.product_bidders=product.product_bidders+f',{member_id}'
            product.product_current_price=bid
            product.product_bids_count=product.product_bids_count+1
            product.save()
            customer=Members.objects.get(member_id=member_id).name
            msg=Messages(seller_id=product.product_owner,message_head='New bid',message=f'New bid of ${int(bid)} on your product named {product.product_name} is received from {customer}',type='bid')
            msg.save()
            return render(request,'accounts/product_details.html',{'id':member_id,'product':product,'save':save})
    
    return render(request,'accounts/product_details.html',{'id':member_id,'product':product})


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
