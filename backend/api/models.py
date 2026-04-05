from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

class Category(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='分类名称'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='分类描述'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        verbose_name = '图书分类'
        verbose_name_plural = '图书分类'
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='标签名称'
    )
    color = models.CharField(
        max_length=7,
        default='#409eff',
        verbose_name='标签颜色'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        verbose_name = '图书标签'
        verbose_name_plural = '图书标签'
    
    def __str__(self):
        return self.name

class User(AbstractUser):
    STUDENT_ID_MAX_LENGTH = 20
    ROLE_CHOICES = [
        ('user', '普通用户'),
        ('admin', '管理员'),
    ]
    student_id = models.CharField(
        max_length=STUDENT_ID_MAX_LENGTH,
        unique=True,
        verbose_name='学号'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='角色'
    )
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

class Book(models.Model):
    ISBN_MAX_LENGTH = 20
    TITLE_MAX_LENGTH = 200
    AUTHOR_MAX_LENGTH = 100
    PUBLISHER_MAX_LENGTH = 100
    CATEGORY_MAX_LENGTH = 50
    LOCATION_MAX_LENGTH = 50
    CALL_NUMBER_MAX_LENGTH = 50
    
    title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name='书名'
    )
    author = models.CharField(
        max_length=AUTHOR_MAX_LENGTH,
        verbose_name='作者'
    )
    isbn = models.CharField(
        max_length=ISBN_MAX_LENGTH,
        unique=True,
        verbose_name='ISBN'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books',
        verbose_name='分类'
    )
    publisher = models.CharField(
        max_length=PUBLISHER_MAX_LENGTH,
        verbose_name='出版社'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='定价'
    )
    location = models.CharField(
        max_length=LOCATION_MAX_LENGTH,
        verbose_name='馆藏地点'
    )
    call_number = models.CharField(
        max_length=CALL_NUMBER_MAX_LENGTH,
        verbose_name='索书号'
    )
    cover_image = models.ImageField(
        upload_to='book_covers/',
        null=True,
        blank=True,
        verbose_name='封面图片'
    )
    total_quantity = models.IntegerField(
        default=1,
        verbose_name='馆藏总数量'
    )
    available_quantity = models.IntegerField(
        default=1,
        verbose_name='可借数量'
    )
    borrow_period = models.IntegerField(
        default=30,
        verbose_name='借阅期限（天）'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='内容简介'
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='books',
        blank=True,
        verbose_name='标签'
    )
    
    class Meta:
        verbose_name = '图书'
        verbose_name_plural = '图书'

class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ('borrowed', '借阅中'),
        ('returned', '已归还'),
        ('overdue', '已逾期'),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='borrow_records',
        verbose_name='用户'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='borrow_records',
        verbose_name='图书'
    )
    borrow_date = models.DateField(
        default=date.today,
        verbose_name='借阅日期'
    )
    due_date = models.DateField(
        verbose_name='应归还日期'
    )
    return_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='实际归还日期'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='borrowed',
        verbose_name='状态'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        verbose_name = '借阅记录'
        verbose_name_plural = '借阅记录'

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('confirmed', '已确认'),
        ('cancelled', '已取消'),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='用户'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='图书'
    )
    reservation_date = models.DateField(
        default=date.today,
        verbose_name='预约日期'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        verbose_name = '预约记录'
        verbose_name_plural = '预约记录'
        unique_together = ('user', 'book', 'status')

class Notification(models.Model):
    TYPE_CHOICES = [
        ('borrow_due', '借阅到期提醒'),
        ('reservation_confirmed', '预约确认通知'),
        ('book_available', '图书可借通知'),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='用户'
    )
    type = models.CharField(
        max_length=25,
        choices=TYPE_CHOICES,
        verbose_name='通知类型'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='通知标题'
    )
    message = models.TextField(
        verbose_name='通知内容'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='是否已读'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']

class Comment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='用户'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='图书'
    )
    content = models.TextField(
        verbose_name='评论内容'
    )
    rating = models.IntegerField(
        choices=[(i, f'{i}星') for i in range(1, 6)],
        verbose_name='评分'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']

class Collection(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='collections',
        verbose_name='用户'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='collections',
        verbose_name='图书'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        unique_together = ('user', 'book')  # 每个用户对每本书只能收藏一次
