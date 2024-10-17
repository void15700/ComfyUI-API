import websocket
import uuid
import json
import urllib.request
import urllib.parse


class ComfyUI:
    def __init__(self, filename, username, server_address, workflow = "KingdomAvatarCutout.json"):
        self.image_filename = filename
        self.username = username
        self.server_address = server_address
        self.workflow = workflow
        self.client_id = str(uuid.uuid4())
        # self.main()
        
    def queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
        return json.loads(urllib.request.urlopen(req).read())

    def get_image(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen("http://{}/view?{}".format(self.server_address, url_values)) as response:
            return response.read()

    def get_history(self, prompt_id):
        with urllib.request.urlopen("http://{}/history/{}".format(self.server_address, prompt_id)) as response:
            return json.loads(response.read())

    def get_images(self, ws, prompt):
        prompt_id = self.queue_prompt(prompt)['prompt_id']
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break #Execution is done
            else:
                # If you want to be able to decode the binary stream for latent previews, here is how you can do it:
                # bytesIO = BytesIO(out[8:])
                # preview_image = Image.open(bytesIO) # This is your preview in PIL image format, store it in a global
                continue #previews are binary data

        history = self.get_history(prompt_id)[prompt_id]
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            images_output = []
            if 'images' in node_output:
                for image in node_output['images']:
                    image_data = self.get_image(image['filename'], image['subfolder'], image['type'])
                    images_output.append(image_data)
            output_images[node_id] = images_output

        return output_images

    def main(self):
            
        with open(self.workflow, "r") as file:
            prompt = json.load(file)

        prompt["73"]["inputs"]["image"] = self.image_filename
        prompt["77"]["inputs"]["separator"] = self.username

        ws = websocket.WebSocket()
        ws.connect("ws://{}/ws?clientId={}".format(self.server_address, self.client_id))
        images = self.get_images(ws, prompt)
        ws.close() # for in case this example is used in an environment where it will be repeatedly called, like in a Gradio app. otherwise, you'll randomly receive connection timeouts
        #Commented out code to display the output images:
        images_data = []
        
        for node_id in images:
            for image_data in images[node_id]:
                images_data.append(image_data)
        #         from PIL import Image
        #         import io
        #         image = Image.open(io.BytesIO(image_data))
        #         image.show()

        return images_data


with open("settings.json", "r") as file:
    settings = json.load(file)

image_filename = settings["image_filename"]
username = settings["username"]
server_address = settings["server_address"]
workflow = settings["workflow"]

output = ComfyUI(
    filename=image_filename,
    username=username,
    server_address=server_address,
    workflow=workflow
     ).main()

# est wait time 30-60s

for img_data in output:
    from PIL import Image
    import io
    image = Image.open(io.BytesIO(img_data))
    image.show()
