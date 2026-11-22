from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.serializers import UserPublicSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_me(request):
    return Response({
        'success': True,
        'user': UserPublicSerializer(request.user).data
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    allowed = ['name', 'phone', 'address']
    updated = False

    for field in allowed:
        if field in request.data:
            setattr(user, field, request.data[field])
            updated = True

    if not updated:
        return Response({
            'success': False,
            'message': 'No valid fields to update'
        }, status=400)

    user.save()
    return Response({
        'success': True,
        'user': UserPublicSerializer(user).data
    })

@api_view(['POST'])
def logout_view(request):
    return Response({
        'success': True,
        'message': 'Logged out successfully'
    })
