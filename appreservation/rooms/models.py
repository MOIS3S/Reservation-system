from django.db import models


class Room(models.Model):
    room_type = models.CharField(max_length=75, verbose_name="Type of room");
    capacity = models.IntegerField(verbose_name="Capacity");
    description = models.TextField(verbose_name="Description")
    photo = models.ImageField(upload_to='photo', null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Price");

    class Meta:
        verbose_name = "Room"

    def __str__(self):
        return self.room_type
