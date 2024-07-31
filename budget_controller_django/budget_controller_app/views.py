from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .functions import hasher
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from .serializers import UserSerializer, CategorySerializer, UserTransactionSerializer
from rest_framework.decorators import action
from .models import User, UserTransaction, Category
from rest_framework import viewsets, status
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class UserAPIView(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = []
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)



class CategoryAPIView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class UserTransactionAPIView(viewsets.ModelViewSet):
    queryset = UserTransaction.objects.all()
    serializer_class = UserTransactionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'query',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
            ),
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