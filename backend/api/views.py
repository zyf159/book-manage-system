from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import serializers
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, BookSerializer, BorrowRecordSerializer
from .models import User, Book, BorrowRecord
from django.db.models import Q
from datetime import date, timedelta

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {'message': '注册成功'}, 
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            student_id = serializer.validated_data['student_id']
            password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(student_id=student_id)
                if user.check_password(password):
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                        'user': UserSerializer(user).data
                    }, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {'error': '密码错误'}, 
                        status=status.HTTP_401_UNAUTHORIZED
                    )
            except User.DoesNotExist:
                return Response(
                    {'error': '用户不存在'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

class UserProfileView(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f'UserListView - User: {request.user}, Role: {request.user.role}, IsStaff: {request.user.is_staff}')
            
            # 获取所有用户
            users = User.objects.all()
            logger.info(f'Total users: {users.count()}')
            
            # 处理搜索
            search = request.query_params.get('search', None)
            if search:
                users = users.filter(
                    Q(username__icontains=search) |
                    Q(student_id__icontains=search)
                )
            
            # 处理分页
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            start = (page - 1) * page_size
            end = start + page_size
            
            paginated_users = users[start:end]
            total = users.count()
            
            serializer = UserSerializer(paginated_users, many=True)
            logger.info(f'Returning {len(serializer.data)} users')
            return Response({
                'results': serializer.data,
                'count': total
            })
        except Exception as e:
            logger.error(f'Error in UserListView: {e}')
            import traceback
            logger.error(traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BookListCreateView(ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 处理搜索
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search) |
                Q(isbn__icontains=search)
            )
        
        # 处理分类筛选
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def create(self, request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f'Received data: {request.data}')
            
            # 移除cover_image字段，无论它是什么值
            data = request.data.copy()
            if 'cover_image' in data:
                data.pop('cover_image')
            
            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                logger.error(f'Serializer errors: {serializer.errors}')
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.error(f'Error creating book: {e}')
            logger.error(f'Request data: {request.data}')
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class BookDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]

class BorrowRecordListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if user.role == 'admin':
            records = BorrowRecord.objects.all()
        else:
            records = BorrowRecord.objects.filter(user=user)
        
        # 处理分页
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_records = records[start:end]
        total = records.count()
        
        serializer = BorrowRecordSerializer(paginated_records, many=True)
        return Response({
            'results': serializer.data,
            'count': total
        })
    
    def post(self, request):
        user = request.user
        
        try:
            # 获取图书ID
            book_id = request.data.get('book_id')
            print(f'Book ID: {book_id}')
            print(f'Request data: {request.data}')
            
            # 检查用户是否已达到借阅上限
            active_borrows = BorrowRecord.objects.filter(user=user, status='borrowed').count()
            print(f'Active borrows: {active_borrows}')
            if active_borrows >= 3:
                return Response({'error': '已达到借阅上限（最多3本）'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查图书是否可借
            book = Book.objects.get(id=book_id)
            print(f'Book: {book}')
            print(f'Available quantity: {book.available_quantity}')
            if book.available_quantity <= 0:
                return Response({'error': '图书已无可用副本'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 计算应归还日期
            due_date = date.today() + timedelta(days=book.borrow_period)
            print(f'Due date: {due_date}')
            
            # 创建借阅记录
            borrow_record = BorrowRecord.objects.create(
                user=user,
                book=book,
                due_date=due_date,
                status='borrowed'
            )
            print(f'Borrow record: {borrow_record}')
            
            # 更新图书可借数量
            book.available_quantity -= 1
            book.save()
            print(f'Updated book available quantity: {book.available_quantity}')
            
            # 返回成功响应
            serializer = BorrowRecordSerializer(borrow_record)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f'Error in post: {e}')
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class BorrowRecordDetailView(RetrieveUpdateDestroyAPIView):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer

class SystemStatusView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # 计算总图书数（按册数计算）
            books = Book.objects.all()
            total_books = 0
            available_books = 0
            
            for book in books:
                # 使用total_quantity字段计算总图书数
                total_books += book.total_quantity
                available_books += book.available_quantity
            
            # 计算已借出图书数
            borrowed_books = total_books - available_books
            
            return Response({
                'total_books': total_books,
                'borrowed_books': borrowed_books,
                'available_books': available_books
            })
        except Exception as e:
            print(f'Error in SystemStatusView: {e}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReturnBookView(APIView):
    permission_classes = [IsAdminUser]
    
    def put(self, request, pk):
        try:
            borrow_record = BorrowRecord.objects.get(id=pk)
            if borrow_record.status != 'borrowed':
                return Response(
                    {'error': '该图书已归还或状态异常'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 更新借阅记录
            borrow_record.status = 'returned'
            borrow_record.return_date = date.today()
            borrow_record.save()
            
            # 更新图书可借数量
            book = borrow_record.book
            book.available_quantity += 1
            book.save()
            
            return Response(
                {'message': '归还成功'},
                status=status.HTTP_200_OK
            )
        except BorrowRecord.DoesNotExist:
            return Response(
                {'error': '借阅记录不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
