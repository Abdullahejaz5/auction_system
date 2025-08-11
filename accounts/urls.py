from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing,name='landing_page'),
    path('login', views.login,name='login'),
    path('signup', views.signup,name='signup'),
    path('decision/<int:member_id>', views.decision,name='decision'),
    path('new_auction/<int:member_id>', views.new_auction,name='new_auction'),
    path('live/<int:member_id>', views.live,name='live'),
    path('inactive/<int:member_id>', views.inactive,name='inactive'),
    path('pending/<int:member_id>', views.pending,name='pending'),
    path('sold/<int:member_id>', views.sold,name='sold'),
    path('withdraw/<int:member_id>/<int:product_id>', views.withdraw,name='withdraw'),
    path('delete/<int:member_id>/<int:product_id>/<str:token>', views.delete,name='delete'),
]
