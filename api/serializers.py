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
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name_fr', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'category_name',
            'name_fr',
            'name_ar',
            'price',
            'description_fr',
            'description_ar',
            'origin_fr',
            'origin_ar',
            'benefits_fr',
            'benefits_ar',
            'image',
            'image_url',  # 👈 مهم
            'weight',
            'views',
            'is_promo',
            'discount_price',
        ]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None