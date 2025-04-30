from inspect import cleandoc
import requests
from io import BytesIO
from PIL import Image
import numpy as np

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
                "image": ("IMAGE", { "tooltip": "Single image or multi images"}),
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

    def _get_current_datetime(self):
        from datetime import datetime
        import random
        now = datetime.now()
        random_suffix = f"{random.randint(0, 999):03d}"  # 生成3位数的随机数字
        return now.strftime("%Y-%m-%d"), f"{now.strftime('%Y%m%d_%H%M%S')}_{random_suffix}"

    def _upload_to_webdav(self, data, url, headers, auth, save_local_when_fail, local_path=None):
        max_retries = 3
        retry_interval = 3  # 重试间隔为3秒
        retry_count = 0

        while retry_count < max_retries:
            try:
                response = requests.put(url, data=data, headers=headers, auth=auth)
                if response.status_code in [200, 201, 204]:
                    print(f"Successfully uploaded to {url}")
                    return True
                else:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"Failed to upload to WebDAV server: {response.status_code} - {response.text}. Retrying in {retry_interval} seconds... (Attempt {retry_count}/{max_retries})")
                        import time
                        time.sleep(retry_interval)
                    else:
                        print(f"Failed to upload to WebDAV server after {max_retries} attempts: {response.status_code} - {response.text}")
                        return False
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Failed to upload to WebDAV server: {e}. Retrying in {retry_interval} seconds... (Attempt {retry_count}/{max_retries})")
                    import time
                    time.sleep(retry_interval)
                else:
                    print(f"Failed to upload to WebDAV server after {max_retries} attempts: {e}")
                    return False

    def upload_image(self, image, webdav_url, webdav_username, webdav_password, save_local_when_fail, async_upload):
        # 处理image为数组的情况
        # if isinstance(image, (list, tuple)):
        #     images = image
        # else:
        #     images = [image]
        images = image
        results = []
        for img in images:
            # Convert the image tensor to a PIL Image
            # _image = img.squeeze().cpu().numpy()

            try:
                _image = img.squeeze().cpu().numpy()
                _image = Image.fromarray((_image * 255).astype('uint8'))
            except:
                i = 255. * img.cpu().numpy()
                _image = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            # Save the image to a BytesIO object
            img_byte_arr = BytesIO()
            _image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            # Get current date and time
            date_folder, time_str = self._get_current_datetime()
            file_name = f"{time_str}.png"
            print(f"Generated file name: {file_name}")

            headers = {'Content-Type': 'image/png'}
            auth = (webdav_username, webdav_password)
            upload_url = f"{webdav_url}/{date_folder}/{file_name}"

            if save_local_when_fail:
                import os
                fail_folder = os.path.join("output", "upload-fail", date_folder)
                fail_path = os.path.join(fail_folder, file_name)
            else:
                fail_path = None

            def upload_task():
                if not self._upload_to_webdav(img_byte_arr, upload_url, headers, auth, save_local_when_fail, fail_path):
                    if save_local_when_fail and fail_path:
                        self._save_locally(img_byte_arr, fail_path)

            if async_upload:
                import threading
                threading.Thread(target=upload_task).start()
            else:
                upload_task()

            results.append(img)

        return (results,)


class SaveFileToWebDAV:
    @classmethod
    def INPUT_TYPES(s):
        """
            Return a dictionary which contains config for all input fields.
        """
        return {
            "required": {
                "filepath": ("STRING", {
                    "multiline": False,
                }),
                "delAfterUpload": ("BOOLEAN", {
                    "default": False,
                    "label_on": "Yes",
                    "label_off": "No"
                }),
                "webdav_url": ("STRING", {
                    "multiline": False,
                    "default": "http://example.com/webdav/"
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

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filepath",)
    FUNCTION = "upload_file"
    CATEGORY = "File/WebDAV"
    OUTPUT_NODE = True

    def _get_current_datetime(self):
        from datetime import datetime
        now = datetime.now()
        return now.strftime("%Y-%m-%d"), now.strftime("%Y%m%d_%H%M%S")

    def _upload_to_webdav(self, data, url, headers, auth, delAfterUpload, filepath):
        try:
            response = requests.put(url, data=data, headers=headers, auth=auth)
            if response.status_code in [200, 201, 204]:
                print(f"Successfully uploaded to {url}")
                if delAfterUpload:
                    self._delete_file(filepath)
                return True
            else:
                print(f"Failed to upload to WebDAV server: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Failed to upload to WebDAV server: {e}")
            return False

    def _delete_file(self, filepath):
        import os
        import time
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                os.remove(filepath)
                print(f"Local file {filepath} deleted after successful upload.")
                break
            except PermissionError as e:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"File is still in use, retrying in 1 second... (Attempt {retry_count}/{max_retries})")
                    time.sleep(1)
                else:
                    print(f"Failed to delete local file {filepath} after {max_retries} attempts: {e}")

    def upload_file(self, filepath, delAfterUpload, webdav_url, webdav_username, webdav_password, async_upload):
        def upload_task():
            with open(filepath, 'rb') as file:
                file_data = file.read()
                date_folder, time_str = self._get_current_datetime()
                file_name = f"{time_str}_{filepath.split('/')[-1]}"
                upload_url = f"{webdav_url}/{date_folder}/{file_name}"
                headers = {'Content-Type': 'application/octet-stream'}
                auth = (webdav_username, webdav_password)
                self._upload_to_webdav(file_data, upload_url, headers, auth, delAfterUpload, filepath)

        if async_upload:
            import threading
            threading.Thread(target=upload_task).start()
        else:
            upload_task()

        return (filepath,)

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "SaveImageToWebDAV": SaveImageToWebDAV,
    "SaveFileToWebDAV": SaveFileToWebDAV
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageToWebDAV": "Save Image to WebDAV",
    "SaveFileToWebDAV": "Save File to WebDAV"
}
