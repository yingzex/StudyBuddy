from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here. (database table)
"""
create python class, a class represents a table in database
a attribute represents a column
a instance represents a row
"""

class User(AbstractUser):
    name = models.CharField(max_length=200,null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)
    avatar = models.ImageField(null=True, default="avatar.svg")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Topic(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Room(models.Model): # inherit from models (make the class a django model)
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)# topic and room: one to many
    name = models.CharField(max_length=200)
    # null: value can be null, blank: when submitting a form, the form can be empty
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True) # user and room: many to many relationship
    # every time the save method is called, take a timestamp
    updated = models.DateTimeField(auto_now=True)
    # only the first tie save or create this instance, take a timestamp
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # order by descending updated time, then created time
        ordering = ['-updated', '-created']

    def __str__(self):
        return str(self.name)

"""
Room and Message: one to many (one room, many messages)
"""
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # user and msg: one to many relationship (when user deleted, delete his all msg)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) # when room deleted, delete all messages in the room
    body = models.TextField()
    # every time the save method is called, take a timestamp
    updated = models.DateTimeField(auto_now=True)
    # only the first tie save or create this instance, take a timestamp
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # order by descending updated time, then created time
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50] # only 50 chars in msg