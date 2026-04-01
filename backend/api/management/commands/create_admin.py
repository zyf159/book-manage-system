from django.core.management.base import BaseCommand
from api.models import User
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = '创建管理员账户'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='管理员用户名')
        parser.add_argument('--student-id', type=str, default='admin123', help='管理员学号')
        parser.add_argument('--email', type=str, default='admin@example.com', help='管理员邮箱')
        parser.add_argument('--password', type=str, default='admin123456', help='管理员密码')

    def handle(self, *args, **options):
        username = options['username']
        student_id = options['student_id']
        email = options['email']
        password = options['password']
        
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'用户名 {username} 已存在'))
            return
        
        # 检查学号是否已存在
        if User.objects.filter(student_id=student_id).exists():
            self.stdout.write(self.style.WARNING(f'学号 {student_id} 已存在'))
            return
        
        # 创建管理员账户
        admin = User(
            username=username,
            student_id=student_id,
            email=email,
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        admin.password = make_password(password)
        admin.save()
        
        self.stdout.write(self.style.SUCCESS(f'管理员账户创建成功: {username}'))
        self.stdout.write(self.style.SUCCESS(f'学号: {student_id}'))
        self.stdout.write(self.style.SUCCESS(f'邮箱: {email}'))
        self.stdout.write(self.style.SUCCESS(f'密码: {password}'))
