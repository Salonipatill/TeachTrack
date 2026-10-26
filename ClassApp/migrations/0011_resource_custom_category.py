from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('ClassApp', '0010_student_batch_submission_academic_details')]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='category',
            field=models.CharField(db_index=True, max_length=100),
        ),
    ]
