from django.contrib.auth.models import UserManager
from django.utils import timezone

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from Organizations.serializers import CompanyMainInformationSerializer
from .models import User, UserCompanyRelation



class UserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        # exclude = '__all__'

    def create(self, validated_data):
        # print("DATA 2:", validated_data)
        password = validated_data['password']

        user = User.objects.create(**validated_data)
        # print("IS ACTIVE:", user.is_active)
        user.set_password(password)
        user.last_login = timezone.now()
        user.email = validated_data['username']
        user.change_password_date = timezone.now().today()
        user.save()

        return user



class LoginUserQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {'username': {'validators': []}, }
        fields = ['username', 'password']
        read_only = True



class UnprotectedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {'username': {'validators': []}, }
        fields = '__all__'
        read_only = True



class ProtectedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {'username': {'validators': []}, }
        exclude = ['password']
        read_only = True



class InfoUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {'username': {'validators': []}, }
        exclude = ['password', 'telegram_id', 'companies', 'groups', 'user_permissions',
                   'factories', 'is_superuser', 'is_staff', 'is_active']

    def to_representation(self, instance: User):
        serializer = super().to_representation(instance)
        telegram_id = instance.telegram_id
        serializer['telegram_confirmed'] = True if telegram_id else False
        try:
            if instance.organization_account:
                company = UserCompanyRelation.objects.get(user=instance).company
                serializer["company"] = CompanyMainInformationSerializer(company).data
        except:
            pass
        if instance.change_password_date is not None:
            serializer["need_change_password"] = False
        else:
            serializer["need_change_password"] = True
        return serializer



class InfoUpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {
            'first_name': {
                "error_messages": {
                    "max_length": "Не может быть более 30 символов",
                },
            },
            'last_name': {
                "error_messages": {
                    "max_length": "Не может быть более 150 символов",
                },
            },
            'middle_name': {
                "error_messages": {
                    "max_length": "Не может быть более 150 символов",
                },
            },
        }
        fields = ['first_name', 'last_name', 'middle_name', 'email',
                  'city', 'country', 'date_of_birth', 'telephone']



class OtherUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {'username': {'validators': []}, }
        fields = ['first_name', 'last_name', ]
        read_only = True



class UserContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'telephone']
        read_only = True

    def to_representation(self, instance: User):
        serializer = super().to_representation(instance)
        serializer['full_name'] = f"{instance.last_name} {instance.first_name} {instance.middle_name}"
        return serializer
    
    
    
class UserCompanyRelationForInvitationLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCompanyRelation
        fields = ['role', 'creator', 'product_interaction_permission',
                  'ordering_permission', 'company_info_permission', 
                  'factory_permission', 'add_users_permission', 'proposal_permission']
        
    def to_representation(self, instance: UserCompanyRelation):
        serializer = super().to_representation(instance)
        serializer['verified'] = False
