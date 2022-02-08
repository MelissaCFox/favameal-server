"""View module for handling requests about meals"""
from termios import ECHOE
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from favamealapi.models import Meal, MealRating, Restaurant, FavoriteMeal
from favamealapi.views.restaurant import RestaurantSerializer
from django.contrib.auth.models import User


class MealSerializer(serializers.ModelSerializer):
    """JSON serializer for meals"""
    restaurant = RestaurantSerializer(many=False)

    class Meta:
        model = Meal
        fields = ('id', 'name', 'restaurant', 'favorites', 'avg_rating',
                  'user_rating', 'favorite') 


class MealView(ViewSet):
    """ViewSet for handling meal requests"""

    def create(self, request):
        """Handle POST operations for meals

        Returns:
            Response -- JSON serialized meal instance
        """
        meal = Meal()
        meal.name = request.data["name"]
        meal.restaurant = Restaurant.objects.get(pk=request.data["restaurant_id"])


        try:
            meal.save()
            serializer = MealSerializer(
                meal, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single meal

        Returns:
            Response -- JSON serialized meal instance
        """
        try:
            meal = Meal.objects.get(pk=pk)
            user = User.objects.get(pk=request.auth.user.id)
            # TODO: Get the rating for current user and assign to `user_rating` property
            meal.user_rating = user.id

            # TODO: Assign a value to the `is_favorite` property of requested meal
            
            meal.favorite = user in meal.favorites.all()


            serializer = MealSerializer(
                meal, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """Handle GET requests to meals resource

        Returns:
            Response -- JSON serialized list of meals
        """
        meals = Meal.objects.all()
        user = User.objects.get(pk=request.auth.user.id)
        # TODO: Get the rating for current user and assign to `user_rating` property
        # TODO: Assign a value to the `is_favorite` property of each meal
        for meal in meals:
            meal.favorite = user in meal.favorites.all()
            meal.user_rating = user.id


        serializer = MealSerializer(
            meals, many=True, context={'request': request})

        return Response(serializer.data)

    # TODO: Add a custom action named `rate` that will allow a client to send a
    #  POST and a PUT request to /meals/3/rate
    @action(methods=['post', 'put'], detail=True)
    def rate(self, request, pk):
        meal = Meal.objects.get(pk=pk)
        user = User.objects.get(pk=request.auth.user.id)
        try:
            meal_rating = MealRating.objects.get(meal=meal, user=user)
            if request.method == 'POST':
                return Response({'message': 'Meal rating already exists for user'}, status=status.HTTP_400_BAD_REQUEST)
            elif request.method == 'PUT':
                meal_rating.rating = request.data['rating']
                meal_rating.save()
                return Response({'message': 'Meal rating updated'}, status=status.HTTP_204_NO_CONTENT)
        
        except:
            if request.method == 'POST':
                MealRating.objects.create(
                        user=user,
                        meal=meal,
                        rating=request.data['rating']
                    )
                return Response({'message': 'Meal rating added'}, status=status.HTTP_201_CREATED)


    # TODO: Add a custom action named `star` that will allow a client to send a
    #  POST and a DELETE request to /meals/3/star.
    @action(methods=['post', 'delete'], detail=True)
    def star(self, request, pk):
        meal = Meal.objects.get(pk=pk)
        user = User.objects.get(pk=request.auth.user.id)
        if request.method == 'POST':
            meal.favorites.add(user)
            return Response({'message': 'Meal favorite added'}, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            meal.favorites.remove(user)
            return Response({'message': 'Meal favorite removed'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'Method not allowed'}, status=status.HTTP_400_BAD_REQUEST)
