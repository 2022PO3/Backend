import os
from anpr.ocr import OCR, OCRResult, ResultLocation
from easyocr import Reader


def createOCRResult(result: dict) -> OCRResult:
    """
    Function to parse the result dictionary of EasyOCR into an OCRResult.

    @param result: dictionary containing the information returned by EasyOCR.
    @return: OCRResult object to use in different parts of code.
    """
    text = result[1]
    location = ResultLocation.fromTopLeftBottomRight(
        topLeft=result[0][0], bottomRight=result[0][2]
    )
    confidence = result[2]

    return OCRResult(text, location, confidence)


class EasyOCR(OCR):
    """
    EasyOCR is a subclass of OCR that implements EasyOCR to read text on images. The English language it uses is stored
    in the src/anpr/models directory.
    """

    def __init__(
        self,
        model_storage_directory: str = os.path.join(
            os.getcwd(), "anpr/src/anpr/models"
        ),
    ):
        """
        Default constructor of the EasyOCR class.

        @param model_storage_directory: path string to the location of the language models directory.
        """
        # A string with all the possible characters in a license plate
        self.alphanumeric = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"
        print(os.getcwd())
        # Reader object for OCR
        self.reader = Reader(
            ["en"],
            gpu=False,
            download_enabled=False,
            model_storage_directory=model_storage_directory,
        )

    def getTextFromImage(self, image) -> list[OCRResult]:
        """
        This method reads the text on the given image using EasyOCR. The configuration used (decoder='greedy',
        paragraph = False) was found by testing different settings and selecting the ones that worked the best for
        detecting text on license plates.

        @param image: image to read text from.
        @return: list containing OCRResults' found on the image.
        """

        # Get results from the EasyOCR reader
        results = self.reader.readtext(
            image, decoder="greedy", allowlist=self.alphanumeric, paragraph=False
        )

        # Parse the dictionaries to OCRResult objects and return them in a list.
        return [createOCRResult(result) for result in results]
