from django.db import models
from jsonfield import JSONField


class Container(models.Model):
    name = models.CharField(max_length=50, verbose_name="视频载体", default='0')


class Scene(models.Model):
    name = models.CharField(max_length=50, verbose_name="业务场景", default='0')


class ProductCategory(models.Model):
    name = models.CharField(max_length=50, verbose_name="产品品类", default='0')


class Style(models.Model):
    name = models.CharField(max_length=50, verbose_name="产品风格", default='0')


class EditedVideo(models.Model):
    url = models.CharField(max_length=200)
    name = models.CharField(max_length=200, default="video")
    jumpArg = models.IntegerField(default=0)
    speedArg = models.IntegerField(default=0)
    positionArg = models.IntegerField(default=0)
    cramArg = models.IntegerField(default=0)
    colorArg = models.IntegerField(default=0)
    container = models.ForeignKey(Container, null=True, blank=True, on_delete=models.SET_NULL)
    scene = models.ForeignKey(Scene, null=True, blank=True, on_delete=models.SET_NULL)
    productCategory = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL)
    style = models.ForeignKey(Style, null=True, blank=True, on_delete=models.SET_NULL)
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
    userId = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    name = models.CharField(max_length=200, default="clip")
