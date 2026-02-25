from rest_framework import serializers
from .models import Category, Product, Order


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name_fr', read_only=True)

    # 🔥 هذا اللي زدنا باش يرجّع رابط الصورة صحيح
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    # 🔥 هاد الدالة كتجيب URL ديال الصورة كامل
    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name_fr', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'