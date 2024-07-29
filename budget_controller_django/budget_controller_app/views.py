from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .functions import hasher
from django.db.models import Q
from .serializers import UserSerializer, CategorySerializer, UserTransactionSerializer
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, UserTransaction, Category
from rest_framework import viewsets, filters, status
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

class UserAPIView(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        password = data.get('password')
        data['password'] = hasher(password)
        return super().create(request, *args, **kwargs)

class CategoryAPIView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class UserTransactionAPIView(viewsets.ModelViewSet):
    queryset = UserTransaction.objects.all()
    serializer_class = UserTransactionSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'query',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'phone_number',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'password',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    @action(detail=False, methods=["get"])
    def search_transaction(self, request):
        query = request.query_params.get('query', None)
        phone_number = request.query_params.get('phone_number', None)
        password = request.query_params.get('password', None)
        user = User.objects.get(phone_number=phone_number, password=password)
        user_transaction = UserTransaction.objects.filter(Q(description__icontains=query) | Q(amount__icontains=query),user=user)
        serializer = UserTransactionSerializer(user_transaction, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)
        
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'phone_number',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'password',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    @action(detail=False, methods=["get"])
    def get_balance(self, request):
        phone_number = request.query_params.get('phone_number', None)
        password = request.query_params.get('password', None)
        user = User.objects.get(phone_number=phone_number, password=password)
        user_transactions = UserTransaction.objects.filter(user=user)
        sum_zero = sum(item.amount for item in user_transactions if item.type == 0)
        sum_one = sum(item.amount for item in user_transactions if item.type == 1)
        total_sum = sum_one - sum_zero

        if total_sum == 0:
            formatted_balance = "0"
        else:
            formatted_balance = "{:.5f}".format(total_sum).rstrip('0').rstrip('.')

        return Response({"balance": formatted_balance}, status=status.HTTP_200_OK)
    