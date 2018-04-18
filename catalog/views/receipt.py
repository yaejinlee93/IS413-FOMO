from django.http import HttpResponseRedirect
from django_mako_plus import view_function
from datetime import datetime
from django.contrib.auth.decorators import login_required
from catalog import models as cmod
#email
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags
# from django.template import Context, Template, RequestContext
# from django.shortcuts import render
#django SEND_MAIL
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string

@login_required
@view_function
def process_request(request,order:cmod.Order=None):
    person = None
    if order is None:
        order = cmod.Order.objects.filter(user=request.user,status='sold').order_by('-id')[0]
        if order is None:
            return HttpResponseRedirect('/catalog/cart/')
    else:
        person = order.user
    if order.user != request.user:
        if not request.user.is_staff:
            return HttpResponseRedirect('/catalog/cart/')
    if order.order_date is not None:
        order.order_date = '{:%m/%d/%Y}'.format(order.order_date)
    cart = cmod.OrderItem.objects.filter(order=order, status='active').exclude(description='TaxAmount')
    context = {
        'order' : order,
        'cart' : cart,
    }

    #email the receipt
    # if send == 'yes':
    #     email(request,order)

    return request.dmp.render('receipt.html', context)

# @login_required
# @view_function
# def email(request,order:cmod.Order=None):
#     if order is None:
#         return HttpResponseRedirect('/catalog/cart/')
#     if order.user != request.user:
#         if not request.user.is_staff:
#             return HttpResponseRedirect('/catalog/cart/')
#
#     # subject, from_email, to = 'FOMO Receipt', 'thefomostore@me.com', request.user.email
#     # html_content = render_to_string('catalog/receipt.html', mycontext) # render with dynamic value
#     # text_content = strip_tags(html_content) # Strip the html tag. So people can see the pure text at least.
#     # # create the email, and attach the HTML version as well.
#     # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
#     # msg.attach_alternative(html_content, "text/html")
#     # msg.send()
#     cart = cmod.OrderItem.objects.filter(order=order, status='active').exclude(description='TaxAmount')
#
#     mycontext = {
#         'order' : order,
#         'cart' : cart,
#         'request' : request,
#     }
#
#     #THE DJANGO WAY OF EMAIL
#     html_content = render_to_string('catalog/printreceipt.html', mycontext) # render with dynamic value
#     # send_mail(
#     #     'FOMO Receipt Number ' +str(order.id),
#     #     html_content,
#     #     'mail@thefomostore.me',
#     #     [request.user.email],
#     #     fail_silently=False,
#     # )
#
#     #THE OTHER DJANGO WAY OF EMAIL
#     subject = 'FOMO Receipt #' + str(order.id)
#     to = [order.user.email,]
#     email = EmailMessage(
#         subject,
#         html_content,
#         'thefomostore.me@gmail.com',
#         to,
#         #reply_to=['another@example.com'],
#         #headers={'Message-ID': 'foo'},
#     )
#     email.content_subtype = 'html'
#
#     email.send(fail_silently=False)
#
#     return HttpResponseRedirect('/catalog/receipt/' + str(order.id) + '/')
