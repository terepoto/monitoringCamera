from django.db import models


class Faces(models.Model):
    rekognition_face_id = models.CharField(max_length=255)
    face_img = models.CharField(max_length=255)


class Position_History(models.Model):
    face_id = models.CharField(max_length=255)
    camera_id = models.CharField(max_length=255)
    position_x = models.CharField(max_length=255)
    position_y = models.CharField(max_length=255)


class Cameras(models.Model):
    ip = models.CharField(max_length=255)
    room_id = models.CharField(max_length=255)


class Rooms(models.Model):
    name = models.CharField(max_length=255)
