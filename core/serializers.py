# core/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    OrganizationUnit, Ishchi, SualKateqoriyasi, Sual, 
    QiymetlendirmeDovru, Qiymetlendirme, Cavab, InkishafPlani,
    Feedback, Notification, CalendarEvent, QuickFeedback,
    PrivateNote, Idea, IdeaCategory, IdeaComment
)

User = get_user_model()


# --- Təşkilati Struktur Serializers ---
class OrganizationUnitSerializer(serializers.ModelSerializer):
    children_count = serializers.ReadOnlyField(source='get_children_count')
    employees_count = serializers.ReadOnlyField(source='get_employees_count')
    full_path = serializers.ReadOnlyField(source='get_full_path')
    
    class Meta:
        model = OrganizationUnit
        fields = ['id', 'name', 'type', 'parent', 'children_count', 'employees_count', 'full_path']


# --- İstifadəçi Serializers ---
class IshchiSerializer(serializers.ModelSerializer):
    organization_unit_name = serializers.CharField(source='organization_unit.name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = Ishchi
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'rol', 'vezife', 'organization_unit', 'organization_unit_name',
            'elaqe_nomresi', 'dogum_tarixi', 'profil_sekli', 'is_active',
            'date_joined', 'last_login'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }


class IshchiCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Ishchi
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'rol', 'vezife', 'organization_unit', 'elaqe_nomresi', 'dogum_tarixi'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Ishchi.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


# --- Sual Hovuzu Serializers ---
class SualKateqoriyasiSerializer(serializers.ModelSerializer):
    class Meta:
        model = SualKateqoriyasi
        fields = ['id', 'ad']


class SualSerializer(serializers.ModelSerializer):
    kateqoriya_name = serializers.CharField(source='kateqoriya.ad', read_only=True)
    yaradan_name = serializers.CharField(source='yaradan.get_full_name', read_only=True)
    
    class Meta:
        model = Sual
        fields = ['id', 'metn', 'kateqoriya', 'kateqoriya_name', 'applicable_to', 'yaradan', 'yaradan_name']


# --- Qiymətləndirmə Serializers ---
class QiymetlendirmeDovruSerializer(serializers.ModelSerializer):
    class Meta:
        model = QiymetlendirmeDovru
        fields = ['id', 'ad', 'bashlama_tarixi', 'bitme_tarixi', 'aktivdir', 'anonymity_level']


class QiymetlendirmeSerializer(serializers.ModelSerializer):
    qiymetlendirilecek_name = serializers.CharField(source='qiymetlendirilecek.get_full_name', read_only=True)
    qiymetlendiren_name = serializers.CharField(source='qiymetlendiren.get_full_name', read_only=True)
    dovr_name = serializers.CharField(source='dovr.ad', read_only=True)
    
    class Meta:
        model = Qiymetlendirme
        fields = [
            'id', 'qiymetlendirilecek', 'qiymetlendirilecek_name',
            'qiymetlendiren', 'qiymetlendiren_name',
            'dovr', 'dovr_name', 'status', 'yaradilma_tarixi',
            'tamamlanma_tarixi', 'umumi_qeyd'
        ]


class QiymetlendirmeDetailSerializer(QiymetlendirmeSerializer):
    """Tam detalları olan qiymətləndirmə serializer"""
    cavablar = serializers.SerializerMethodField()
    
    class Meta(QiymetlendirmeSerializer.Meta):
        fields = QiymetlendirmeSerializer.Meta.fields + ['cavablar']
    
    def get_cavablar(self, obj):
        cavablar = obj.cavablar.all()
        return CavabSerializer(cavablar, many=True).data


class CavabSerializer(serializers.ModelSerializer):
    sual_text = serializers.CharField(source='sual.metn', read_only=True)
    sual_category = serializers.CharField(source='sual.kateqoriya.ad', read_only=True)
    
    class Meta:
        model = Cavab
        fields = ['id', 'sual', 'sual_text', 'sual_category', 'xal', 'metnli_rey']


# --- İnkişaf Planı Serializers ---
class InkishafPlaniSerializer(serializers.ModelSerializer):
    ishchi_name = serializers.CharField(source='ishchi.get_full_name', read_only=True)
    dovr_name = serializers.CharField(source='dovr.ad', read_only=True)
    
    class Meta:
        model = InkishafPlani
        fields = [
            'id', 'ishchi', 'ishchi_name', 'dovr', 'dovr_name',
            'guclu_terefler', 'inkishaf_saheleri', 'hedefler',
            'ai_tovsiyeler', 'yaradilma_tarixi', 'yenileme_tarixi'
        ]


# --- Feedback Serializers ---
class FeedbackSerializer(serializers.ModelSerializer):
    gonderici_name = serializers.CharField(source='gonderici.get_full_name', read_only=True)
    alici_name = serializers.CharField(source='alici.get_full_name', read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'gonderici', 'gonderici_name', 'alici', 'alici_name',
            'kateqoriya', 'metn', 'anonymous', 'yaradilma_tarixi'
        ]


# --- Notification Serializers ---
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message', 'notification_type',
            'is_read', 'created_at', 'action_url'
        ]


# --- Calendar Serializers ---
class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = [
            'id', 'title', 'description', 'start_date', 'end_date',
            'event_type', 'is_all_day', 'created_by', 'created_at'
        ]


# --- Quick Feedback Serializers ---
class QuickFeedbackSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    receiver_name = serializers.CharField(source='receiver.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = QuickFeedback
        fields = [
            'id', 'sender', 'sender_name', 'receiver', 'receiver_name',
            'category', 'category_name', 'message', 'emoji',
            'is_anonymous', 'created_at'
        ]


# --- Private Notes Serializers ---
class PrivateNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    
    class Meta:
        model = PrivateNote
        fields = [
            'id', 'author', 'author_name', 'employee', 'employee_name',
            'title', 'content', 'created_at', 'updated_at'
        ]


# --- Idea Bank Serializers ---
class IdeaCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IdeaCategory
        fields = ['id', 'name', 'description']


class IdeaCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    
    class Meta:
        model = IdeaComment
        fields = ['id', 'author', 'author_name', 'content', 'created_at']


class IdeaSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    
    class Meta:
        model = Idea
        fields = [
            'id', 'title', 'description', 'author', 'author_name',
            'category', 'category_name', 'status', 'priority',
            'created_at', 'updated_at', 'comments_count', 'likes_count'
        ]


class IdeaDetailSerializer(IdeaSerializer):
    comments = IdeaCommentSerializer(many=True, read_only=True)
    
    class Meta(IdeaSerializer.Meta):
        fields = IdeaSerializer.Meta.fields + ['comments']


# --- Authentication Serializers ---
class UserProfileSerializer(serializers.ModelSerializer):
    """İstifadəçinin öz profilini görmək üçün"""
    organization_unit_name = serializers.CharField(source='organization_unit.name', read_only=True)
    
    class Meta:
        model = Ishchi
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'rol', 'vezife', 'organization_unit', 'organization_unit_name',
            'elaqe_nomresi', 'dogum_tarixi', 'profil_sekli',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login', 'rol']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Yeni şifrələr uyğun gəlmir.")
        return attrs