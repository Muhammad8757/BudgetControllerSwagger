from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework_simplejwt.authentication import JWTAuthentication
from .functions import add_category_id, sorted_transactions
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from .serializers import UserSerializer, CategorySerializer, UserTransactionSerializer
from rest_framework.decorators import action
from .models import User, UserTransaction, Category
from rest_framework import status
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse



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
    
    @extend_schema(
        request=UserSerializer,
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description="Successful login"
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



class CategoryAPIView(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
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
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    



class UserTransactionAPIView(mixins.RetrieveModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
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
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='query', type=str, description='Search query for transactions', required=False),
            OpenApiParameter(name='sorted_by', type=str, description='Field to sort transactions by (e.g., amount, type, category, date, description)', required=False),
            OpenApiParameter(name='category_id', type=int, description='Category ID to filter transactions by', required=False),
        ],
        responses={
            200: UserTransactionSerializer(many=True),
            400: 'Invalid input'
        }
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('query', None)
        sorted_by = request.query_params.get('sorted_by', None)
        category_id = request.query_params.get('category_id', None)
        transaction = UserTransaction.objects.filter(user=request.user)

        if query:
            transaction = transaction.filter(Q(description__icontains=query) | Q(amount__icontains=query))
        
        if category_id:
            transaction = transaction.filter(category=category_id)
        
        if sorted_by:
            if sorted_by in ['amount', 'type', 'category', 'date', 'description']:
                transaction = sorted_transactions(request, sorted_by)
            else:
                raise serializers.ValidationError("Choose somethings from this list 'amount', 'type', 'category', 'date', 'description'.")
        if query is None and sorted_by is None and category_id is None:
            raise serializers.ValidationError("choose some filter")
        
        serializer = UserTransactionSerializer(transaction, many=True)
        return Response(
            {
                'results': serializer.data
            }, 
            status=status.HTTP_200_OK
        )
            
        

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Balance retrieved successfully'
            ),
        }
    )
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
    