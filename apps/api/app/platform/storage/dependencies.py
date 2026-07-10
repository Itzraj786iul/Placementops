from functools import lru_cache

from app.platform.storage.cloudinary_service import CloudinaryService


@lru_cache(maxsize=1)
def get_cloudinary_service() -> CloudinaryService:
    return CloudinaryService()
