from django_mako_plus import view_function
from django import forms
from django.http import HttpResponseRedirect
from formlib.form import Formless

@view_function
def process_request(request):
    #process the form_method
    form = TestForm(request)
    if form.is_valid():
        #once you get here, you cannot yell at the user anymore
        #this area is for an absolutely perfect form
        #ready to be processed

        #work of the form - create user, login user, purchase
        return HttpResponseRedirect('/account/formtest/')

    #render the form
    context = {
        'form': form,
    }
    return request.dmp_render('formtest.html', context)


class TestForm(Formless):
    def init(self):
        self.fields['email'] = forms.CharField(label='Email')
        self.fields['age'] = forms.IntegerField(label='Your age')
        self.fields['renewal_date'] = forms.DateField(help_text='Enter a date between now and 4 weeks (default 3)')

    def clean_username(self):
        username = self.cleaned_data.get('email')

        #check if this email alrady exists
        return username

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 18:
            #show an error message: no soup for your
            raise forms.ValidationError('LESS THAN 18.')
        return age

    # def clean(self):
    #     #for checking the entire form - usually two variables at once
    #     #"password" and "password2"
    #     pw1 = self.cleaned_data.get('password')
    #     pw2 = self.cleaned_data.get('password2')
    #
    #     if pw1 = pw2:
    #         #yell at the user
    #
    #     return self.cleaned_data
