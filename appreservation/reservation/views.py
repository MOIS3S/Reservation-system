from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse_lazy
from django.template.loader import get_template
from django.http import FileResponse
from rooms.models import Room
from .models import Reservation
from .forms import SearchReservationForm, CreateReservationForm
from .utils import render_to_pdf
from datetime import datetime


# Create your views here.
class SearchReservationPageView(View):
    form_class = SearchReservationForm
    template_name = "reservation/reservation_search_form.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form_class()})


    def post(self, request, *args, **kwargs):
        # Rellenamo el formulario con los datos envidos por POST
        form = self.form_class(data=request.POST)
        # Verificamos el los datos de formulario
        if form.is_valid():
            # Extraemos las fecha de entra y salida
            check_in_date = request.POST.get('check_in', '')
            check_out_date = request.POST.get('check_out', '')
            # Formato para la fecha
            format_date = '%Y-%m-%d'
            # Formatiar fecha de string a objecto date
            a = datetime.strptime(check_in_date, format_date)
            b = datetime.strptime(check_out_date, format_date)
            # Calculo de dias de la reserva
            total_days = abs((a - b).days)
            # primer filter busca todas la reservas que sean 
            # igual o menor al check-in el segundo filter busca todas la que sean
            # igual o mayor al check-out
            room_booked_1 = Reservation.objects.values_list('type_room',
                                flat=True).filter(
                                check_in__lte=check_in_date).filter( 
                                check_out__gte = check_out_date )
            # Filtramos el check-in con el rango de fecha selecionada y
            # Filtramos el check-out con el rango de fecha selecionado
            room_booked_2 = Reservation.objects.values_list('type_room', flat=True).filter(  
                                Q(check_in__range=(check_in_date, check_out_date) )  | 
                                Q(check_out__range=(check_in_date, check_out_date) ))
            # Esta 2 busquedas nos devuelven las reservas creadas
            #  y luego la combinamos o un merge
            room_booked = room_booked_1 | room_booked_2
            # Bscamos todas la habitacinos excepto
            # las que filtramos que tiene reserva
            room_avilable = Room.objects.exclude(id__in=list(room_booked))
            # Creamos estas varibles en la session
            # para utilizarlas en otra view
            # total_days para hacer el calculo del precio final
            request.session['total_days'] = total_days
            # check-in y check-out para luego crear la reservacion
            # con estas fechas seleccionadas
            request.session['check_in'] = check_in_date
            request.session['check_out'] = check_out_date
            ctx = {
                'form': form,
                'room_avilable': room_avilable,
                'total_days':   total_days,
            }
            return render(request, self.template_name, ctx)
        else:
            return render(request, self.template_name, {'form': form})


class ReservationPageView(View):
    form_class = CreateReservationForm
    template_name = 'reservation/reservation_form.html'

    def get(self, request, id, *args, **kwargs):
        # Buscamos la habitacion selecionada
        room = get_object_or_404(Room, id=id)
        # Calculamos el precio total de la habitacion
        # toamndo el precio de la habiatio por los dias
        total_price = room.price * request.session['total_days']
        # Enviamos el formulario para crear la reserva
        form = self.form_class()
        return render(request, self.template_name, {'form': self.form_class, 'total_price': total_price})
    
    def post(self, request, id, *args, **kwargs):
        # Buscamos el usuario que creo la reserva
        user = get_object_or_404(User, id=request.user.id)
        # Buscamos la habitacion
        room = get_object_or_404(Room, id=id)  
        # Rellenamo el formlario con los datos suministrados
        form = self.form_class(request.POST)
        # Verificamos si el valido
        if form.is_valid():
            # Limpiamos el formulario y guarmos los datos
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            card = form.cleaned_data['num_card']
            observations = form.cleaned_data['observations']
            check_in = request.session['check_in']
            check_out = request.session['check_out']
            # Calculamos el precio total de la reserva
            total_price = room.price * request.session['total_days']
            # Creamos una reservacion con los datos de formulario
            reserve = Reservation(
                user=user,
                type_room=room, 
                name=name, 
                last_name=last_name, 
                email=email, 
                num_card=card,
                observations=observations,
                check_in=check_in,
                check_out=check_out,
                total_price=total_price
            )
            # Guardamos la reserva en la base de datos
            reserve.save(force_insert=True)
            # Redireccionamos a la lista o panel de reservas
            return redirect(reverse_lazy('reservation_list'))
        return render(request, self.template_name)


# Vista pra la lista de reservas
class ReservationListView(ListView):
    model = Reservation
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filtramos todas las reservas del usurio 
        context['reservations'] = Reservation.objects.filter(user=self.request.user).order_by('id')
        return context


# Vista de detalle de reserva
class ReservationDetailView(DetailView):
    model = Reservation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservations'] = get_object_or_404(Reservation, id=self.kwargs['pk'])
        return context


# Vista para borrar una reserva
class ReservationDeleteView(DeleteView):
    model = Reservation
    success_url = reverse_lazy('reservation_list')


# Vista que genera la factura en pdf
class GeneratePDF(View):
    def get(self,request, *args, **kwargs):
        # Buscamos la reserva por su id
        reserve = get_object_or_404(Reservation, id=kwargs['id'])
        # Cargamos el template o diseño del pdf
        template = get_template('reservation/invoice.html')
        # Guarmos la reserva en un variable context
        context = {"reserve":reserve}
        # Cargamos el templates con los datos del context
        html = template.render(context)
        # Creamos el pdf con el context
        pdf = render_to_pdf('reservation/invoice.html', context)
        # Creamos el la respuesta para que el navegador lo descarge
        # automaticamente
        response = FileResponse(pdf,content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format('invoice.pdf')
        return response