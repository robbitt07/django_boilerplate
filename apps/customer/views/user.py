from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import View


from apps.customer.forms import UserActivateResetPasswordForm
from apps.customer.tokens import account_activation_token
from utils.mixins import CustomerViewMixin

User = get_user_model()


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('login_user'))


def login_user(request):
    form = AuthenticationForm()
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if user.is_admin:
                    return HttpResponseRedirect(reverse('customer:admin_landing'))
                return HttpResponseRedirect(reverse('customer:dashboard'))
            else:
                return render(request, 'customer/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'customer/login.html', {'error_message': 'Invalid login', 'form' : form})
    return render(request, 'customer/login.html', {'form' : form})


class UserActivateView(View):

    def get(self, request, uidb, token, *args, **kwargs):
        ## Get User for Activation
        try:
            uid = force_text(urlsafe_base64_decode(uidb))
            # Filter for those who are not yet activated
            user_obj = User.objects.get(
                pk=uid, email_confirmed=False
            )
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user_obj = None

        if user_obj is not None and account_activation_token.check_token(user_obj, token):
            form = UserActivateResetPasswordForm(user=user_obj)
            context = {'form': form}
            return render(request, 'customer/user/user_activation_reset_password.html', context)

        else:
            # Invalid link
            return render(request, 'customer/user/user_activation_invalid.html')

    def post(self, request, uidb, token, *args, **kwargs):
        ## Get User for Activation
        try:
            uid = force_text(urlsafe_base64_decode(uidb))
            # Filter for those who are not yet activated
            user_obj = User.objects.get(
                pk=uid, email_confirmed=False
            )
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user_obj = None

        if user_obj is not None and account_activation_token.check_token(user_obj, token):
            form = UserActivateResetPasswordForm(user=user_obj, data=request.POST)

            if form.is_valid():
                # If passwords meet requirements and are correct then activate
                # user, set password, login and redirect to main landing page
                form.save()
                user_obj.active = True
                user_obj.save()
                login(request, user_obj)

                ## Direct to landing page
                return HttpResponseRedirect(reverse('customer:dashboard'))

            ## Form is invalid, render form again
            return render(request, 'customer/user/user_activation_reset_password.html', context={'form': form})


class UserDashboardLanding(CustomerViewMixin, View):

    def get(self, *args, **kwargs):
        return render(self.request, 'customer/dashboard.html')


class UserAPIView(View):

    def get(self, *args, **kwargs):
        context = {'api_token': self.request.user.auth_token}
        return render(self.request, 'customer/user_api.html', context=context)