import uuid
import boto3
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

def get_boto3_client():
    if not settings.R2_ENDPOINT or not settings.R2_ACCESS_KEY_ID or not settings.R2_SECRET_ACCESS_KEY:
        return None
    return boto3.client(
        's3',
        endpoint_url=settings.R2_ENDPOINT,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name='auto',
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_upload_signature(request):
    s3 = get_boto3_client()
    if not s3:
        return Response({'success': False, 'message': 'R2 storage not configured'}, status=500)

    file_type = request.GET.get('type', 'image/jpeg')
    ext = file_type.split('/')[-1] if '/' in file_type else 'jpg'
    key = f"uploads/{uuid.uuid4().hex}.{ext}"

    presigned_url = s3.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': settings.R2_BUCKET,
            'Key': key,
            'ContentType': file_type
        },
        ExpiresIn=300
    )
    public_url = f"{settings.R2_PUBLIC_URL}/{key}" if settings.R2_PUBLIC_URL else presigned_url.split('?')[0]

    return Response({
        'success': True,
        'uploadUrl': presigned_url,
        'publicUrl': public_url,
        'key': key
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_files(request):
    s3 = get_boto3_client()
    if not s3:
        return Response({'success': False, 'message': 'R2 storage not configured'}, status=500)

    files = request.FILES.getlist('images')
    if not files:
        return Response({'success': False, 'message': 'No files uploaded'}, status=400)

    uploaded = []
    for f in files:
        ext = f.name.split('.')[-1] if '.' in f.name else 'jpg'
        key = f"uploads/{uuid.uuid4().hex}.{ext}"
        content_type = f.content_type or 'application/octet-stream'

        s3.put_object(
            Bucket=settings.R2_BUCKET,
            Key=key,
            Body=f.read(),
            ContentType=content_type
        )
        url = f"{settings.R2_PUBLIC_URL}/{key}" if settings.R2_PUBLIC_URL else key
        uploaded.append({
            'url': url,
            'publicId': key,
            'type': 'video' if content_type.startswith('video') else 'image'
        })

    return Response({'success': True, 'files': uploaded})
