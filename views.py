from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.template import RequestContext

from preseeded_invite.forms import InvitedUserCreationForm, InvitedUserCreationFormPasswordOnly, InviteCSVForm
from preseeded_invite.models import UserInvitation

from urllib import quote
from hashlib import sha1
import random, base64

from datetime import datetime
from csv import reader

def join(request, hash, **kwargs):
    try:
        invite = UserInvitation.objects.get(hash=hash, is_used=False)
    except:
        return render_to_response('invite_join_fail.html')

    email = invite.email
    if invite.username:
        formclass = InvitedUserCreationFormPasswordOnly
        name = "%s %s" % (invite.first_name, invite.last_name)
    else:
        formclass = InvitedUserCreationForm
        name = None

    if request.method == 'POST': # If the form has been submitted...
        form = formclass(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            password = form.cleaned_data["password1"]
            username = invite.username or form.cleaned_data['username']

            new_user = User.objects.create_user(username, email, password)
            new_user.first_name = invite.first_name or form.cleaned_data['first_name']
            new_user.last_name = invite.last_name or form.cleaned_data['last_name']
            new_user.save()

            user = authenticate(username=username, password=password)
            auth_login(request, user)

            invite.is_used = True
            invite.used_date = datetime.now()
            invite.user = new_user
            invite.save()

            return HttpResponseRedirect('/') #user.get_absolute_url
    else:
        form = formclass() # An unbound form

    return render_to_response('invite_join.html', {
        'form': form,
        'name': name,
        'email': email,
    }, context_instance=RequestContext(request))

@login_required
def invite(request):
    if request.user.is_staff:
        if request.method == 'POST': # If the form has been submitted...
            form = InviteCSVForm(request.POST, request.FILES) # A form bound to the POST data
            if form.is_valid(): # All validation rules pass
                csv = reader(request.FILES['csv'], delimiter=',', quotechar='"')
                recipients = []
                for row in csv:
                    if len(row)==4:
                        (username, first, last, email) = row
                        invite = UserInvitation()
                        invite.username = username
                        invite.first_name = first
                        invite.last_name = last
                        invite.email = email
                        invite.save()
                        recipients.append(email)
                    elif len(row)==1:
                        (email) = row
                        invite = UserInvitation()
                        invite.email = email 
                        invite.save()
                        recipients.append(email)
                new_form = InviteCSVForm()
                recipients = ', '.join(recipients)
                return render_to_response('invite.html', {
                    'form': new_form,
                    'recipients': recipients,
                }, context_instance=RequestContext(request))
        else:
            form = InviteCSVForm() # An unbound form

        return render_to_response('invite.html', {
            'form': form,
            'recipients': '',
        }, context_instance=RequestContext(request))
    else:
        return HttpResponseForbidden(content='get outa here!')
