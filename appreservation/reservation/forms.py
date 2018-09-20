from django import forms
from .models import Reservation
from datetime import datetime

# Formulario para la busqueda de reservaciones
class SearchReservationForm(forms.Form):
    check_in = forms.CharField(
        label="check_in", required=True,widget=forms.DateInput(
        attrs={'id':'check_in', 'class': 'form-control',
        'placeholder':'Check_in', 'aria-describedby':'emailHelp', 'type':'date'}
    ))
    check_out = forms.CharField(
        label="check_put", required=True,widget=forms.DateInput(
        attrs={'id':'check_out', 'class': 'form-control',
        'placeholder':'Check_in', 'aria-describedby':'emailHelp', 'type':'date'}
    ))

    # Funcio que evalua que las fecha sean correctas
    def clean(self):
        cleaned_data = super().clean()
        check_in = self.cleaned_data.get('check_in')
        check_out = self.cleaned_data.get('check_out')
        # Formato para la fecha
        format_date = '%Y-%m-%d'
        a = datetime.strptime(check_in, format_date)
        b = datetime.strptime(check_out, format_date)
        if (a <= b and b >= a):
            pass
        else: 
            self.add_error('check_in', 'Las fecha son incorrecta')

# Formulario para la creacion de la reserva
class CreateReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['name', 'last_name', 'email', 'num_card', 'observations']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class':'form-control', 'placeholder': 'Email'}),
            'num_card': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Numero de tarjeta'}),
            'observations': forms.Textarea(attrs={'class':'form-control', 'placeholder': 'Observaciones'}),
        }