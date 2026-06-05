from django.db import models

class TrendCache(models.Model):
    keyword = models.CharField(max_length=255, unique=True)
    data = models.JSONField()
    last_fetched = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.keyword


class Trend(models.Model):
    topic = models.CharField(max_length=255)
    context = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    source = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category}: {self.topic}"


class GeneratedPost(models.Model):
    request_hash = models.CharField(max_length=64, unique=True)
    topic = models.CharField(max_length=255)
    context = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    platforms = models.CharField(max_length=100, default="LinkedIn, Instagram, X")
    tone = models.CharField(max_length=60, blank=True)
    audience = models.CharField(max_length=120, blank=True)
    length = models.CharField(max_length=40, blank=True)
    emoji_style = models.CharField(max_length=40, blank=True)
    cta = models.CharField(max_length=120, blank=True)
    hashtags = models.CharField(max_length=120, blank=True)
    generated_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.topic} ({self.platforms})"
