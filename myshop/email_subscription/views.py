from django.shortcuts import render
from common.decorators import ajax_required
from .models import EmailContact
from django.http import JsonResponse
from django.core.validators import validate_email
from django import forms

# Create your views here.
#
# def email_subscribe(request):
#     # List of active comments for this post
#
#     new_subscriber = None
#
#     if request.method == 'POST':
#         subscription_form = SubscriptionForm(data=request.POST)
#         if subscription_form.is_valid():
#             # Create Comment object but don't save to database yet
#             new_subscriber = subscription_form.save(commit=False)
#             # Save the comment to the database
#             new_subscriber.save()
#     else:
#         subscription_form = SubscriptionForm()
#
#     return render(request,
#                   'subscribtion.html',
#                   {
#                    'new_subscriber': new_subscriber,
#                    'subscription_form': subscription_form,
#                    },
#                     using=None)

@ajax_required
def email_subscribe(request):
    #     if request.method == 'POST':
    #         subscription_form = SubscriptionForm(data=request.POST)
    #         if subscription_form.is_valid():
    #             # Create Comment object but don't save to database yet
    #             new_subscriber = subscription_form.save(commit=False)
    #             # Save the comment to the database
    #             new_subscriber.save()
    #     else:
    #         subscription_form = SubscriptionForm()
    email = request.POST.get('email')
    if email:
        try:
            validate_email(email)
            if EmailContact.objects.filter(email=email).exists():
                return JsonResponse({'status': '510', 'message': "this email existed before"})

            EmailContact.objects.get_or_create(email=email)
            return JsonResponse({'status': 'ok'})
        except forms.ValidationError:
            return JsonResponse({'status': '502'})

    return JsonResponse({'status':'ko'})