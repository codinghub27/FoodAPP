from rest_framework import serializers
from .models import Item


class ItemSerializer(serializers.ModelSerializer):
    user_name = serializers.StringRelatedField()
    item_image = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Item
        fields = ['id', 'user_name', 'item_name', 'item_desc', 'item_price', 'item_image']

    def validate(self, data):
        if data['item_name'].lower() == data['item_desc'].lower():
            return serializers.ValidationError("Item name and desc cant be same")
