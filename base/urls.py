# urls for this specific app
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),

    path('', views.home, name='home'), # when user input empty url, trigger function home
    path('room/<str:pk>/', views.room, name='room'), # when user input this url, trigger function room 
    # also pass argument pk into function room (pk is in the url, is string type)
    # user can pass in dynamic value, eg. room/1 
    path('profile/<str:pk>/', views.userProfile, name='user-profile'),

    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),

    path('update-user/', views.updateUser, name="update-user"),
]