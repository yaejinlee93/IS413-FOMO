from django_mako_plus import view_function
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django import forms
from formlib.form import Formless
from account import models as amod
import re

@view_function
def process_request(request):
    #process the form_method
    form = SignupForm(request)

    if form.is_valid():
        #once you get here, you cannot yell at the user anymore
        #this area is for an absolutely perfect form
        #ready to be processed

        form.commit()

        #work of the form - create user, login user, purchase
        return HttpResponseRedirect('/account/index/')

    #render the form
    context = {
        'form': form,
    }
    return request.dmp.render('signup.html', context)

class SignupForm(Formless):
    def init(self):
        self.fields['email'] = forms.CharField(label='Email')
        self.fields['password'] = forms.CharField(widget=forms.PasswordInput,label='Password', help_text='longer than 8 characters, contain number')
        self.fields['password2'] = forms.CharField(widget=forms.PasswordInput,label='Confirm Password')
        self.fields['first_name'] = forms.CharField(label='First Name')
        self.fields['last_name'] = forms.CharField(label='Last Name')
        self.fields['address'] = forms.CharField(label='Street Address')
        self.fields['city'] = forms.CharField(label='City')
        self.fields['state'] = forms.CharField(label='State')
        self.fields['zipcode'] = forms.IntegerField(label='Zipcode')


    def clean_email(self):
        email = self.cleaned_data.get('email')
        #check if this email alrady exists
        checkemail = amod.User.objects.filter(email=email).count()
        if checkemail > 0:
            raise forms.ValidationError('Email already exist.')

        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError('Password has to be longer than 8 charachters.')

        if not re.search('\d+', password):
            raise forms.ValidationError('Password has to contain number.')

        return password

    def clean(self):
        #for checking the entire form - usually two variables at once
        #"password" and "password2"
        pw1 = self.cleaned_data.get('password')
        pw2 = self.cleaned_data.get('password2')

        if pw1 != pw2:
            #yell at the user
            raise forms.ValidationError({'password2':['Password not matching.']})

        return self.cleaned_data

    def commit(self):
        user = amod.User()
        user.email = self.cleaned_data.get('email')
        user.set_password(self.cleaned_data.get('password'))
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('first_name')
        user.address = self.cleaned_data.get('address')
        user.city = self.cleaned_data.get('city')
        user.state = self.cleaned_data.get('state')
        user.zipcode = self.cleaned_data.get('zipcode')

        user.save()

        user = authenticate(email=self.cleaned_data.get('email'), password=self.cleaned_data.get('password'))
        if user is not None:
            login(self.request, user)
