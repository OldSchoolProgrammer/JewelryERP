from django import forms
from .models import Customer, Supplier


PHONE_PREFIX_CHOICES = [
    ('', 'Select...'),
    ('+1', '+1 (USA/Canada)'),
    ('+7', '+7 (Russia)'),
    ('+20', '+20 (Egypt)'),
    ('+27', '+27 (South Africa)'),
    ('+30', '+30 (Greece)'),
    ('+31', '+31 (Netherlands)'),
    ('+32', '+32 (Belgium)'),
    ('+33', '+33 (France)'),
    ('+34', '+34 (Spain)'),
    ('+36', '+36 (Hungary)'),
    ('+39', '+39 (Italy)'),
    ('+40', '+40 (Romania)'),
    ('+41', '+41 (Switzerland)'),
    ('+43', '+43 (Austria)'),
    ('+44', '+44 (UK)'),
    ('+45', '+45 (Denmark)'),
    ('+46', '+46 (Sweden)'),
    ('+47', '+47 (Norway)'),
    ('+48', '+48 (Poland)'),
    ('+49', '+49 (Germany)'),
    ('+51', '+51 (Peru)'),
    ('+52', '+52 (Mexico)'),
    ('+54', '+54 (Argentina)'),
    ('+55', '+55 (Brazil)'),
    ('+56', '+56 (Chile)'),
    ('+57', '+57 (Colombia)'),
    ('+60', '+60 (Malaysia)'),
    ('+61', '+61 (Australia)'),
    ('+62', '+62 (Indonesia)'),
    ('+63', '+63 (Philippines)'),
    ('+64', '+64 (New Zealand)'),
    ('+65', '+65 (Singapore)'),
    ('+66', '+66 (Thailand)'),
    ('+81', '+81 (Japan)'),
    ('+82', '+82 (South Korea)'),
    ('+84', '+84 (Vietnam)'),
    ('+86', '+86 (China)'),
    ('+90', '+90 (Turkey)'),
    ('+91', '+91 (India)'),
    ('+92', '+92 (Pakistan)'),
    ('+93', '+93 (Afghanistan)'),
    ('+94', '+94 (Sri Lanka)'),
    ('+95', '+95 (Myanmar)'),
    ('+98', '+98 (Iran)'),
    ('+212', '+212 (Morocco)'),
    ('+213', '+213 (Algeria)'),
    ('+216', '+216 (Tunisia)'),
    ('+234', '+234 (Nigeria)'),
    ('+254', '+254 (Kenya)'),
    ('+351', '+351 (Portugal)'),
    ('+352', '+352 (Luxembourg)'),
    ('+353', '+353 (Ireland)'),
    ('+354', '+354 (Iceland)'),
    ('+357', '+357 (Cyprus)'),
    ('+358', '+358 (Finland)'),
    ('+370', '+370 (Lithuania)'),
    ('+371', '+371 (Latvia)'),
    ('+372', '+372 (Estonia)'),
    ('+380', '+380 (Ukraine)'),
    ('+381', '+381 (Serbia)'),
    ('+385', '+385 (Croatia)'),
    ('+386', '+386 (Slovenia)'),
    ('+420', '+420 (Czech Republic)'),
    ('+421', '+421 (Slovakia)'),
    ('+966', '+966 (Saudi Arabia)'),
    ('+971', '+971 (UAE)'),
    ('+972', '+972 (Israel)'),
    ('+974', '+974 (Qatar)'),
]


class CustomerForm(forms.ModelForm):
    phone_prefix = forms.ChoiceField(
        choices=PHONE_PREFIX_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'})
    )

    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.HiddenInput(),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Parse existing phone into prefix and number
        if self.instance and self.instance.phone:
            phone = self.instance.phone
            # Try to find matching prefix
            for prefix, _ in PHONE_PREFIX_CHOICES:
                if prefix and phone.startswith(prefix):
                    self.fields['phone_prefix'].initial = prefix
                    self.fields['phone_number'].initial = phone[len(prefix):].strip()
                    break
            else:
                # No prefix found, put everything in number
                self.fields['phone_number'].initial = phone

    def clean(self):
        cleaned_data = super().clean()
        prefix = cleaned_data.get('phone_prefix', '')
        number = cleaned_data.get('phone_number', '')
        # Combine prefix and number
        if prefix and number:
            cleaned_data['phone'] = f"{prefix} {number}"
        elif number:
            cleaned_data['phone'] = number
        else:
            cleaned_data['phone'] = ''
        return cleaned_data


class SupplierForm(forms.ModelForm):
    phone_prefix = forms.ChoiceField(
        choices=PHONE_PREFIX_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'})
    )

    class Meta:
        model = Supplier
        fields = ['name', 'email', 'phone', 'vat_number', 'address', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.HiddenInput(),
            'vat_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., EL123456789'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Parse existing phone into prefix and number
        if self.instance and self.instance.phone:
            phone = self.instance.phone
            # Try to find matching prefix
            for prefix, _ in PHONE_PREFIX_CHOICES:
                if prefix and phone.startswith(prefix):
                    self.fields['phone_prefix'].initial = prefix
                    self.fields['phone_number'].initial = phone[len(prefix):].strip()
                    break
            else:
                # No prefix found, put everything in number
                self.fields['phone_number'].initial = phone

    def clean(self):
        cleaned_data = super().clean()
        prefix = cleaned_data.get('phone_prefix', '')
        number = cleaned_data.get('phone_number', '')
        # Combine prefix and number
        if prefix and number:
            cleaned_data['phone'] = f"{prefix} {number}"
        elif number:
            cleaned_data['phone'] = number
        else:
            cleaned_data['phone'] = ''
        return cleaned_data
