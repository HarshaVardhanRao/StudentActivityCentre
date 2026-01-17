# Generated migration for EventReport model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0010_event_thumbnail'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Event report title', max_length=200)),
                ('description', models.TextField(help_text='Detailed description of the event and outcomes')),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('PENDING', 'Pending Approval'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='DRAFT', max_length=20)),
                ('total_attendees', models.PositiveIntegerField(default=0, help_text='Total number of attendees')),
                ('expected_attendees', models.PositiveIntegerField(default=0, help_text='Expected number of attendees')),
                ('highlights', models.TextField(blank=True, help_text='Key highlights and achievements')),
                ('challenges', models.TextField(blank=True, help_text='Challenges faced during the event')),
                ('lessons_learned', models.TextField(blank=True, help_text='Lessons learned and recommendations for future events')),
                ('budget_used', models.DecimalField(decimal_places=2, default=0, help_text='Budget amount used', max_digits=10)),
                ('budget_allocated', models.DecimalField(decimal_places=2, default=0, help_text='Budget amount allocated', max_digits=10)),
                ('file', models.FileField(blank=True, help_text='Attached report document or images', null=True, upload_to='event_reports/')),
                ('approval_notes', models.TextField(blank=True, help_text='Notes from approver')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('submitted_at', models.DateTimeField(blank=True, help_text='When report was submitted for approval', null=True)),
                ('approved_at', models.DateTimeField(blank=True, help_text='When report was approved/rejected', null=True)),
                ('approved_by', models.ForeignKey(blank=True, help_text='Admin or SAC Coordinator who approved the report', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_event_reports', to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_reports', to='events.event')),
                ('submitted_by', models.ForeignKey(help_text='Club coordinator or Club advisor who submitted the report', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='submitted_event_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Event Report',
                'verbose_name_plural': 'Event Reports',
                'ordering': ['-created_at'],
            },
        ),
    ]
