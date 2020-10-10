from django.db import models


# Create your models here.
class Actor(models.Model):
    name = models.CharField(max_length=100)  # ex) image_2018_10_09_08_29_30.jpg
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.name
