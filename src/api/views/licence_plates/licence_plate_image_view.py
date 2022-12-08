import os
import re
import shutil

from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

from src.core.settings import DEBUG
from src.core.views import BackendResponse, _OriginAPIView
from src.api.models import Image, LicencePlate

from anpr.license_plate_recognition import ANPR
from anpr.google_vision_ocr import GoogleVisionOCR


class LicencePlateImageView(_OriginAPIView):
    """
    A view class to handle the incoming images in base64-format. From within this view, a image
    processing is performed and a request is sent to the Google Vision API. The image itself
    will NOT be stored in the database, but deleted when the function ends.
    """

    permission_classes = [AllowAny]
    origins = ["rpi"]

    def post(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().post(request, format)) is not None:
            return resp
        file = request.data["file"]  # type: ignore
        try:
            garage_id: int = request.headers["PO3-GARAGE-ID"]
        except KeyError:
            return BackendResponse(
                ["The PO3-GARAGE-ID-header is not sent with the request."],
                status=status.HTTP_400_BAD_REQUEST,
            )
        Image.objects.create(image=file)
        lp = ""
        try:
            lp = perform_ocr(file.name)  # type: ignore
        except Exception as e:
            delete_file(DEBUG)
            return BackendResponse(
                [f"An error occurred while parsing the licence plate image: {e}."],
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        stripped_lp_string = strip_special_chars(lp)
        out_int = LicencePlate.handle_licence_plate(stripped_lp_string, garage_id)
        delete_file(DEBUG)
        return BackendResponse(
            {"response": f"Successfully registered licence plate {stripped_lp_string}."}
            if out_int == 1
            else {
                "response": f"Successfully signed out licence plate {stripped_lp_string}."
            },
            status=status.HTTP_200_OK,
        )


def perform_ocr(image_path: str) -> str:
    anpr = ANPR(None, GoogleVisionOCR(), formats=["N-LLL-NNN", "N:LLL-NNN", "LLL-NNN"], verbosity=0)  # type: ignore
    ocr_results = anpr.find_and_ocr(
        os.path.join(os.getcwd(), f"src/media/images/{image_path}")
    )
    if not ocr_results:
        raise Exception("No licence plates detected on the image.")

    lp = "".join([lp.text for lp in ocr_results])
    return lp


def strip_special_chars(string: str) -> str:
    """
    Strips out all special characters from a given string.
    """
    return re.sub(r"\W", "", string)


def delete_file(debug: bool) -> None:
    """
    Delete the entire directory of the image files, which makes sure that none remain on the
    server.
    """
    if not debug:
        try:
            shutil.rmtree(os.path.join(os.getcwd(), "src/media/images"))
        except FileNotFoundError:
            pass
        # Delete record from the database.
        try:
            Image.objects.all().delete()
        except Exception as e:
            print("Image deletion exception:", e)
