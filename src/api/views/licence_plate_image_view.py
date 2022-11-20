import os
import io
import shutil
from google.cloud import vision

from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

from src.core.utils import OriginAPIView
from src.core.views import BackendResponse
from src.api.models import Image

from anpr.license_plate_recognition import ANPR
from anpr.google_vision_ocr import GoogleVisionOCR


class LicencePlateImageView(OriginAPIView):
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
        Image.objects.create(image=file)
        try:
            pass
            # google_vision_api(file.name)  # type: ignore
        except Exception as e:
            print(e)
            delete_file()
        # Make sure the image files get deleted.
        delete_file()
        return BackendResponse("Success", status=status.HTTP_200_OK)


def perform_ocr(image_path: str):
    anpr = ANPR(None, GoogleVisionOCR(), formats=["N-LLL-NNN"], verbosity=0)  # type: ignore
    image = cv2.imread(image_path)
    licence_plates = anpr.find_and_ocr(image, doSelection=False)
    print(licence_plates)


def google_vision_api(image_path: str):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
        os.getcwd(), "google_vision_api_credentials.json"
    )
    client = vision.ImageAnnotatorClient()
    with io.open(
        os.path.join(os.getcwd(), f"src/media/images/{image_path}"), "rb"
    ) as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)  # type: ignore
    print(response)


def delete_file() -> None:
    """
    Delete the entire directory of the image files, which makes sure that none remain on the
    server.
    """
    try:
        shutil.rmtree(os.path.join(os.getcwd(), "src/media/images"))
    except FileNotFoundError:
        pass
