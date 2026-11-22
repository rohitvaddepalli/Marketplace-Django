import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        data = response.data
        if isinstance(data, dict):
            message = data.get('detail') or data.get('message')
            if not message:
                # Extract first validation error string
                first_key = next(iter(data), None)
                val = data[first_key]
                if isinstance(val, list) and val:
                    message = f"{first_key}: {val[0]}"
                else:
                    message = f"{first_key}: {val}"
        elif isinstance(data, list) and data:
            message = str(data[0])
        else:
            message = str(data)

        code = getattr(exc, 'default_code', exc.__class__.__name__)
        return Response({
            'success': False,
            'message': str(message),
            'code': str(code)
        }, status=response.status_code)

    logger.exception("Unhandled server error: %s", exc)
    return Response({
        'success': False,
        'message': str(exc) if str(exc) else 'Internal server error',
        'code': 'SERVER_ERROR'
    }, status=500)
