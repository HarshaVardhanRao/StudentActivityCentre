from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0004_backfill_ref_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='ref_code',
            field=models.CharField(max_length=32, unique=True),
        ),
    ]
