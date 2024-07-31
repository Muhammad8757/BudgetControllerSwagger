from rest_framework import serializers
from .models import User, UserTransaction, Category
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'phone_number', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(
            name=validated_data['name'],
            phone_number=validated_data['phone_number']
        )
        user.set_password(password)
        user.save()
        return user
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
    
    def create(self, validated_data):
        user = self.context['user']
        category = Category.objects.create(name=validated_data['name'], created_category_by=user)
        category.save()
        return category
    
class UserTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTransaction
        fields = ['amount', 'user', 'date', 'description', 'type', 'category']