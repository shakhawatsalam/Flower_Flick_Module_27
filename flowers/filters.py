from django_filters.rest_framework import FilterSet
from flowers.models import Flower



class ProductFilter(FilterSet):
    class Meta:
        model = Flower
        fields = {
            'category_id': ['exact'],
            'price': ['gt', 'lt']
        }