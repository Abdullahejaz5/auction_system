from django.db import models

class Members (models.Model):
    member_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50,default='')
    email=models.CharField(max_length=100,default='')
    password=models.CharField(max_length=100,default='')
    contact=models.IntegerField()
    role=models.CharField(max_length=50,default='')

    def __str__(self):
        return self.name