from inspect import cleandoc
import requests
from io import BytesIO
from PIL import Image

class SaveImageToWebDAV:
    """
    A node to save an image to a WebDAV server.

    Class methods
    -------------
    INPUT_TYPES (dict):
        Tell the main program input parameters of nodes.
    IS_CHANGED:
        optional method to control when the node is re executed.

    Attributes
    ----------
    RETURN_TYPES (`tuple`):
        The type of each element in the output tuple.
    RETURN_NAMES (`tuple`):
        Optional: The name of each output in the output tuple.
    FUNCTION (`str`):
        The name of the entry-point method. For example, if `FUNCTION = "execute"` then it will run SaveImageToWebDAV().execute()
    OUTPUT_NODE ([`bool`]):
        If this node is an output node that outputs a result/image from the graph. The SaveImage node is an example.
        The backend iterates on these output nodes and tries to execute all their parents if their parent graph is properly connected.
        Assumed to be False if not present.
    CATEGORY (`str`):
        The category the node should appear in the UI.
    execute(s) -> tuple || None:
        The entry point method. The name of this method must be the same as the value of property `FUNCTION`.
        For example, if `FUNCTION = "execute"` then this method's name must be `execute`, if `FUNCTION = "foo"` then it must be `foo`.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
            Return a dictionary which contains config for all input fields.
            Some types (string): "MODEL", "VAE", "CLIP", "CONDITIONING", "LATENT", "IMAGE", "INT", "STRING", "FLOAT".
            Input types "INT", "STRING" or "FLOAT" are special values for fields on the node.
            The type can be a list for selection.

            Returns: `dict`:
                - Key input_fields_group (`string`): Can be either required, hidden or optional. A node class must have property `required`
                - Value input_fields (`dict`): Contains input fields config:
                    * Key field_name (`string`): Name of a entry-point method's argument
                    * Value field_config (`tuple`):
                        + First value is a string indicate the type of field or a list for selection.
                        + Secound value is a config for type "INT", "STRING" or "FLOAT".
        """
        return {
            "required": {
                "image": ("IMAGE", { "tooltip": "This is an image"}),
                "webdav_url": ("STRING", {
                    "multiline": False,
                    "default": "http://example.com/webdav/"
                }),
                "save_local_when_fail": ("BOOLEAN", {
                    "default": False,
                    "label_on": "Yes",
                    "label_off": "No"
                }),
                "webdav_username": ("STRING", {
                    "multiline": False,
                    "default": "username"
                }),
                "webdav_password": ("STRING", {
                    "multiline": False,
                    "default": "password"
                }),
                "async_upload": ("BOOLEAN", {
                    "default": False,
                    "label_on": "Yes",
                    "label_off": "No"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)  # 修改输出类型为图片
    RETURN_NAMES = ("image",)  # 修改输出名称为image
    FUNCTION = "upload_image"
    CATEGORY = "Image/WebDAV"
    OUTPUT_NODE = True  # 增加输出节点标志，以便在UI中显示预览

    def upload_image(self, image, webdav_url, webdav_username, webdav_password, save_local_when_fail, async_upload):
        # Convert the image tensor to a PIL Image
        _image = image.squeeze().cpu().numpy()
        _image = Image.fromarray((_image * 255).astype('uint8'))

        # Save the image to a BytesIO object
        img_byte_arr = BytesIO()
        _image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Get current date and time
        from datetime import datetime
        now = datetime.now()
        date_folder = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%Y%m%d_%H%M%S")
        file_name = f"{time_str}.png"
        print(f"Generated file name: {file_name}")  # 调试日志：生成的文件名

        def upload_and_handle_failure():
            # Upload the image to the WebDAV server
            headers = {
                'Content-Type': 'image/png'
            }
            auth = (webdav_username, webdav_password)
            upload_url = f"{webdav_url}/{date_folder}/{file_name}"

            uploadSuccess = False

            try:
                print("Uploading...")  # 调试日志：保存到字节流
                response = requests.put(upload_url, data=img_byte_arr, headers=headers, auth=auth)
                if response.status_code in [200, 201, 204]:
                    print(f"Image successfully uploaded to {upload_url}")  # 上传成功日志
                    uploadSuccess = True
                else:
                    print(f"Failed to upload image to WebDAV server: {response.status_code} - {response.text}")  # 上传失败日志
                    uploadSuccess = False
            except requests.exceptions.RequestException as e:
                    print(f"Failed to upload image to WebDAV server: {e}")
                    uploadSuccess = False

            if uploadSuccess == False:
                if save_local_when_fail:
                    import os
                    fail_folder = os.path.join("output","upload-fail", date_folder)
                    os.makedirs(fail_folder, exist_ok=True)
                    fail_path = os.path.join(fail_folder, file_name)
                    _image.save(fail_path)
                    print(f"Image saved locally at {fail_path}")  # 本地保存日志

        if async_upload:
            import threading
            threading.Thread(target=upload_and_handle_failure).start()
        else:
            upload_and_handle_failure()

        return (image,)

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "SaveImageToWebDAV": SaveImageToWebDAV
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageToWebDAV": "Save Image to WebDAV"
}
