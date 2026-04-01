from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

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
    category = models.CharField(
        max_length=CATEGORY_MAX_LENGTH,
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
