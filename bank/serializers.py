
from rest_framework import serializers
from rest_framework.authtoken.admin import User
from rest_framework.serializers import ModelSerializer

from .models import Bank,Transaction


class Loginserializer(serializers.Serializer):

    username=serializers.CharField()
    password=serializers.CharField()

class Bankmodelserializer(ModelSerializer):
    class Meta:
        model=User
        fields=['first_name','username','password','email']

class Accountmodelserializer(ModelSerializer):
    class Meta:
        model=Bank
        fields=['acc_number','username','balance']

class Withdrawserializer(serializers.Serializer):
    amount=serializers.IntegerField()

class Depositserializer(serializers.Serializer):
    amount=serializers.IntegerField()


class Transactionserializer(serializers.Serializer):
    acc_number = serializers.CharField()
    to_acc = serializers.IntegerField()
    amount = serializers.IntegerField()

    def create(self, validated_data):
        acc_number = validated_data["acc_number"]
        accounts = Bank.objects.get(acc_number=acc_number)
        validated_data["acc_number"] = accounts
        return Transaction.objects.create(**validated_data)