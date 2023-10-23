from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    first_name = forms.CharField(label='Name', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(label='Course', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        labels = {
            'username': 'Matrikel Number',
            'first_name': 'Name',
            'last_name': 'Course',
        }


    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class':'form-control'})
        self.fields['password1'].widget.attrs.update({'class':'form-control'})
        self.fields['password2'].widget.attrs.update({'class':'form-control'})