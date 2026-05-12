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
