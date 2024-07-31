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
        fields = ['id', 'amount', 'date', 'description', 'type', 'category']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['category'].required = False

    def validate(self, data):
        user = self.context['user']
        category = data.get('category')
        
        if category is not None:
            if isinstance(category, Category):
                
                category_id = category.id
            elif isinstance(category, str) and category.isdigit():
                
                category_id = int(category)
            else:
                
                raise serializers.ValidationError("Category must be a number.")
            
            
            if not Category.objects.filter(id=category_id, created_category_by=user).exists():
                raise serializers.ValidationError("The specified category does not exist.")
            
        amount = data.get('amount')
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise serializers.ValidationError("Amount must be a positive number.")
        
        return data
    
    def create(self, validated_data):
        user = self.context['user']
        transaction = UserTransaction.objects.create(user=user, **validated_data)
        return transaction
    
    def update(self, instance, validated_data):
    
        user = self.context.get('user')
        if user is None:
            raise serializers.ValidationError("User must be provided in the context.")
        
    
        instance.amount = validated_data.get('amount', instance.amount)
        instance.category = validated_data.get('category', instance.category)
        instance.description = validated_data.get('description', instance.category)
        instance.type = validated_data.get('type', instance.category)
        
    
        instance.save()
        
        return instance