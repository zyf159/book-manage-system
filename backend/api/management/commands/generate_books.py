from django.core.management.base import BaseCommand
from api.models import Book
import random
import string

class Command(BaseCommand):
    help = '生成随机图书数据'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=50, help='生成图书数量')

    def handle(self, *args, **options):
        count = options['count']
        
        # 图书分类
        categories = ['计算机科学', '文学', '历史', '哲学', '艺术', '教育', '科学', '工程']
        
        # 出版社
        publishers = ['人民出版社', '清华大学出版社', '北京大学出版社', '上海人民出版社', '商务印书馆', '中华书局', '人民教育出版社', '科学出版社']
        
        # 馆藏地点
        locations = ['A区', 'B区', 'C区', 'D区', 'E区', 'F区']
        
        # 生成随机图书数据
        for i in range(count):
            # 生成随机书名
            title_length = random.randint(2, 5)
            title = ''.join(random.choice(string.ascii_letters) for _ in range(title_length)) + '图书'
            
            # 生成随机作者
            author_length = random.randint(2, 3)
            author = ''.join(random.choice(string.ascii_letters) for _ in range(author_length)) + '作者'
            
            # 生成随机ISBN
            isbn = ''.join(random.choice(string.digits) for _ in range(13))
            
            # 随机分类
            category = random.choice(categories)
            
            # 随机出版社
            publisher = random.choice(publishers)
            
            # 随机定价
            price = round(random.uniform(20, 100), 2)
            
            # 随机馆藏地点
            location = random.choice(locations)
            
            # 生成随机索书号
            call_number = f'{category[:2]}{random.randint(100, 999)}.{random.randint(10, 99)}'
            
            # 随机馆藏数量和可借数量
            total_quantity = random.randint(1, 10)
            available_quantity = random.randint(0, total_quantity)
            
            # 随机借阅期限
            borrow_period = random.randint(15, 60)
            
            # 生成随机简介
            description = f'这是一本关于{category}的图书，由{publisher}出版。'
            
            # 创建图书
            book = Book(
                title=title,
                author=author,
                isbn=isbn,
                category=category,
                publisher=publisher,
                price=price,
                location=location,
                call_number=call_number,
                total_quantity=total_quantity,
                available_quantity=available_quantity,
                borrow_period=borrow_period,
                description=description
            )
            book.save()
            
            self.stdout.write(self.style.SUCCESS(f'生成图书: {title}'))
        
        self.stdout.write(self.style.SUCCESS(f'成功生成 {count} 本图书'))
