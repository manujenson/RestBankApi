from django.contrib.auth import authenticate, login, logout

from django.shortcuts import render
from rest_framework import generics, mixins, permissions, status,authentication
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.admin import User
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from .models import Bank,Transaction
from .serializers import Loginserializer, Bankmodelserializer, Accountmodelserializer, Withdrawserializer,\
    Depositserializer,Transactionserializer
# Create your views here.
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class BankdetailMixin(generics.GenericAPIView, mixins.CreateModelMixin):
    serializer_class = Bankmodelserializer

    def post(self, request):
        return self.create(request)


class BankAccountview(generics.GenericAPIView, mixins.CreateModelMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = Accountmodelserializer

    def get(self, request):
        acc_number = Bank.objects.last()
        if acc_number:
            acc_number = acc_number.acc_number + 1


        else:
            acc_number = 1000
        return Response({"acc_number": "Account number is " + str(acc_number)})

    def post(self, request):
        return self.create(request)

class Balanceview(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request,acc_number):
        acc_number=Bank.objects.get(acc_number=acc_number)
        serializer=Accountmodelserializer(acc_number)
        return Response({"messege": "Balance is " + str(acc_number.balance)})


class Loginbank(APIView):

    def post(self, request):
        serializer = Loginserializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get("username")
            password = serializer.validated_data.get("password")
            # user = authenticate(request, username=username, password=password)
            user = User.objects.get(username=username)
            if (user.username == username) & (user.password == password):
                login(request, user)

                token, created = Token.objects.get_or_create(user=user)
                return Response({"token": token.key}, status=204)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    def get(self, request):
        logout(request)
        request.user.auth_token.delete()

class Withdrawview(APIView):
    def post(self,request,acc_number):
        serializer=Withdrawserializer(data=request.data)
        acc_number=Bank.objects.get(acc_number=acc_number)
        if serializer.is_valid():
            amt=serializer.validated_data.get("amount")
            if amt<acc_number.balance:
                acc_number.balance-=amt
                acc_number.save()
                return Response({"message":"withdraw succesfull, balance is"+str(acc_number.balance)})
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class Depositview(APIView):
    def post(self, request, acc_number):
        serializer = Depositserializer(data=request.data)
        acc_number = Bank.objects.get(acc_number=acc_number)
        if serializer.is_valid():
            amt = serializer.validated_data.get("amount")
            acc_number.balance += amt
            acc_number.save()
            return Response({"message": "Deposit succesfull, balance is" + str(acc_number.balance)})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class Transactionview(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, acc_number):
        accounts=Bank.objects.get(acc_number=acc_number)
        debit = Transaction.objects.filter(acc_number=accounts)
        credit = Transaction.objects.filter(to_acc=acc_number)
        serializer1 = Transactionserializer(debit, many=True)
        serializer2 = Transactionserializer(credit, many=True)
        return Response({"All Debit Transactions": serializer1.data, "All credit transactions": serializer2.data},status=status.HTTP_200_OK)


    def post(self, request):
        serializer = Transactionserializer(data=request.data)
        if serializer.is_valid():
            acc_number = serializer.validated_data.get("acc_number")
            to_acc = serializer.validated_data.get("to_acc")
            amount = serializer.validated_data.get("amount")
            accounts=Bank.objects.get(acc_number=acc_number)
            to_accounts=Bank.objects.get(acc_number=to_acc)

            if amount <= (accounts.balance):
                serializer.save()
                accounts.balance -= amount
                to_accounts.balance += amount
                accounts.save()
                to_accounts.save()
                return Response({"msg":str(amount) + "has been sent to acno: " + str(to_acc)})
            else:
                return Response({"No Sufficient balance"})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

