from django.shortcuts import render
from rest_framework.viewsets  import ModelViewSet
from flowers.models import Flower, Category
from flowers.serializers import FlowerSerializer, CategorySerializer
# Create your views here.

class FlowerViewSet(ModelViewSet):
    queryset = Flower.objects.all()
    serializer_class = FlowerSerializer
    
    
    
    
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
