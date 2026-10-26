from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('ClassApp', '0011_resource_custom_category')]

    operations = [
        migrations.CreateModel(
            name='ResourceFile',
            fields=[
                ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
                ('storage_name',models.CharField(max_length=255)),
                ('content',models.BinaryField()),
                ('created_at',models.DateTimeField(auto_now_add=True)),
                ('resource',models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name='stored_file',to='ClassApp.resource')),
            ],
        ),
    ]
