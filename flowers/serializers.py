from rest_framework import serializers
from .models import Flower, Category, FlowerImage

class FlowerImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        model = FlowerImage
        fields = ['id','image']       
        
class FlowerSerializer(serializers.ModelSerializer):
    images = FlowerImageSerializer(many=True, read_only=True)
    class Meta:
        model = Flower
        fields = '__all__'
     
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']