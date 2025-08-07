from django.db import models
from datetime import date,timedelta

def ten_days_later():
    return date.today() + timedelta(days=20)

class Members (models.Model):
    member_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50,default='')
    email=models.CharField(max_length=100,default='')
    password=models.CharField(max_length=100,default='')
    contact=models.IntegerField()
    role=models.CharField(max_length=50,default='')

    def __str__(self):
        return self.name
    

class Products (models.Model):
    product_id=models.AutoField(primary_key=True)
    product_name=models.CharField(max_length=50,default='')
    product_category=models.CharField(max_length=50,default='')
    product_desc=models.CharField(max_length=1000,default='')
    product_pub_date=models.DateField(default=date.today)
    product_end_date=models.DateField(default=ten_days_later)
    product_image=models.ImageField(upload_to='shop/images',default='')
    product_start_price= models.IntegerField(default=0)
    product_end_price=models.IntegerField(default=0)
    product_mid_price=models.IntegerField(default=0)
    product_owner=models.IntegerField(default=0)
    product_winner=models.IntegerField(default=None)
    product_bidders=models.CharField(max_length=200,default='')
    product_status=models.CharField(max_length=50,default='pending')
    
    def __str__(self):
        return self.product_name