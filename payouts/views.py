from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import PayoutRequest
from .serializers import PayoutRequestSerializer, PayoutRequestUpdateSerializer
from .tasks import process_payout_request


class PayoutRequestViewSet(viewsets.ModelViewSet):
    """ViewSet для управления заявками на выплату."""
    
    queryset = PayoutRequest.objects.all()
    serializer_class = PayoutRequestSerializer
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'partial_update':
            return PayoutRequestUpdateSerializer
        return PayoutRequestSerializer
    
    def create(self, request, *args, **kwargs):
        """Создание новой заявки с запуском Celery задачи."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Создаем заявку со статусом 'pending'
        payout_request = serializer.save(status='pending')
        
        # Запускаем асинхронную задачу обработки
        process_payout_request.delay(payout_request.id)
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def list(self, request, *args, **kwargs):
        """Получение списка заявок."""
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """Получение заявки по идентификатору."""
        return super().retrieve(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление заявки."""
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Удаление заявки."""
        return super().destroy(request, *args, **kwargs)

