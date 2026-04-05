from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import serializers
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, BookSerializer, BorrowRecordSerializer, CategorySerializer, ReservationSerializer, NotificationSerializer, TagSerializer, CommentSerializer, CollectionSerializer
from .models import User, Book, BorrowRecord, Category, Reservation, Notification, Tag, Comment, Collection
from django.db.models import Q
from datetime import date, timedelta
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

@method_decorator(ensure_csrf_cookie, name='dispatch')
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

@method_decorator(ensure_csrf_cookie, name='dispatch')
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
                    # 使用Session认证，登录用户
                    from django.contrib.auth import login
                    login(request, user)
                    return Response({
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
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        
        # 处理分类筛选（支持分类名称）
        category = self.request.query_params.get('category', None)
        if category:
            # 尝试根据分类名称查找分类ID
            try:
                from .models import Category
                category_obj = Category.objects.filter(name__icontains=category).first()
                if category_obj:
                    queryset = queryset.filter(category=category_obj)
                else:
                    # 如果没有找到分类，返回空结果
                    queryset = queryset.none()
            except Exception as e:
                print(f'分类筛选错误: {e}')
                queryset = queryset.none()
        
        return queryset
    
    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        # 为每个图书计算额外字段
        if hasattr(serializer, 'instance'):
            instances = serializer.instance
            if not isinstance(instances, list):
                instances = [instances]
            
            for book in instances:
                # 计算平均评分
                from django.db.models import Avg
                avg_rating = book.comments.aggregate(Avg('rating'))['rating__avg']
                book.average_rating = round(avg_rating, 1) if avg_rating else 0
                
                # 计算收藏数量
                book.collection_count = book.collections.count()
                
                # 检查当前用户是否已收藏
                user = self.request.user
                if user.is_authenticated:
                    from .models import Collection
                    book.is_collected = Collection.objects.filter(user=user, book=book).exists()
                else:
                    book.is_collected = False
        return serializer
    
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
    
    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        # 为图书计算额外字段
        if hasattr(serializer, 'instance'):
            book = serializer.instance
            
            # 计算平均评分
            from django.db.models import Avg
            avg_rating = book.comments.aggregate(Avg('rating'))['rating__avg']
            book.average_rating = round(avg_rating, 1) if avg_rating else 0
            
            # 计算收藏数量
            book.collection_count = book.collections.count()
            
            # 检查当前用户是否已收藏
            user = self.request.user
            if user.is_authenticated:
                book.is_collected = Collection.objects.filter(user=user, book=book).exists()
            else:
                book.is_collected = False
        return serializer

class BorrowRecordListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if user.role == 'admin':
            records = BorrowRecord.objects.all()
        else:
            records = BorrowRecord.objects.filter(user=user)
        
        # 处理搜索
        search = request.query_params.get('search', None)
        if search:
            records = records.filter(
                Q(user__username__icontains=search) |
                Q(book__title__icontains=search)
            )
        
        # 处理状态过滤
        status_filter = request.query_params.get('status', None)
        if status_filter:
            records = records.filter(status=status_filter)
        
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
    permission_classes = [AllowAny]
    
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

class AvailableBooksView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            # 获取所有可借数量大于0的图书
            available_books = Book.objects.filter(available_quantity__gt=0)
            
            # 序列化
            serializer = BookSerializer(available_books, many=True)
            
            return Response({
                'count': available_books.count(),
                'results': serializer.data
            })
        except Exception as e:
            print(f'Error in AvailableBooksView: {e}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReservableBooksView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            # 获取所有可借数量为0的图书（已被借出，可以预约）
            reservable_books = Book.objects.filter(available_quantity=0)
            
            # 序列化
            serializer = BookSerializer(reservable_books, many=True)
            
            return Response({
                'count': reservable_books.count(),
                'results': serializer.data
            })
        except Exception as e:
            print(f'Error in ReservableBooksView: {e}')
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

class RenewBookView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        try:
            borrow_record = BorrowRecord.objects.get(id=pk)
            
            # 检查是否是当前用户的借阅记录
            if borrow_record.user != request.user and not request.user.is_staff:
                return Response(
                    {'error': '无权限操作此借阅记录'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 检查借阅记录状态
            if borrow_record.status != 'borrowed':
                return Response(
                    {'error': '该图书已归还或状态异常，无法续借'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 检查是否已逾期
            if borrow_record.due_date < date.today():
                return Response(
                    {'error': '该图书已逾期，无法续借'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 获取续借天数，默认为30天
            renew_days = request.data.get('renew_days', 30)
            
            # 更新应归还日期
            borrow_record.due_date += timedelta(days=renew_days)
            borrow_record.save()
            
            # 创建通知
            Notification.objects.create(
                user=borrow_record.user,
                type='borrow_due',
                title='续借成功',
                message=f'《{borrow_record.book.title}》续借成功，新的归还日期为{borrow_record.due_date}'
            )
            
            serializer = BorrowRecordSerializer(borrow_record)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BorrowRecord.DoesNotExist:
            return Response(
                {'error': '借阅记录不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

class OverdueBooksView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def get(self, request):
        try:
            # 获取当前用户的逾期记录（非管理员）
            if not request.user.is_staff:
                overdue_records = BorrowRecord.objects.filter(
                    user=request.user,
                    status='borrowed',
                    due_date__lt=date.today()
                )
            # 获取所有逾期记录（管理员）
            else:
                overdue_records = BorrowRecord.objects.filter(
                    status='borrowed',
                    due_date__lt=date.today()
                )
            
            serializer = BorrowRecordSerializer(overdue_records, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(f'Error in OverdueBooksView: {e}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BorrowingRankingView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # 按图书ID分组，计算每本书的借阅次数
            from django.db.models import Count
            
            # 获取借阅次数最多的图书
            top_books = Book.objects.annotate(
                borrow_count=Count('borrow_records')
            ).order_by('-borrow_count')[:10]  # 取前10名
            
            # 序列化结果
            serializer = BookSerializer(top_books, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(f'Error in BorrowingRankingView: {e}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BookRecommendationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # 获取当前用户的借阅历史
            user_borrow_records = BorrowRecord.objects.filter(
                user=request.user
            )
            
            # 提取用户借阅过的图书ID
            borrowed_book_ids = [record.book.id for record in user_borrow_records]
            
            if not borrowed_book_ids:
                # 如果用户没有借阅历史，返回热门图书
                from django.db.models import Count
                recommended_books = Book.objects.annotate(
                    borrow_count=Count('borrow_records')
                ).order_by('-borrow_count')[:10]
            else:
                # 基于用户借阅历史推荐图书
                # 1. 获取用户借阅过的图书的分类
                borrowed_books = Book.objects.filter(id__in=borrowed_book_ids)
                category_ids = set()
                tag_ids = set()
                
                for book in borrowed_books:
                    if book.category:
                        category_ids.add(book.category.id)
                    # 收集图书的标签
                    for tag in book.tags.all():
                        tag_ids.add(tag.id)
                
                # 2. 查找同分类或同标签的图书
                recommended_books = Book.objects.filter(
                    Q(category_id__in=category_ids) | Q(tags__id__in=tag_ids)
                ).exclude(id__in=borrowed_book_ids).distinct()[:10]
                
                # 如果推荐数量不足，补充热门图书
                if len(recommended_books) < 10:
                    from django.db.models import Count
                    popular_books = Book.objects.annotate(
                        borrow_count=Count('borrow_records')
                    ).exclude(id__in=borrowed_book_ids).order_by('-borrow_count')[:10 - len(recommended_books)]
                    recommended_books = list(recommended_books) + list(popular_books)
            
            # 序列化结果
            serializer = BookSerializer(recommended_books, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(f'Error in BookRecommendationView: {e}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def get(self, request):
        # 定义8个目标分类
        target_categories = [
            '计算机科学', '文学', '历史', '哲学',
            '艺术', '教育', '科学', '工程'
        ]
        # 只返回这8个分类
        categories = Category.objects.filter(name__in=target_categories)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetailView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request, pk):
        try:
            category = Category.objects.get(id=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({'error': '分类不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        try:
            category = Category.objects.get(id=pk)
            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response({'error': '分类不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            category = Category.objects.get(id=pk)
            category.delete()
            return Response({'message': '删除成功'}, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({'error': '分类不存在'}, status=status.HTTP_404_NOT_FOUND)

class ReservationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.is_staff:
            reservations = Reservation.objects.all()
        else:
            reservations = Reservation.objects.filter(user=request.user)
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            # 检查用户是否已经预约了该图书
            book_id = request.data.get('book_id')
            existing_reservation = Reservation.objects.filter(
                user=request.user,
                book_id=book_id,
                status='pending'
            ).exists()
            if existing_reservation:
                return Response({'error': '您已经预约了该图书'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查图书是否存在
            try:
                book = Book.objects.get(id=book_id)
            except Book.DoesNotExist:
                return Response({'error': '图书不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 检查图书是否可借
            if book.available_quantity > 0:
                return Response({'error': '图书当前可借，无需预约'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建预约记录
            reservation = serializer.save(user=request.user)
            return Response(ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReservationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            if request.user.is_staff:
                reservation = Reservation.objects.get(id=pk)
            else:
                reservation = Reservation.objects.get(id=pk, user=request.user)
            serializer = ReservationSerializer(reservation)
            return Response(serializer.data)
        except Reservation.DoesNotExist:
            return Response({'error': '预约记录不存在'}, status=status.HTTP_404_NOT_FOUND)

class NotificationView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        # 只有登录用户才返回通知
        if request.user.is_authenticated:
            notifications = Notification.objects.filter(user=request.user)
            serializer = NotificationSerializer(notifications, many=True)
            return Response(serializer.data)
        else:
            # 未登录用户返回空列表
            return Response([])
    
    def post(self, request):
        # 只有登录用户才能标记通知为已读
        if request.user.is_authenticated:
            # 标记所有通知为已读
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
            return Response({'message': '所有通知已标记为已读'})
        else:
            # 未登录用户返回错误信息
            return Response({'error': '需要登录才能执行此操作'}, status=status.HTTP_401_UNAUTHORIZED)

class NotificationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        try:
            notification = Notification.objects.get(id=pk, user=request.user)
            notification.is_read = True
            notification.save()
            serializer = NotificationSerializer(notification)
            return Response(serializer.data)
        except Notification.DoesNotExist:
            return Response({'error': '通知不存在'}, status=status.HTTP_404_NOT_FOUND)

class CommentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, book_id=None):
        try:
            if book_id:
                # 获取指定图书的评论
                comments = Comment.objects.filter(book_id=book_id).order_by('-created_at')
            else:
                # 获取当前用户的评论
                comments = Comment.objects.filter(user=request.user).order_by('-created_at')
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(f'Error in CommentView get: {e}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try:
            data = request.data.copy()
            data['user_id'] = request.user.id
            serializer = CommentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f'Error in CommentView post: {e}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, pk):
        try:
            comment = Comment.objects.get(id=pk)
            # 只有评论的作者可以删除评论
            if comment.user != request.user:
                return Response({'error': '无权删除此评论'}, status=status.HTTP_403_FORBIDDEN)
            comment.delete()
            return Response({'message': '评论删除成功'}, status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({'error': '评论不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f'Error in CommentView delete: {e}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CollectionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # 获取当前用户的收藏
            collections = Collection.objects.filter(user=request.user).order_by('-created_at')
            serializer = CollectionSerializer(collections, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(f'Error in CollectionView get: {e}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try:
            data = request.data.copy()
            data['user_id'] = request.user.id
            
            # 检查是否已经收藏
            existing = Collection.objects.filter(user=request.user, book_id=data.get('book_id')).exists()
            if existing:
                return Response({'error': '已经收藏过此图书'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = CollectionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f'Error in CollectionView post: {e}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, book_id):
        try:
            collection = Collection.objects.get(user=request.user, book_id=book_id)
            collection.delete()
            return Response({'message': '取消收藏成功'}, status=status.HTTP_200_OK)
        except Collection.DoesNotExist:
            return Response({'error': '未收藏此图书'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f'Error in CollectionView delete: {e}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NotificationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            notification = Notification.objects.get(id=pk, user=request.user)
            serializer = NotificationSerializer(notification)
            return Response(serializer.data)
        except Notification.DoesNotExist:
            return Response({'error': '通知不存在'}, status=status.HTTP_404_NOT_FOUND)

class TagView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TagDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def get(self, request, pk):
        try:
            tag = Tag.objects.get(id=pk)
            serializer = TagSerializer(tag)
            return Response(serializer.data)
        except Tag.DoesNotExist:
            return Response({'error': '标签不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        try:
            tag = Tag.objects.get(id=pk)
            serializer = TagSerializer(tag, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Tag.DoesNotExist:
            return Response({'error': '标签不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            tag = Tag.objects.get(id=pk)
            tag.delete()
            return Response({'message': '删除成功'}, status=status.HTTP_200_OK)
        except Tag.DoesNotExist:
            return Response({'error': '标签不存在'}, status=status.HTTP_404_NOT_FOUND)
