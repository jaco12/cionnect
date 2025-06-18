from sqlite3 import IntegrityError

import pytest

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Group, File

import os
import django
from django.conf import settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'a09site.settings'  # replace with your project name
django.setup()

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Group, File, Task, Profile, Message, GroupJoinRequest
from django.core.files.uploadedfile import SimpleUploadedFile


class GroupModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="password")
        self.member = User.objects.create_user(username="member", password="password")
        self.group = Group.objects.create(
            name="Test Group", description="A group for testing", owner=self.owner
        )


    def test_group_creation(self):
        self.assertEqual(self.group.name, "Test Group")
        self.assertEqual(self.group.description, "A group for testing")
        self.assertEqual(self.group.owner, self.owner)

    def test_group_members(self):
        self.group.members.add(self.member)
        self.assertIn(self.member, self.group.members.all())

    def test_group_str(self):
        self.assertEqual(str(self.group), "Test Group")


class FileModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="uploader", password="password")
        self.group = Group.objects.create(name="Test Group", description="Testing Files", owner=self.owner)

        self.file = File.objects.create(
            group=self.group,
            upload=SimpleUploadedFile("test_file.txt", b"Test file content"),
            filename="test_file.txt",
            owner=self.owner,
            description="A test file",
            keywords="test,file",
        )

    def test_file_creation(self):
        self.assertIn('test_file', self.file.upload.name)
        '''self.assertEqual(self.file.filename, "test_file.txt")'''
        self.assertEqual(self.file.description, "A test file")
        self.assertEqual(self.file.owner, self.owner)
        self.assertEqual(self.file.get_keywords(), ["test", "file"])

'''
    def test_file_str(self):
        print(f"String representation of file: {str(self.file)}")
        self.assertIn('test_file', str(self.file))

        self.assertEqual(str(self.file), self.file.filename)
        '''



class TaskModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="password")
        self.group = Group.objects.create(name="Task Group", description="Testing Tasks", owner=self.owner)
        self.task = Task.objects.create(name="Test Task", group=self.group)

    def test_task_creation(self):
        self.assertEqual(self.task.name, "Test Task")
        self.assertEqual(self.task.completed, False)
        self.assertEqual(self.task.group, self.group)

    def test_task_str(self):
        self.assertEqual(str(self.task), "Test Task")

'''
class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="profile_user", password="password")
        try:
            self.profile = Profile.objects.create(user=self.user, nickname="Tester")
            print("Profile created successfully.")
        except IntegrityError:
            self.profile = Profile.objects.get(user=self.user)
            print("Profile already exists, retrieved existing profile.")

    def test_profile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.nickname, "Tester")

    def test_profile_str(self):
        self.assertEqual(str(self.profile), "profile_user")
        '''


class MessageModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="password")
        self.group = Group.objects.create(name="Message Group", description="Testing Messages", owner=self.owner)
        self.message = Message.objects.create(
            group=self.group, subject="Test Subject", message="Test message content"
        )

    def test_message_creation(self):
        self.assertEqual(self.message.group, self.group)
        self.assertEqual(self.message.subject, "Test Subject")
        self.assertEqual(self.message.message, "Test message content")

    def test_message_str(self):
        self.assertEqual(str(self.message), "Test Subject")


class GroupJoinRequestModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="request_user", password="password")
        self.owner = User.objects.create_user(username="owner", password="password")
        self.group = Group.objects.create(name="Request Group", description="Testing Requests", owner=self.owner)
        self.request = GroupJoinRequest.objects.create(user=self.user, group=self.group)

    def test_join_request_creation(self):
        self.assertEqual(self.request.user, self.user)
        self.assertEqual(self.request.group, self.group)

    def test_join_request_str(self):
        self.assertEqual(str(self.request), "request_user -> Request Group")

'''
'''

@pytest.mark.django_db  # Gives test access to the database
def test_project_create():
    # Create a dummy user (you need a user to be the owner of the project)
    user = User.objects.create_user(username="testuser", password="testpassword")

    # Create a dummy project
    group = Group.objects.create(
        name="Test Project",
        description="This is a test project.",
        owner=user
    )

    # Assert that the project was created and saved correctly
    assert group.name == "Test Project"
    assert group.description == "This is a test project."
    assert group.owner == user
    assert group.owner.username == "testuser"

@pytest.mark.django_db
class GroupModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.group = Group.objects.create(
            name='Test Group',
            description='This is a test group.',
            owner=self.user
        )

    def test_project_creation(self):
        self.assertEqual(self.group.name, 'Test Group')
        self.assertEqual(self.group.description, 'This is a test group.')
        self.assertEqual(self.group.owner.username, 'testuser')

    def test_project_str(self):
        self.assertEqual(str(self.group), 'Test Group')

@pytest.mark.django_db
class FileModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        # You might need to create a temporary file for this test
        self.group = Group.objects.create(
            name='Test Group',
            description='This is a test group.',
            owner=self.user
        )
        self.file = File.objects.create(
            group=self.group,
            upload=SimpleUploadedFile("test_file.txt", b"Test file content"),
            filename="test_file.txt",
            owner=self.user,
            description="A test file",
            keywords="test,file",
        )


    def test_document_creation(self):
        self.assertIn('test_file', self.file.upload.name)
        self.assertEqual(self.file.owner.username, 'testuser')
        self.assertEqual(self.file.group.name, 'Test Group')





