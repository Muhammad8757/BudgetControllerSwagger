from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .functions import add_category_id, hasher, sorted_transactions
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
from django.contrib.auth.hashers import make_password



class UserAPIView(mixins.CreateModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = []
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        categories = ["Медицина", "Транспорт", "Еда и напитки", "Образование", "Другое"]
        for category in categories:
            add_category_id(request, id=user, name=category)

        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'phone_number': openapi.Schema(type=openapi.TYPE_INTEGER, description='Phone number of the user'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password of the user'),
            },
            required=['phone_number', 'password']
        ),
        responses={
            200: openapi.Response(
                description="Successful login",
                examples={
                    'application/json': {
                        'refresh': 'your-refresh-token',
                        'access': 'your-access-token'
                    }
                }
            ),
            400: 'Invalid input',
            404: 'User not found'
        }
    )
    @action(detail=False, methods=["post"])
    def login(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        if phone_number and password:
            try:
                user = User.objects.get(phone_number=phone_number)
                
                if user.check_password(password):  # Проверяем правильность пароля
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    })
                else:
                    return Response({"detail": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "Phone number and password are required"}, status=status.HTTP_400_BAD_REQUEST)



class CategoryAPIView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Category.objects.filter(created_category_by=self.request.user)

    def create(self, request):
        serializer = CategorySerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)



class UserTransactionAPIView(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.ListModelMixin,
                            GenericViewSet):
    serializer_class = UserTransactionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserTransaction.objects.filter(user=self.request.user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context
    
    def create(self, request):
        serializer = UserTransactionSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save()
        return Response(UserTransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)
    

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
        user_transaction = UserTransaction.objects.filter(Q(description__icontains=query) | Q(amount__icontains=query),user=request.user)
        serializer = UserTransactionSerializer(user_transaction, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)
        

    @action(detail=False, methods=["get"])
    def get_balance(self, request):
        user_transactions = UserTransaction.objects.filter(user=request.user)
        sum_zero = sum(item.amount for item in user_transactions if item.type == 0)
        sum_one = sum(item.amount for item in user_transactions if item.type == 1)
        total_sum = sum_one - sum_zero

        if total_sum == 0:
            formatted_balance = "0"
        else:
            formatted_balance = "{:.5f}".format(total_sum).rstrip('0').rstrip('.')

        return Response({"balance": formatted_balance}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['get'])
    def sorted_by_amount(self, request):
        transactions = sorted_transactions(request, 'amount')
        serializer = UserTransactionSerializer(transactions, many=True)
        return Response(
            {
                "result": serializer.data
            }
        )
    
    @action(detail=False, methods=['get'])
    def sorted_by_type(self, request):
        transactions = sorted_transactions(request, 'type')
        serializer = UserTransactionSerializer(transactions, many=True)
        return Response(
            {
                "result": serializer.data
            }
        )
    
    @action(detail=False, methods=['get'])
    def sorted_by_category(self, request):
        transactions = sorted_transactions(request, 'category')
        serializer = UserTransactionSerializer(transactions, many=True)
        return Response(
            {
                "result": serializer.data
            }
        )
    
    @action(detail=False, methods=['get'])
    def sorted_by_date(self, request):
        transactions = sorted_transactions(request, 'date')
        serializer = UserTransactionSerializer(transactions, many=True)
        return Response(
            {
                "result": serializer.data
            }
        )
    
    @action(detail=False, methods=['get'])
    def sorted_by_description(self, request):
        transactions = sorted_transactions(request, 'description')
        serializer = UserTransactionSerializer(transactions, many=True)
        return Response(
            {
                "result": serializer.data
            }
        )
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'category_id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def filter_by_category(self, request):
        choosen_category = request.query_params.get('category_id', None)
        filter_by_category_result = UserTransaction.objects.filter(user=request.user, category_id=choosen_category)
        serializer = UserTransactionSerializer(filter_by_category_result, many=True)
        return Response(
            {
                "result": serializer.data
            }
        )
    