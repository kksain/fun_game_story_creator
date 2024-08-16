from django.contrib.auth.models import User
from django.db import models


class Story(models.Model):
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    pdf_file = models.FileField(
        upload_to='exports/pdf/', null=True, blank=True)
    image_file = models.ImageField(
        upload_to='exports/images/', null=True, blank=True)

    def __str__(self):
        return self.title


class Contribution(models.Model):
    story = models.ForeignKey(
        Story, related_name='contributions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Contribution by {self.user.username} to {self.story.title}'
