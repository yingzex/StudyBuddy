from django.contrib import admin

# Register your models here.
from .models import Room, Message, Topic

admin.site.register(Room) # after register, can see the model in bulit-in admin panel
admin.site.register(Message)
admin.site.register(Topic)