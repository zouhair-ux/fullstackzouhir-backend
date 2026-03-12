from rest_framework import serializers
from .models import Category, Product, Order


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.image:
            representation['image'] = instance.image.url
        return representation


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name_fr', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.image:
            representation['image'] = instance.image.url
        return representation


class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name_fr', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'