from django import forms
from monitoring.models import Usertype_Ref,Type,Pool,ipaddress_ref
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm,AuthenticationForm

class SignUpForm(UserCreationForm):
    username = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs={'class': 'form-control','id':'username', 'autocomplete':'off','placeholder':'username'}), max_length=30, required=True, error_messages={ 'invalid': ("This value must contain only letters, numbers and underscores.") })
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','autocomplete':'off','placeholder':'First Name'}),max_length=30, required=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','autocomplete':'off','placeholder':'Last Name'}),max_length=30, required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','autocomplete':'off'}),required=True, max_length=30, label=("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','autocomplete':'off'}),required=True, max_length=30, label=("Re-type Password"))
    #email = forms.EmailField(max_length=254,required=False)

    def clean_username(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(("The username is unavailable."))

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(("The two password fields did not match."))
        return self.cleaned_data

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class RegisterPool(forms.ModelForm):
    pool_name = forms.CharField(max_length = 250, required= True, label=('Pool Name'),widget = forms.TextInput( attrs = {'class': 'form-control','id': 'pool_name'}))
    pool_location = forms.CharField(max_length = 250, required= True, label=('Pool Location'),widget = forms.TextInput( attrs = {'class': 'form-control','id': 'pool_location'}))
    pool_length = forms.DecimalField(max_digits=8, decimal_places=2, required= True, label=('Pool Length'),widget = forms.TextInput( attrs = {'class': 'form-control','id': 'pool_length'}))
    pool_width = forms.DecimalField(max_digits=8, decimal_places=2, required= True, label=('Pool Width'),widget = forms.TextInput( attrs = {'class': 'form-control','id': 'pool_width'}))
    pool_depth = forms.DecimalField(max_digits=8, decimal_places=2, required= True, label=('Pool Depth'),widget = forms.TextInput( attrs = {'class': 'form-control','id': 'pool_depth'}))
    pool_availabletimestart = forms.TimeField( required= True, label=('Open Time'),widget = forms.TextInput( attrs = {'class': 'form-control timepicker','id': 'pool_availabletimestart'}))
    pool_availabletimeend = forms.TimeField( required= True, label=('Close Time'),widget = forms.TextInput( attrs = {'class': 'form-control timepicker','id': 'pool_availabletimeend'}))
    pool_ip = forms.ModelChoiceField(queryset=ipaddress_ref.objects.only('ipaddress'), required=True, label=('IP address'),widget=forms.Select(attrs={'class': 'form-control','autocomplete':'off', 'id': 'pool_ip'}))
    class Meta:
        model = Pool
        fields = ('pool_name','pool_location','pool_length','pool_width','pool_depth','pool_availabletimestart','pool_availabletimeend','pool_ip')

class SignUpType(forms.ModelForm):
    type = forms.ModelChoiceField(queryset=Usertype_Ref.objects.all(), required=True,widget=forms.Select(attrs={'class': 'form-control','autocomplete':'off'}))

    class Meta:
        model = Type
        fields = ('type',)



class NewPool(forms.ModelForm):
    pool = forms.ModelChoiceField(queryset=Pool.objects.all(), required=True,widget = forms.Select(attrs ={'class': 'form-control'}))
    reservedtime = forms.CharField(max_length = 20,required=True,label= ("Start of Maintenance"),widget = forms.TextInput( attrs = {'class': 'form-control pull-right','id': 'reservationtime'}))

    class Meta:
        model = Pool
        fields = ('pool_location',)


class EditDetailsForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','autocomplete':'off','placeholder':'First Name'}),max_length=30, required=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','autocomplete':'off','placeholder':'Last Name'}),max_length=30, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label="Old Password", max_length=30, widget=forms.PasswordInput(attrs={'placeholder':'Enter current password','autocomplete':'off', 'class': 'form-control pw'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Enter new password','class': 'form-control pw','autocomplete':'off'}),required=True, max_length=30, label=("New Password"))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Re-enter new password','class': 'form-control pw','autocomplete':'off'}),required=True, max_length=30, label=("Re-type Password"))

class LoginForm(AuthenticationForm):
	username = forms.CharField(label="Username", max_length=20, widget=forms.TextInput(attrs={'autocomplete':'off', 'class': 'form-control'}))
	password = forms.CharField(label="Password", max_length=20, widget=forms.PasswordInput(attrs={'autocomplete':'off', 'id':'login_pw', 'class': 'form-control'}))
