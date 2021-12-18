from django.forms import ModelForm, fields
from . models import Room
from django.contrib.auth.models import User

# Create a room
class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']