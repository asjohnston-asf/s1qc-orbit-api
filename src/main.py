import requests
import json


def get_orbit(granule, orbit_type):
    platform = granule[0:3]
    date_time = f'{granule[17:21]}-{granule[21:23]}-{granule[23:25]}T{granule[26:28]}:{granule[28:30]}:{granule[30:32]}'

    params = {
        'product_type': orbit_type,
        'product_name__startswith': platform,
        'validity_start__lt': date_time,
        'validity_stop__gt': date_time,
        'ordering': '-creation_date',
        'page_size': '1',
    }

    response = requests.get(url='https://qc.sentinel1.eo.esa.int/api/v1/', params=params)
    response.raise_for_status()
    qc_data = response.json()

    orbit = None
    if qc_data['results']:
        orbit = qc_data['results'][0]
    return orbit


def lambda_handler(event, context):
    granule = event['queryStringParameters']['granule_name']
    response_type = event['queryStringParameters'].get('response_type')

    orbit = get_orbit(granule, 'AUX_POEORB')
    if not orbit:
        orbit = get_orbit(granule, 'AUX_RESORB')

    if not orbit:
        response = {
            'statusCode': 400,
            'body': f'No orbit found for {granule}',
        }
    elif response_type == 'json':
        response = {
            'statusCode': 200,
            'body': json.dumps(orbit),
        }
    else:
        response = {
            'statusCode': 307,
            'headers': {
                'Location': orbit['remote_url'],
            },
            'body': None,
        }

    return response
