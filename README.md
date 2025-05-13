# Save Image and File to WebDAV

A collection of custom nodes for ComfyUI that allows saving images and files to a WebDAV server.

## Features

- Save images to a WebDAV server with optional local backup on failure.
- Save files to a WebDAV server with optional local deletion after successful upload.
- Support for asynchronous uploads.
- User-friendly configuration options in the ComfyUI interface.

## Quickstart
1. Look up this extension in ComfyUI-Manager. If you are installing manually, clone this repository under `ComfyUI/custom_nodes`.
2. Restart ComfyUI.

## Configuration

### Save Image to WebDAV Node

- **image**: Input image to be saved.
- **webdav_url**: URL of the WebDAV server.
- **save_local_when_fail**: Option to save the image locally if the upload fails.
- **webdav_username**: Username for WebDAV authentication.
- **webdav_password**: Password for WebDAV authentication.
- **async_upload**: Option to upload the image asynchronously.

### Save File to WebDAV Node

- **filepath**: Path of the file to be uploaded.
- **delAfterUpload**: Option to delete the local file after successful upload.
- **webdav_url**: URL of the WebDAV server.
- **webdav_username**: Username for WebDAV authentication.
- **webdav_password**: Password for WebDAV authentication.
- **async_upload**: Option to upload the file asynchronously.

