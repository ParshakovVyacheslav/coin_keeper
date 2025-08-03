from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from .forms import UserRegistrationForm, LoginForm
from .models import CustomUser


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


def register(request):
    form = UserRegistrationForm()

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            current_site = get_current_site(request)
            mail_subject = _("Activate your account.")

            message = render_to_string('accounts/email_activation/activate_email_message.html', {
                    'user': form.cleaned_data['username'],
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token':  default_token_generator.make_token(user),
                })
            to_email = form.cleaned_data['email']
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            messages.success(request, _('Account created successfully. Please check your email to activate your account.'))
            return render(request, 'accounts/register.html',{'form': form })
        else:
            messages.error(request, _('Account creation failed. Please try again.'), extra_tags='danger')       

    return render(request, 'accounts/register.html',{'form': form })


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except:
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'accounts/email_activation/activation_successful.html')
    else:
        return render(request, 'accounts/email_activation/activation_unsuccessful.html')
    

class CustomLoginView(LoginView):
    template_name='accounts/login.html'
    form_class=LoginForm
    redirect_authenticated_user=True
    
    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super().form_valid(form)