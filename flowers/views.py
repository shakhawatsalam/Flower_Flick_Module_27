from django.shortcuts import render
from rest_framework.viewsets  import ModelViewSet
from flowers.models import Flower, Category, FlowerImage
from flowers.serializers import FlowerSerializer, CategorySerializer, FlowerImageSerializer
from flowers.permissions import IsAdminOrReadOnly
from flowers.filters import  ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.

class FlowerViewSet(ModelViewSet):
    queryset = Flower.objects.all()
    serializer_class = FlowerSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends=[DjangoFilterBackend]
    filterset_class = ProductFilter
    
    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of all flowers.

        This endpoint returns a paginated list of all flowers available in the store.
        """
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific flower by ID.

        This endpoint returns details of a specific flower identified by its ID.
        """
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new flower.

        This endpoint allows authenticated users with admin privileges to create a new flower.
        """
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        Update an existing flower.

        This endpoint allows authenticated users with admin privileges to update an existing flower.
        """
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update an existing flower.

        This endpoint allows authenticated users with admin privileges to partially update an existing flower.
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a flower.

        This endpoint allows authenticated users with admin privileges to delete a flower.
        """
        return super().destroy(request, *args, **kwargs)
    
class FlowerImageViewSet(ModelViewSet):
    serializer_class = FlowerImageSerializer
    permission_classes = [IsAdminOrReadOnly]
    def get_queryset(self):
        """
        Retrieve a list of images for a specific flower.

        This endpoint returns a list of images associated with a specific flower identified by `flower_pk`.
        """
        return FlowerImage.objects.filter(flower_id=self.kwargs.get('flower_pk'))

    def perform_create(self, serializer):
        """
        Create a new image for a specific flower.

        This endpoint allows authenticated users with admin privileges to create a new image for a specific flower.
        """
        serializer.save(flower_id=self.kwargs.get('flower_pk'))

    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of images for a specific flower.

        This endpoint returns a paginated list of images associated with a specific flower identified by `flower_pk`.
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific image for a specific flower by ID.

        This endpoint returns details of a specific image associated with a specific flower identified by `flower_pk` and `pk`.
        """
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Create a new image for a specific flower.

        This endpoint allows authenticated users with admin privileges to create a new image for a specific flower identified by `flower_pk`.

        
        """
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Update an existing image for a specific flower.

        This endpoint allows authenticated users with admin privileges to update an existing image for a specific flower identified by `flower_pk` and `pk`.

           
        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update an existing image for a specific flower.

        This endpoint allows authenticated users with admin privileges to partially update an existing image for a specific flower identified by `flower_pk` and `pk`.

       
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete an image for a specific flower.

        This endpoint allows authenticated users with admin privileges to delete an image for a specific flower identified by `flower_pk` and `pk`.

        
        """
        return super().destroy(request, *args, **kwargs) 
    
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    
    # views.py



class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of all categories.

        This endpoint returns a paginated list of all categories available in the store.
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific category by ID.

        This endpoint returns details of a specific category identified by its ID.
        """
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Create a new category.
        
        This endpoint allows authenticated users with admin privileges to create a new category.
        
        """
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Update an existing category.

        This endpoint allows authenticated users with admin privileges to update an existing category.

        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update an existing category.

        This endpoint allows authenticated users with admin privileges to partially update an existing category.
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a category.

        This endpoint allows authenticated users with admin privileges to delete a category.

          
        """
        return super().destroy(request, *args, **kwargs)
    
