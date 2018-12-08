from django.db import models
from jsonfield import JSONField


def user_directory_path(instance, filename):
    return 'video/{0}/{1}'.format(instance.name, filename)


class EditedVideo(models.Model):
    url = models.FileField(upload_to=user_directory_path, default="video")
    name = models.CharField(max_length=200, default="video")
    jumpArg = models.IntegerField(default=0)
    speedArg = models.IntegerField(default=0)
    positionArg = models.IntegerField(default=0)
    cramArg = models.IntegerField(default=0)
    colorArg = models.IntegerField(default=0)
    container = models.IntegerField(default=0)
    scenes = models.IntegerField(default=0)
    productCategory = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)


class ShotElement(models.Model):
    editedVideo = models.ForeignKey(EditedVideo, on_delete=models.CASCADE)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    during = models.IntegerField(default=0)
    speed = JSONField(default=[0, 0])
    position = JSONField(default=[0, 0])
    craMotion = JSONField(default=[0, 0])
    color = JSONField(default=[0, 0])
    shotSize = models.IntegerField(default=[0, 0])


class Clip(models.Model):
    url = models.FileField(upload_to='raw', default="clip")
    name = models.CharField(max_length=200, default="clip")
