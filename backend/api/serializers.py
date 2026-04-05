from rest_framework import serializers
from .models import User, Book, BorrowRecord, Category, Reservation, Notification, Tag, Comment, Collection
from django.contrib.auth.hashers import make_password

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

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
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    borrow_count = serializers.IntegerField(read_only=True, default=0)
    average_rating = serializers.FloatField(read_only=True, default=0)
    collection_count = serializers.IntegerField(read_only=True, default=0)
    is_collected = serializers.BooleanField(read_only=True, default=False)
    
    class Meta:
        model = Book
        fields = '__all__'
        extra_fields = ['category_id', 'tag_ids', 'borrow_count', 'average_rating', 'collection_count', 'is_collected']
    
    def create(self, validated_data):
        # 处理category_id
        category_id = validated_data.pop('category_id', None)
        if category_id:
            from .models import Category
            try:
                category = Category.objects.get(id=category_id)
                validated_data['category'] = category
            except Category.DoesNotExist:
                pass
        
        # 处理tag_ids
        tag_ids = validated_data.pop('tag_ids', [])
        
        # 移除cover_image字段，如果它存在且不是文件类型
        if 'cover_image' in validated_data and not hasattr(validated_data['cover_image'], 'read'):
            validated_data.pop('cover_image')
        
        book = Book.objects.create(**validated_data)
        if tag_ids:
            book.tags.set(tag_ids)
        return book
    
    def update(self, instance, validated_data):
        # 处理category_id
        category_id = validated_data.pop('category_id', None)
        if category_id is not None:
            if category_id == 0:
                validated_data['category'] = None
            else:
                from .models import Category
                try:
                    category = Category.objects.get(id=category_id)
                    validated_data['category'] = category
                except Category.DoesNotExist:
                    pass
        
        # 处理tag_ids
        tag_ids = validated_data.pop('tag_ids', None)
        
        # 移除cover_image字段，如果它存在且不是文件类型
        if 'cover_image' in validated_data and not hasattr(validated_data['cover_image'], 'read'):
            validated_data.pop('cover_image')
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        
        return instance

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = serializers.SerializerMethodField()
    book_id = serializers.IntegerField(write_only=True, required=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'book', 'book_id', 'user_id', 'content', 'rating', 'created_at', 'updated_at']
    
    def get_book(self, obj):
        from .serializers import BookSerializer
        return BookSerializer(obj.book).data
    
    def create(self, validated_data):
        # 从validated_data中获取book_id和user_id
        book_id = validated_data.pop('book_id')
        user_id = validated_data.pop('user_id')
        
        # 创建评论对象
        comment = Comment.objects.create(
            book_id=book_id,
            user_id=user_id,
            **validated_data
        )
        return comment

class CollectionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = serializers.SerializerMethodField()
    book_id = serializers.IntegerField(write_only=True, required=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Collection
        fields = ['id', 'user', 'book', 'book_id', 'user_id', 'created_at']
    
    def get_book(self, obj):
        from .serializers import BookSerializer
        return BookSerializer(obj.book).data
    
    def create(self, validated_data):
        # 从validated_data中获取book_id和user_id
        book_id = validated_data.pop('book_id')
        user_id = validated_data.pop('user_id')
        
        # 创建收藏对象
        collection = Collection.objects.create(
            book_id=book_id,
            user_id=user_id,
            **validated_data
        )
        return collection

class BorrowRecordSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = BookSerializer(read_only=True)
    
    class Meta:
        model = BorrowRecord
        fields = ['id', 'user', 'book', 'borrow_date', 'due_date', 'return_date', 'status']

class ReservationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = BookSerializer(read_only=True)
    book_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = Reservation
        fields = ['id', 'user', 'book', 'book_id', 'reservation_date', 'status']
    
    def create(self, validated_data):
        book_id = validated_data.pop('book_id')
        book = Book.objects.get(id=book_id)
        return Reservation.objects.create(book=book, **validated_data)

class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'type', 'title', 'message', 'is_read', 'created_at']
