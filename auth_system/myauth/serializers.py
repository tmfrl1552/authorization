from .models import Account
from rest_framework import serializers

class AccountSerializers(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('user_id', 'user_pw', 'user_email',)