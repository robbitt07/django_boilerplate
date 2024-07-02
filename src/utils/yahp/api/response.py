
from django.http import JsonResponse
from django.utils import timezone

from typing import Dict, List, Union


def api_response_wrapper(payload: Union[Dict, List], status: int, warnings: List = None):

    # Any 2** status, including 200, 201, 204 etc
    if status >= 200 and status < 300:
        data = {'results': payload, 'success': True }
    else:
        data = {'results': {}, 'error': payload, 'success': False }
    
    data.update({
        'response_timestamp': timezone.now(), 'warnings': warnings
    })
    response = JsonResponse(
        data=data, status=status, content_type='application/json'
    )
    return response
