class ResultLocation:
    """
    ResultLocation is used to store the location and rectangular boundaries of certain attributes on an image. For
    example, the location of text or a license plate.

    The coordinate system used has an x-axis pointing right and a y-axis pointing down like this:

    origin ------------>x
      |
      |
      |
     \/
      y

    """

    @classmethod
    def fromTopLeftBottomRight(cls, topLeft, bottomRight) -> "ResultLocation":
        """
        Constructor to create a ResultLocation based on the coordinates of the top-left and bottom-right corners.

        @param topLeft: tuple containing x and y coordinates of the top-left corner.
        @param bottomRight: tuple containing x and y coordinates of the bottom-right corner.
        @return: ResultLocation object.
        """

        # Use topLeft as origin and calculate width and height based of the difference in the coordinates.
        return cls(
            topLeft=topLeft,
            width=bottomRight[0] - topLeft[0],
            height=bottomRight[1] - topLeft[1],
        )

    def __init__(self, topLeft, width, height):
        """
        Default constructor of the ResultLocation class.

        @param topLeft: top-left corner (origin or start) of the result's boundaries.
        @param width: width of the rectangular boundary.
        @param height: height of the rectangular boundary.
        """
        self.topLeft = topLeft
        self.width = width
        self.height = height

    @property
    def topRight(self) -> tuple:
        """
        Property to access the location of the top-right corner.

        @return: tuple with x and y coordinate of the top-right corner.
        """
        return self.topLeft[0] + self.width, self.topLeft[1]

    @property
    def bottomLeft(self) -> tuple:
        """
        Property to access the location of the bottom-left corner.

        @return: tuple with x and y coordinate of the bottom-left corner.
        """
        return self.topLeft[0], self.topLeft[1] + self.height

    @property
    def bottomRight(self) -> tuple:
        """
        Property to access the location of the bottom-right corner.

        @return: tuple with x and y coordinate of the bottom-right corner.
        """
        return self.topLeft[0] + self.width, self.topLeft[1] + self.height

    def getCorners(self) -> list:
        """
        This method returns a list with all the corners of the surrounding rectangle.
        """
        return [self.topLeft, self.topRight, self.bottomRight, self.bottomLeft]

    def moveBy(self, x, y) -> None:
        """
        Method to move this ResultLocation's origin over a given x and y distance.

        @param x: distance to add to the x-coordinate of the current origin.
        @param y: distance to add to the y-coordinate of the current origin.
        @return: None, the class changes the topLeft attribute of this instance.
        """
        self.topLeft = (self.topLeft[0] + x, self.topLeft[1] + y)

    def moveByLocation(self, location: "ResultLocation") -> None:
        """
        Method to move this ResultLocation's origin by x and y coordinate of the top-left corner of the given
        ResultLocation object.

        @param location: ResultLocation to move by.
        @return: None, the class changes the topLeft attribute of this instance.
        """
        self.topLeft = (
            self.topLeft[0] + location.topLeft[0],
            self.topLeft[1] + location.topLeft[1],
        )


class OCRResult:
    """
    OCRResult contains the results of an OCR operation. This class stores the text on the image, its location and the
    confidence the algorithm has.
    """

    def __init__(self, text: str, location: ResultLocation, confidence: float):
        """
        Default constructor of the OCRResult class.

        @param text: text detected on the image.
        @param location: ResultLocation containing the location and boundaries of the detected text on the image.
        @param confidence: confidence returned by the used algorithm.
        """
        self.text = text
        self.location = location
        self.confidence = confidence


class OCR:
    """
    Abstract OCR class. This class does nothing, but is subclasses should have the 'getTextFromImage' method.
    """

    def getTextFromImage(self, image) -> list[OCRResult]:
        """
        This method finds and returns all the text on the given image.

        !!! In this abstract OCR class it returns None !!!

        @param image: image to perform OCR on.
        @return: list containing OCRResults' found on the image.
        """
        return []


if __name__ == "__main__":

    import cv2

    # Initialize the Google Vision OCR tool
    from google_vision_ocr import GoogleVisionOCR

    ocr = GoogleVisionOCR()

    # Initialize the EasyOCR OCR tool
    # from easy_ocr import EasyOCR
    # ocr = EasyOCR()

    # Load the image
    image = cv2.imread("google_vision_image.png")

    # Print text on the image
    print(ocr.getTextFromImage(image))
