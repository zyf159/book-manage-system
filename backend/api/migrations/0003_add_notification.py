from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_add_category_and_reservation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('borrow_due', '借阅到期提醒'), ('reservation_confirmed', '预约确认通知'), ('book_available', '图书可借通知')], max_length=25, verbose_name='通知类型')),
                ('title', models.CharField(max_length=200, verbose_name='通知标题')),
                ('message', models.TextField(verbose_name='通知内容')),
                ('is_read', models.BooleanField(default=False, verbose_name='是否已读')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='api.user', verbose_name='用户')),
            ],
            options={
                'verbose_name': '通知',
                'verbose_name_plural': '通知',
                'ordering': ['-created_at'],
            },
        ),
    ]
