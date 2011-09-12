from django.db import models
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.contrib.sites.models import Site, RequestSite

from random import randrange

# stolen from
# https://github.com/workmajj/django-unique-random/blob/master/unique_random/models.py
CHARSET = '0123456789ABCDEFGHJKMNPQRSTVWXYZabcdefghijklmnopqrstuvwxyz'
LENGTH = 32
MAX_TRIES = 1024

class UserInvitation(models.Model):
    hash = models.CharField(_('hash'), editable=False, max_length=255, unique=True)
    username = models.CharField(_('username'), max_length=30, blank=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('e-mail address'), blank=False, unique=True)
    is_used = models.BooleanField(_('already used'), default=False)
    used_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    user = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return '%s|%s' % (self.email, self.hash)

    def save(self, *args, **kwargs):
        new_invite = self.pk is None
        """
        Upon saving, generate a code by randomly picking LENGTH number of
        characters from CHARSET and concatenating them. If code has already
        been used, repeat until a unique code is found, or fail after trying
        MAX_TRIES number of times. (This will work reliably for even modest
        values of LENGTH and MAX_TRIES, but do check for the exception.)
        Discussion of method: http://stackoverflow.com/questions/2076838/
        """
        if new_invite:
            loop_num = 0
            unique = False
            while not unique:
                if loop_num < MAX_TRIES:
                    new_code = ''
                    for i in xrange(LENGTH):
                        new_code += CHARSET[randrange(0, len(CHARSET))]
                    if not UserInvitation.objects.filter(hash=new_code):
                        self.hash = new_code
                        unique = True
                    loop_num += 1
                else:
                    raise ValueError("Couldn't generate a unique code.")

        if new_invite:
            if Site._meta.installed:
                site = Site.objects.get_current()
            else:
                site = None

            link = 'http://adhocid.die-welt.net/join/%s' % self.hash

            ctx_dict = {'link': link,
                        'invitation': self,
                        'site': site}

            s = render_to_string('invite_email_subject.txt', ctx_dict)
            # Email subject *must not* contain newlines
            s = ''.join(s.splitlines())
          
            m = render_to_string('invite_email_body.txt', ctx_dict).strip()
  
            r = [self.email]
  
            send_mail(subject=s, message=m, from_email=None, recipient_list=r, fail_silently=False)

        super(UserInvitation, self).save(*args, **kwargs)
