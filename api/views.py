from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, Product, Order
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['views', 'price']
    ordering = ['-views']  # Default ordering by trending
    
    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.query_params.get('category')
        is_promo = self.request.query_params.get('is_promo')
        if category:
            queryset = queryset.filter(category__id=category)
        if is_promo:
            queryset = queryset.filter(is_promo=True)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        print(f"COMMANDE CRÉÉE: ID={order.id}, Client={order.customer_name}")
        
        # Send email notification in background to avoid worker timeout
        import threading
        from django.core.mail import send_mail
        from django.conf import settings
        import logging

        def send_email_thread(order_id, customer_name, phone, city, address, items_description, status_display):
            try:
                subject = f"Nouvelle commande #{order_id} - {customer_name}"
                message = f"""
Une nouvelle commande a été reçue !

Détails de la commande:
-----------------------
ID Commande: {order_id}
Client: {customer_name}
Téléphone: {phone}
Ville: {city}
Adresse: {address}

Description des produits:
{items_description}

Statut: {status_display}
"""
                recipient_list = ['zouhirzaitoune36@gmail.com']
                
                send_mail(
                    subject, 
                    message, 
                    settings.DEFAULT_FROM_EMAIL, 
                    recipient_list,
                    fail_silently=False,
                )
                print(f"DEBUG: Email envoyé avec succès pour la commande #{order_id}")
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"ERREUR ENVOI EMAIL (Commande #{order_id}): {str(e)}")
                print(f"DEBUG: Erreur lors de l'envoi de l'email: {e}")

        # Start background thread
        thread = threading.Thread(
            target=send_email_thread, 
            args=(
                order.id, 
                order.customer_name, 
                order.phone, 
                order.city, 
                order.address, 
                order.items_description, 
                order.get_status_display()
            )
        )
        thread.daemon = True # Ensure thread doesn't block exit
        thread.start()

    
    def get_permissions(self):
        if self.action in ['create', 'test_email']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def daily_stats(self, request):
        from django.db.models import Count
        from django.db.models.functions import TruncDate
        from django.utils import timezone
        import datetime

        # Get current date info
        now = timezone.now()
        current_month = now.month
        current_year = now.year

        # Filter orders for this month
        orders = Order.objects.filter(
            created_at__year=current_year, 
            created_at__month=current_month
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        return Response(list(orders)) 

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def test_email(self, request):
        """Action pour tester l'envoi d'email directement depuis le navigateur"""
        from django.http import JsonResponse
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            print(f"Tentative de test email vers {settings.DEFAULT_FROM_EMAIL}")
            
            send_mail(
                'Test de Connexion Zaitouni Bio',
                'Si vous recevez ce message, la configuration email de votre serveur Railway est correcte !',
                settings.DEFAULT_FROM_EMAIL,
                ['zouhirzaitoune36@gmail.com'],
                fail_silently=False,
            )
            return JsonResponse({
                "success": True, 
                "message": "L'email de test a été envoyé avec succès à zouhirzaitoune36@gmail.com",
                "from_email": settings.DEFAULT_FROM_EMAIL
            })
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"ERREUR TEST EMAIL: {str(e)}")
            return JsonResponse({
                "success": False, 
                "error": str(e),
                "tip": "Vérifiez vos variables d'environnement Railway (EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)"
            })
