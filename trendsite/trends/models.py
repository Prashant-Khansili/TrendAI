from django.db import models

class TrendCache(models.Model):
    keyword = models.CharField(max_length=255, unique=True)
    data = models.JSONField()
    last_fetched = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.keyword
