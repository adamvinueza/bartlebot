import requests


def toot(story_line):

    host_instance = 'https://hachyderm.io'
    token = 'AAAAA-BBBBB-CCCCC-DDDDD-EEEEE'

    headers = {}
    headers['Authorization'] = 'Bearer ' + token

    data = {}
    data['status'] = story_line
    data['visibility'] = 'public'

    response = requests.post(
        url=host_instance + '/api/v1/statuses', data=data, headers=headers)

    return response.status_code == 200

