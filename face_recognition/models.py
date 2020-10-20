from django.db import models


def directory_path(instance, filename):
    file_format = filename[-3:]
    if file_format in ['jpg', 'jpeg']:
        return f'images/original/{filename}'
    elif file_format in ['avi', 'mp4']:
        return f'videos/{filename}'
    else:
        return f'./{filename}'


class Actor(models.Model):
    name = models.CharField(max_length=200, blank=True)  # ex) image_2018_10_09_08_29_30.jpg
    file = models.FileField(upload_to=directory_path)

    def __str__(self):
        return self.name
