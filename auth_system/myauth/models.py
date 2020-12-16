from django.db import models

# Create your models here.
class Account(models.Model):
    user_id = models.CharField(max_length=20, unique=True)
    user_pw = models.CharField(max_length=300)
    user_email = models.CharField(max_length=300)
    salt = models.CharField(max_length=40)
    is_active = models.IntegerField(max_length=2)

    class Meta:
        db_table = 'Account'