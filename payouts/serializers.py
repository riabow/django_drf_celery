from rest_framework import serializers
from .models import PayoutRequest


class PayoutRequestSerializer(serializers.ModelSerializer):
    """Сериализатор для заявки на выплату."""
    
    class Meta:
        model = PayoutRequest
        fields = [
            'id',
            'amount',
            'currency',
            'recipient_details',
            'status',
            'comment',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_amount(self, value):
        """Валидация суммы выплаты."""
        if value <= 0:
            raise serializers.ValidationError("Сумма должна быть положительным числом.")
        return value
    
    def validate_recipient_details(self, value):
        """Валидация реквизитов получателя."""
        if not value or not value.strip():
            raise serializers.ValidationError("Реквизиты получателя обязательны для заполнения.")
        if len(value) > 1000:
            raise serializers.ValidationError("Реквизиты получателя не должны превышать 1000 символов.")
        return value.strip()
    
    def validate_comment(self, value):
        """Валидация комментария."""
        if value and len(value) > 500:
            raise serializers.ValidationError("Комментарий не должен превышать 500 символов.")
        return value


class PayoutRequestUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для частичного обновления заявки."""
    
    class Meta:
        model = PayoutRequest
        fields = [
            'status',
            'comment',
        ]
    
    def validate_status(self, value):
        """Валидация статуса."""
        valid_statuses = [choice[0] for choice in PayoutRequest.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Недопустимый статус. Допустимые значения: {', '.join(valid_statuses)}")
        return value
    
    def validate_comment(self, value):
        """Валидация комментария."""
        if value and len(value) > 500:
            raise serializers.ValidationError("Комментарий не должен превышать 500 символов.")
        return value

