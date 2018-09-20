import uuid
from django.db import models
from rooms.models import Room
from django.contrib.auth.models import User


# Create your models here.

class Reservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE);
    type_room = models.ForeignKey(Room, 
        verbose_name="Type of room",
        on_delete=models.CASCADE);
    name = models.CharField(max_length=255, verbose_name="Nombre");
    last_name = models.CharField(max_length=255, verbose_name="Apellido");
    email = models.EmailField();
    num_card = models.IntegerField(verbose_name="Numero de tarjeta");
    observations = models.TextField(verbose_name="Observaciones", blank=True)
    check_in = models.DateField(verbose_name="Check-in", null=True)
    check_out = models.DateField(verbose_name="Check-out", null=True)
    total_price = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Reservation"

    def __str__(self):
        return self.name