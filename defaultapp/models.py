from django.db import models

# Create your models here.



from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='joined_groups', blank=True)

    def __str__(self):
        return self.name

class File(models.Model):
    group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name="files")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload = models.FileField()
    filename = models.CharField(max_length=100)
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    description = models.TextField()
    keywords = models.TextField(blank=True, default="")  # Replace ArrayField

    def get_keywords(self):
      return self.keywords.split(",") if self.keywords else []

    def set_keywords(self, keywords_list):
        self.keywords = ",".join(keywords_list)

    def str(self):
        return self.filename

    
class Task(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="tasks")
    name = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Profile(models.Model):
    user: User = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.user.username


class Message(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="messages")
    subject = models.CharField(max_length=255)
    message = models.CharField(max_length=1000)
    message_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.subject

class GroupJoinRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.group.name}"