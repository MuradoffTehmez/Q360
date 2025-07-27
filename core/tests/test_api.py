# core/tests/test_api.py

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from datetime import date, timedelta

from core.models import OrganizationUnit, QiymetlendirmeDovru, Notification

User = get_user_model()


@override_settings(LANGUAGE_CODE='en-us')
class UserAPITest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            rol=User.Rol.ADMIN
        )
        
        self.regular_user = User.objects.create_user(
            username="user",
            email="user@example.com", 
            password="userpass123",
            rol=User.Rol.ISHCHI
        )

    def authenticate_user(self, user):
        """İstifadəçini authenticate et"""
        self.client.force_authenticate(user=user)

    def test_user_list_as_admin(self):
        """Admin kimi istifadəçi siyahısını əldə etməyi test et"""
        self.authenticate_user(self.admin_user)
        
        url = reverse('ishchi-list')
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertTrue(len(response.data['results']) >= 2)

    def test_user_profile(self):
        """İstifadəçi profilini əldə etməyi test et"""
        self.authenticate_user(self.regular_user)
        
        url = reverse('ishchi-detail', kwargs={'pk': self.regular_user.pk})
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user')

    def test_user_create(self):
        """Yeni istifadəçi yaratmağı test et"""
        self.authenticate_user(self.admin_user)
        
        url = reverse('ishchi-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'rol': 'ISHCHI'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username='newuser').count(), 1)


@override_settings(LANGUAGE_CODE='en-us')
class DashboardAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            rol=User.Rol.ADMIN
        )
        
        # Test datası yarat
        self.dovr = QiymetlendirmeDovru.objects.create(
            ad="Test Dövrü",
            bashlama_tarixi=date.today(),
            bitme_tarixi=date.today() + timedelta(days=30),
            aktivdir=True
        )

    def authenticate_user(self):
        """İstifadəçini authenticate et"""
        self.client.force_authenticate(user=self.user)

    def test_dashboard_stats(self):
        """Dashboard statistikalarını test et"""
        self.authenticate_user()
        
        url = reverse('dashboard-stats')
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Gözlənilən sahələrin olduğunu yoxla
        expected_fields = [
            'pending_evaluations',
            'completed_evaluations', 
            'unread_notifications',
            'quick_feedback_received',
            'ideas_submitted'
        ]
        
        for field in expected_fields:
            self.assertIn(field, response.data)
            self.assertIsInstance(response.data[field], int)


@override_settings(LANGUAGE_CODE='en-us')
class OrganizationUnitAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            rol=User.Rol.ADMIN
        )
        
        self.parent_unit = OrganizationUnit.objects.create(
            name="Ana Şirkət",
            type=OrganizationUnit.UnitType.ALI_IDARE
        )
        
        self.child_unit = OrganizationUnit.objects.create(
            name="İT Departamenti",
            type=OrganizationUnit.UnitType.SHOBE,
            parent=self.parent_unit
        )

    def authenticate_user(self):
        """İstifadəçini authenticate et"""
        self.client.force_authenticate(user=self.user)

    def test_organization_unit_list(self):
        """Təşkilati vahidlər siyahısını test et"""
        self.authenticate_user()
        
        url = reverse('organizationunit-list')
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_organization_unit_children(self):
        """Təşkilati vahidin alt vahidlərini test et"""
        self.authenticate_user()
        
        url = reverse('organizationunit-children', kwargs={'pk': self.parent_unit.pk})
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'İT Departamenti')


@override_settings(LANGUAGE_CODE='en-us')
class NotificationAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        self.notification = Notification.objects.create(
            recipient=self.user,
            title="Test Bildirişi",
            message="Bu bir test bildirişidir.",
            notification_type=Notification.NotificationType.INFO
        )

    def authenticate_user(self):
        """İstifadəçini authenticate et"""
        self.client.force_authenticate(user=self.user)

    def test_notification_list(self):
        """İstifadəçinin bildirişlərini test et"""
        self.authenticate_user()
        
        url = reverse('notification-list')
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Bildirişi')

    def test_mark_notification_read(self):
        """Bildirişi oxunmuş kimi işarələməyi test et"""
        self.authenticate_user()
        
        url = reverse('notification-mark-read', kwargs={'pk': self.notification.pk})
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Bildirişin oxunmuş olduğunu yoxla
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)