from django import forms
from .models import Actor


class ActorForm(forms.ModelForm):
    class Meta:
        model = Actor
        fields = ['name', 'image']
