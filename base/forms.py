from django.forms import ModelForm, fields
from . models import Room

# Create a room
class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']