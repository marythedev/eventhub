from django.db import models
from datetime import date

class User(models.Model):
    firstname = models.CharField('firstname', max_length = 15)
    lastname = models.CharField('lastname', max_length = 20)
    email = models.EmailField('email', max_length = 30, unique = True)

class Concert(models.Model):
    managers = models.ManyToManyField(User)
    name = models.CharField('concert name', max_length = 60)
    description = models.TextField('description', blank=True)
    date = models.DateTimeField('date')
    image = models.ImageField('preview image', null = True, blank = True)
    location = models.CharField('location', max_length = 100)
    website = models.URLField('website', max_length=255, null = False)

class Seat(models.Model):
    concert = models.ForeignKey(Concert, on_delete = models.CASCADE)
    seat_type = models.CharField('seat type', max_length = 60)
    quantity = models.IntegerField('seat quantity')
    price = models.FloatField('price')

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    card_number = models.CharField('Card Number', max_length = 16, null = False)
    cvv = models.CharField('CVV', max_length = 4, null = False)
    exp_month = models.CharField('Expiration month', max_length = 2, null = False)
    exp_year = models.CharField('Expiration year', max_length = 4, null = False)
    holder_name = models.CharField('Card Holder Name', max_length = 100, null = False)

class Ticket(models.Model):
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    concert = models.ForeignKey(Concert, on_delete=models.CASCADE)

class Order(models.Model):
    purchaser = models.ForeignKey(User, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete = models.PROTECT)
    tickets = models.ManyToManyField(Ticket)
    date = models.DateField('order date', default = date.today)