from django.db import models
from django.contrib.auth.models import User


class Restaurant(models.Model):

    name = models.CharField(max_length=55, unique=True)
    address = models.CharField(max_length=255)
    favorites = models.ManyToManyField(User, through="FavoriteRestaurant", related_name="favoritedRest")

    # TODO: Add a `favorite` custom property
    
    # @property
    # def favorite(self):
    #     return self.__favorite

    # @favorite.setter
    # def favorite(self, value):
    #     self.__favorite = value