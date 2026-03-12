import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zadibio_backend_project.settings')
django.setup()

from api.models import Category, Product
from api.serializers import ProductSerializer
from django.core.files.uploadedfile import SimpleUploadedFile

def test_product_creation():
    try:
        # Create a test category
        cat = Category.objects.create(name_fr='Test Category', name_ar='تصنيف تجريبي')
        print(f"Created category: {cat.id}")

        # Prepare image
        with open('dummy.jpg', 'rb') as f:
            img_content = f.read()
        
        img = SimpleUploadedFile('test_image.jpg', img_content, content_type='image/jpeg')

        # Test data
        data = {
            'name_fr': 'Test Product',
            'name_ar': 'منتج تجريبي',
            'price': '150.00',
            'description_fr': 'Test description in French',
            'description_ar': 'وصف تجريبي بالعربية',
            'category': cat.id,
            'weight': '250ml',
            'is_promo': True,
            'discount_price': '120.00'
        }

        # Validate with serializer
        serializer = ProductSerializer(data=data)
        if not serializer.is_valid():
            print(f"Validation failed: {serializer.errors}")
            cat.delete()
            return

        print("Validation successful!")

        # Save with image
        product = serializer.save(image=img)
        print(f"Product saved successfully!")
        print(f"ID: {product.id}")
        # print(f"Image: {product.image}") # This might try to upload to Cloudinary if configured
        print(f"Weight: {product.weight}")

        # Verify fields
        assert product.name_fr == data['name_fr']
        assert product.weight == data['weight']
        assert product.is_promo == True
        
        print("All assertions passed!")

        # Cleanup
        product.delete()
        cat.delete()
        print("Cleanup successful!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if not os.path.exists('dummy.jpg'):
        with open('dummy.jpg', 'w') as f:
            f.write('dummy content')
    test_product_creation()
