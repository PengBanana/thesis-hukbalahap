from django import forms

class AddUserForm(forms.Form):
   user = forms.CharField(
        max_length = 6,
        widget=forms.TextInput(
            attrs={
            'class': 'form-control'
            }

   ))
   ##password = forms.CharField(widget = forms.PasswordInput())
