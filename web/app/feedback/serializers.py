from rest_framework import serializers

from .models import DemoForm


class DemoFormSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name_of_requester')
    organisation_name = serializers.CharField(source='org_name')
    organisation_type = serializers.IntegerField(write_only=True)
    organization_type = serializers.CharField(source='org_type', read_only=True)
    objects = serializers.IntegerField(source='quantity_objects')
    
    class Meta:
        model = DemoForm
        fields = ['id', 'name', 'phone', 'organisation_name', 'organisation_type', 'organization_type', 'objects', 'created_at']
        read_only_fields = ['created_at']