from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Message
from api.serializers import MessageSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_messages(request, room_id):
    parts = room_id.split('_')
    my_id = str(request.user.id)

    if len(parts) != 2 or my_id not in parts:
        return Response({'success': False, 'message': 'Access denied to this chat room'}, status=403)

    messages = Message.objects.filter(room_id=room_id).select_related('sender').order_by('created_at')[:50]
    return Response({'success': True, 'messages': MessageSerializer(messages, many=True).data})
