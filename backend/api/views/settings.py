from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import Settings
from api.serializers import SettingsSerializer

@api_view(['GET'])
def get_public_settings(request):
    settings, _ = Settings.objects.get_or_create(id=True)
    return Response({
        'success': True,
        'settings': SettingsSerializer(settings).data
    })
