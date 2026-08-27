from django.core.files.storage import Storage
from django.core.files.base import File
import cloudinary
import cloudinary.uploader
import cloudinary.api


class CloudinaryStorage(Storage):

    def _save(self, name, content):
        result = cloudinary.uploader.upload(
            content,
            folder="voya/houses",
            resource_type="image"
        )

        return result["public_id"]

    def _open(self, name, mode="rb"):
        raise NotImplementedError(
            "Cloudinary files cannot be opened locally."
        )

    def delete(self, name):
        try:
            cloudinary.uploader.destroy(
                name,
                resource_type="image"
            )
        except Exception:
            pass

    def exists(self, name):
        return False

    def url(self, name):
        return cloudinary.CloudinaryImage(name).build_url(
            secure=True
        )