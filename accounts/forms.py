from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import check_password

from scraping.models import City, Language

User = get_user_model()


class UserLoginForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email').strip()
        password = self.cleaned_data.get('password').strip()

        if email and password:
            qs = User.objects.filter(email=email)
            if not qs.exists():
                raise forms.ValidationError('Такого пользователя нет!')
            if not check_password(password, qs[0].password):
                raise forms.ValidationError('Пароль не верный!')
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError('Данный аккаунт заблокирован')
        return super(UserLoginForm, self).clean(*args, **kwargs)


class UserRegistrationForm(forms.ModelForm):
    email = forms.CharField(label='Введите email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Введите пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Подтвердите пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        data = self.cleaned_data
        if data.get('password') != data.get('password2'):
            raise forms.ValidationError('Пароли не совпадают')
        return data.get('password2')


class UserUpdateForm(forms.Form):
    city = forms.ModelChoiceField(queryset=City.objects.all(),
                                  to_field_name='slug', required=True,
                                  label='Город',
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    language = forms.ModelChoiceField(queryset=Language.objects.all(),
                                      label='Специальность',
                                      to_field_name='slug', required=True,
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    send_email = forms.BooleanField(required=False, widget=forms.CheckboxInput, label='Хочу получать рассылку')

    class Meta:
        model = User
        fields = ('email', 'city', 'send_email')


class ContactForm(forms.Form):
    city = forms.CharField(required=True, label='Город', widget=forms.TextInput(attrs={'class': 'form-control'}))
    language = forms.CharField(required=True, label='Специальность', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(required=True, label='Введите email', widget=forms.EmailInput(attrs={'class': 'form-control'}))