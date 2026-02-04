"""
DRF Serializers for User model.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from apps.plans.models import Plan


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    plan_id = serializers.IntegerField(required=False)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'plan_id']
    
    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        plan_id = validated_data.pop('plan_id', None)
        password = validated_data.pop('password')
        
        # Assign Free plan by default
        if plan_id:
            try:
                plan = Plan.objects.get(id=plan_id)
            except Plan.DoesNotExist:
                plan = Plan.objects.get(name='Free')
        else:
            plan = Plan.objects.get(name='Free')
        
        user = User.objects.create_user(password=password, plan=plan, **validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials")
            if not user.is_active:
                raise serializers.ValidationError("Account is disabled")
            data['user'] = user
        else:
            raise serializers.ValidationError("Email and password required")
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    total_videos = serializers.IntegerField(read_only=True)
    total_storage_used = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'plan_name', 
                  'total_videos', 'total_storage_used', 'created_at']
        read_only_fields = ['id', 'email', 'role', 'created_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = ['username']
