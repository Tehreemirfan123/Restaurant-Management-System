from fastapi import APIRouter

from core.client_config import public_profile


router = APIRouter(tags=["Client config"])


@router.get("/client-config")
def read_client_config():
    """Public: the non-secret client profile (brand, terminology, features,
    enabled modules). The frontend can use this for labels and feature flags.
    """
    return public_profile()
