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
    form = LoginForm(request)

    if form.is_valid():
        form.commit()
        return HttpResponseRedirect('/account/')

    #render the form
    context = {
        'form': form,
    }
    return request.dmp.render('login.html', context)

class LoginForm(Formless):
    def init(self):
        #self.fields['type'] = forms.ChoiceField() 
        self.fields['email'] = forms.CharField(label='Email')
        self.fields['password'] = forms.CharField(widget=forms.PasswordInput,label='Password')
        self.user = None

    def clean(self):

        self.user = authenticate(email=self.cleaned_data.get('email'), password=self.cleaned_data.get('password'))

        if self.user is None:
            raise forms.ValidationError('Invalid email or password.')
        return self.cleaned_data

    def commit(self):
        login(self.request, self.user)
