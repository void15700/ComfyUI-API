
import urllib.request
import urllib.parse
from requests_toolbelt import MultipartEncoder


def upload_image(input_path, name, server_address, image_type="input", overwrite=False):
    with open(input_path, 'rb') as file:
        multipart_data = MultipartEncoder(
            fields= {
            'image': (name, file, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
        }
    )
        data = multipart_data
        headers = { 'Content-Type': multipart_data.content_type }
        request = urllib.request.Request("http://{}/upload/image".format(server_address), data=data, headers=headers)
        with urllib.request.urlopen(request) as response:
            return response.read()