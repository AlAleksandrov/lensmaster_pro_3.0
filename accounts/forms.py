from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from accounts.models import Profile

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        label='First Name',
        help_text='Enter your first name',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'John',
            }
        )
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        label='Last Name',
        help_text='Enter your last name',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Doe',
            }
        )
    )
    email = forms.EmailField(
        required=True,
        label='Email Address',
        help_text='Enter valid email address',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'john.doe@example.com',
            }
        )
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'username': 'Username',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email Address',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }

        help_texts = {
            'username': 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
            'password1': 'Your password must contain at least 8 characters.',
            'password2': 'Enter the same password as before, for verification.',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('A user with this username already exists.')
        return username

class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        required=False,
        label='First Name',
        help_text='Enter your first name',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'placeholder': 'John',
            }
        )
    )
    last_name = forms.CharField(
        max_length=50, required=False,
        label='Last Name',
        help_text='Enter your last name',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'placeholder': 'Doe',
            }
        )
    )
    email = forms.EmailField(
        required=False,
        label='Email Address',
        help_text='Enter your email address',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'placeholder': 'john.doe@example.com',
            }
        )
    )
    username = forms.CharField(
        required=False,
        label='Username',
        help_text='Your username cannot be changed.',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'placeholder': 'john_doe',
                'readonly': 'readonly',
            }
        )
    )

    class Meta:
        model = Profile
        fields = ('profile_picture', 'phone', 'bio', 'city')
        labels = {
            'profile_picture': 'Upload a profile photo (JPEG, PNG or WebP, max 5MB).',
            'phone': 'Phone Number',
            'bio': 'A short description about yourself.',
            'city': 'The city you are based in.',
        }
        help_texts = {
            'phone': 'Select your country code and enter your local phone number.',
            'bio': 'Tell us about yourself (at least 10 characters).',
            'city': 'Enter your city name.',
        }
        widgets = {
            'phone': forms.TextInput(
                attrs={
                    'id': 'profile-phone-input',
                    'type': 'tel',
                    'class': 'form-control bg-dark text-white border-secondary',
                    'placeholder': 'Your phone number',
                }
            ),
            'bio': forms.Textarea(
                attrs={
                    'class': 'form-control bg-dark text-white border-secondary',
                    'rows': 4,
                    'placeholder': 'Tell us about yourself...',
                }
            ),
            'city': forms.TextInput(
                attrs={
                    'class': 'form-control bg-dark text-white border-secondary',
                    'placeholder': 'Your city...',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['username'].initial = self.instance.user.username

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        if commit:
            user.save()
            profile.save()
        return profile