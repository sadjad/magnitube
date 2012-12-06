from django.db import models

class VideoInfo(models.Model):
	raw_url = models.CharField(max_length=255)
	video_id = models.CharField(max_length=255)