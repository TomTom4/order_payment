from django import forms
from zxcvbn_password.fields import PasswordField, PasswordConfirmationField
from zxcvbn_password import zxcvbn


class RegisterForm(forms.Form):
	password1 = PasswordField(label='password here')
	password2 = PasswordConfirmationField(confirm_with='password1')


	def clean(self):
		password = self.cleaned_data.get('password1')
		passwordVerification = self.cleaned_data.get('password2')

		if password:
			score = zxcvbn(password, [passwordVerification])['score']
		return self.cleaned_data
