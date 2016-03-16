import account.views

import myprofile.forms

from account.mixins import LoginRequiredMixin

from django.views.generic.edit import FormView

from account.forms import SettingsForm

from django.contrib import auth, messages

from django.utils.translation import ugettext_lazy as _

from account.models import SignupCode, EmailAddress, EmailConfirmation, Account, AccountDeletion


class SignupView(account.views.SignupView):

   form_class = myprofile.forms.SignupForm

   def after_signup(self, form):
       self.create_profile(form)
       super(SignupView, self).after_signup(form)

   def create_profile(self, form):
       profile = self.created_user.userprofile  # replace with your reverse one-to-one profile attribute
       profile.birthdate = form.cleaned_data["birthdate"]
       profile.save()

class SettingsView(LoginRequiredMixin, FormView):



        def get_form_class(self):
            # @@@ django: this is a workaround to not having a dedicated method
            # to initialize self with a request in a known good state (of course
            # this only works with a FormView)
            self.primary_email_address = EmailAddress.objects.get_primary(self.request.user)
            return super(SettingsView, self).get_form_class()

        def get_initial(self):
            initial = super(SettingsView, self).get_initial()
            if self.primary_email_address:
                initial["email"] = self.primary_email_address.email
            initial["timezone"] = self.request.user.account.timezone
            initial["language"] = self.request.user.account.language
            initial["birthdate"] = self.request.user.userprofile.birthdate
            return initial



        def update_settings(self, form):
            self.update_email(form)
            self.update_account(form)

        def update_email(self, form, confirm=None):
            user = self.request.user
            if confirm is None:
                confirm = settings.ACCOUNT_EMAIL_CONFIRMATION_EMAIL
            # @@@ handle multiple emails per user
            email = form.cleaned_data["email"].strip()
            if not self.primary_email_address:
                user.email = email
                EmailAddress.objects.add_email(self.request.user, email, primary=True, confirm=confirm)
                user.save()
            else:
                if email != self.primary_email_address.email:
                    self.primary_email_address.change(email, confirm=confirm)

        def get_context_data(self, **kwargs):
            ctx = super(SettingsView, self).get_context_data(**kwargs)
            redirect_field_name = self.get_redirect_field_name()
            ctx.update({
                "redirect_field_name": redirect_field_name,
                "redirect_field_value": self.request.POST.get(redirect_field_name, self.request.GET.get(redirect_field_name, "")),
            })
            return ctx

        def update_account(self, form):
            fields = {}
            if "timezone" in form.cleaned_data:
                fields["timezone"] = form.cleaned_data["timezone"]
            if "language" in form.cleaned_data:
                fields["language"] = form.cleaned_data["language"]
            if "birthdate" in form.cleaned_data:
                fields["birthdate"] = form.cleaned_data["birthdate"]
            if fields:
                account = self.request.user.account
                for k, v in fields.items():
                    setattr(account, k, v)
                account.save()

        def get_redirect_field_name(self):
            return self.redirect_field_name

        def get_success_url(self, fallback_url=None, **kwargs):
            if fallback_url is None:
                fallback_url = settings.ACCOUNT_SETTINGS_REDIRECT_URL
            kwargs.setdefault("redirect_field_name", self.get_redirect_field_name())
            return default_redirect(self.request, fallback_url, **kwargs)
