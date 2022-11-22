import io
import os

import cv2
from google.cloud import vision
from anpr.ocr import OCR, OCRResult, ResultLocation


class GoogleVisionOCR(OCR):
    """
    GoogleVisionOCR is a subclass of OCR. It implements the Google Vision API to read the text on images.
    """

    def __init__(
        self,
        default_image_path: str = "google_vision_image.png",
        default_confidence: float = 1,
    ):
        """
        Default constructor of the GoogleVisionOCR class

        @param default_image_path: path to store and read images given to the 'getTextFromImage' and
        'getTextFromImagePath' methods. The image needs to be stored locally because the Google vision API for python
        only takes an image path as an argument.
        @param default_confidence: confidence to return in the OCRResult object if text is detected. Google Vision API
        doesn't return a confidence level but is really accurate.
        """

        self.default_confidence = default_confidence

        # Store the path to the API key in the environment

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
            os.getcwd(), "google_vision_api_credentials.json"
        )

        self.default_image_path = default_image_path

        # Initialize client to connect to Google Cloud
        self.client = vision.ImageAnnotatorClient()

    def get_text_from_image_path(self, path: str) -> list[OCRResult]:
        """
        This method reads the text on the image at the given path, using Google Vision API.

        @param path: location the image is stored at. If this parameter is None, the default_image_path attribute of
        this class instance is used.
        @return: list containing OCRResults' found on the image.
        """

        # Open the image
        with io.open(path, "rb") as image_file:
            content = image_file.read()

        # Send image to the Google Vision API
        image = vision.Image(content=content)
        response = self.client.text_detection(image=image)  # type: ignore

        # If an error is returned, raise an exception
        if response.error.message:
            raise Exception(
                "{}\nFor more info on error messages, check: "
                "https://cloud.google.com/apis/design/errors".format(
                    response.error.message
                )
            )

        # Parse the results returned by Google Vision to OCRResult objects and return them in a list.
        return [
            self.create_ocr_result(text_annotation)
            for text_annotation in response.text_annotations
        ]

    def get_text_from_image(self, image) -> list[OCRResult]:
        """
        This method reads the text on the given image using Google Vision API.

        @param image: image to read text from.
        @return: list containing OCRResults' found on the image.
        """
        # Store image at the default image path
        cv2.imwrite(self.default_image_path, image)

        # Read text from this path
        return self.get_text_from_image_path(self.default_image_path)

    def create_ocr_result(self, text_annotation: vision.TextAnnotation) -> OCRResult:
        """
        Function to parse the text result of Google Vision into an OCRResult.

        @param text_annotation: result containing the information returned by Google Vision.
        @return: OCRResult object to use in different parts of code.
        """
        text = text_annotation.description
        vertices = text_annotation.bounding_poly.vertices
        topLeft = (vertices[0].x, vertices[0].y)
        bottomRight = (vertices[2].x, vertices[2].y)
        location = ResultLocation.fromTopLeftBottomRight(
            topLeft=topLeft, bottomRight=bottomRight
        )
        confidence = (
            self.default_confidence
        )  # Google Vision API doesn't return a confidence level but is really accurate

        return OCRResult(text, location, confidence)
