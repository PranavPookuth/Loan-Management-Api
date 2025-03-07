# Generated by Django 5.1.6 on 2025-03-02 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_id', models.CharField(blank=True, max_length=20, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tenure', models.IntegerField()),
                ('interest_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('monthly_installment', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_interest', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('amount_remaining', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('CLOSED', 'Closed')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
