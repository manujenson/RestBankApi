from django.db import models


# Create your models here.
class Bank(models.Model):
    acc_number = models.IntegerField(unique=True)
    username = models.CharField(max_length=120, unique=True)
    balance = models.FloatField(default=50)

    def __str__(self):
        return str(self.acc_number)

class Transaction(models.Model):
    acc_number = models.ForeignKey(Bank,on_delete=models.CASCADE)
    to_acc = models.IntegerField()
    amount = models.IntegerField()

    def __str__(self):
        return str(self.acc_number)