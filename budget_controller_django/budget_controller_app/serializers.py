from rest_framework import serializers
from .models import User, UserTransaction, Category

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone_number', 'password']

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'created_category_by']
    
class UserTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTransaction
        fields = ['amount', 'user', 'date', 'description', 'type', 'category']