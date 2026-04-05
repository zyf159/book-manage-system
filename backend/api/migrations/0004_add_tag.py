from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_add_notification'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='标签名称')),
                ('color', models.CharField(default='#409eff', max_length=7, verbose_name='标签颜色')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '图书标签',
                'verbose_name_plural': '图书标签',
            },
        ),
        migrations.AddField(
            model_name='book',
            name='tags',
            field=models.ManyToManyField(
                blank=True,
                related_name='books',
                to='api.tag',
                verbose_name='标签'
            ),
        ),
    ]
