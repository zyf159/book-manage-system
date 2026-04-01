from rest_framework import serializers
from .models import User, Book, BorrowRecord
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'student_id', 'email', 'role']
        read_only_fields = ['id', 'role']

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'student_id', 'email', 'password', 'confirm_password']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': '密码不一致'})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)

class UserLoginSerializer(serializers.Serializer):
    student_id = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class BookSerializer(serializers.ModelSerializer):
    cover_image = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True)
    
    class Meta:
        model = Book
        fields = '__all__'
    
    def create(self, validated_data):
        # 移除cover_image字段，如果它存在且不是文件类型
        if 'cover_image' in validated_data and not hasattr(validated_data['cover_image'], 'read'):
            validated_data.pop('cover_image')
        return super().create(validated_data)

class BorrowRecordSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = BookSerializer(read_only=True)
    
    class Meta:
        model = BorrowRecord
        fields = ['id', 'user', 'book', 'borrow_date', 'due_date', 'return_date', 'status']
