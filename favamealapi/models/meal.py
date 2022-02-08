from django.db import models
from django.contrib.auth.models import User
from favamealapi.models.mealrating import MealRating



class Meal(models.Model):

    name = models.CharField(max_length=55)
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE)
    favorites = models.ManyToManyField(User, through="FavoriteMeal", related_name="favoritedMeal")


    # TODO: Add an user_rating custom properties
    @property
    def user_rating(self):
        return self.__user_rating
    
    @user_rating.setter
    def user_rating(self, user_id):
        user = User.objects.get(pk=user_id)
        try:
            rating = MealRating.objects.get(user=user, meal=self)
            if rating:
                self.__user_rating = rating.rating
        except:
            self.__user_rating = "Not rated"


    # TODO: Add an avg_rating custom properties
    @property
    def avg_rating(self):
        ratings = MealRating.objects.filter(meal=self)
        total_rating = 0
        if len(ratings) > 0:
            for rating in ratings:
                total_rating += rating.rating
            avg_rating = total_rating / len(ratings)
            rounded_average = round(avg_rating, 1)
            return rounded_average
        else:
            return "No ratings yet"


    # TODO: Add a favorite boolean to meal for current user
    @property
    def favorite(self):
        return self.__favorite
    
    @favorite.setter
    def favorite(self, value):
        self.__favorite = value



