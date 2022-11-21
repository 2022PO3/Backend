# import the necessary packages
import re

import cv2
import numpy as np

from dotenv import load_dotenv
from anpr.ocr import OCR, ResultLocation


class LicensePlateResult:
    """
    This class contains the result of a license plate recognition detection algorithm. It stores the detected text and
    the location on the image. It also provides a function to find a given license plate format in the detected text.
    """

    def __init__(self, text: str, location: ResultLocation):
        self.text = text
        self.location = location

    def match_format(self, formats: list) -> list:
        """
        This function matches the detected text to the given regex patterns. It also creates new LicensePlateResult's
        based on the matching patterns.
        @param formats: list for regex patterns
        @return: list of LicensePlateResult's with matched strings
        """

        # Make list for new results
        matches = []
        # Go over each regex format and find all matching strings
        for f in formats:
            matches += re.findall(f, self.text)

        return [LicensePlateResult(text, self.location) for text in matches]


# noinspection PyUnresolvedReferences
class ANPR:
    """
    This class can perform Automatic Number Plate Recognition (ANPR) on given images.
    """

    def __init__(
        self,
        selection_ocr: OCR,
        result_ocr: OCR,
        formats: list[str] | None = None,
        minAR: float = 3,
        maxAR: float = 7,
        verbosity: int = 4,
    ):
        """
        Default constructor of an ANPR object.

        @param selection_ocr: OCR object to use for selecting license plate candidates
        @param result_ocr: OCR object to use for reading the text on the final candidate
        @param formats: list of formats that the ANPR algorith should look our for. N means a number is expected, an L
        will be replaced by a letter. For example, a standard Belgian license plate would have the following format:
        'N-LLL-NNN'
        @param minAR: minimum aspect ratio of rectangular license plate candidates
        @param maxAR: maximum aspect ratio of rectangular license plate candidates
        @param verbosity: Variable to store how much debug output the class should give
               Levels of verbosity:
                * -1: nothing
                *  0: prints detected license plates
                *  1: show result image
                *  2: show all detected license plate candidates
                *  3: show result of black/white transformation to find license plate shapes
                *  4: show all steps
        """

        self.selection_ocr = selection_ocr
        self.result_ocr = result_ocr
        self.minAR = minAR
        self.maxAR = maxAR
        self.verbosity = verbosity

        # Transform custom format to regex ex. 'N-LLL-NNN' -> '[0-9]-[A-Z][A-Z][A-Z]-[0-9][0-9][0-9]'
        if formats is not None:
            formats = [f.replace("N", "[0-9]").replace("L", "[A-Z]") for f in formats]
        self.formats = formats

    def _debug_imshow(self, title: str, image, verbosity: int, waitKey=False) -> None:
        """
        Method to show debug or result images.

        @param title: Title of image window
        @param image: Image to show
        @param verbosity: level of verbosity required to show the image
        @param waitKey: boolean indicating whether the program should sleep until the user presses a key.
        """

        # Check if the verbosity of the image is below the verbosity specified by the user. A low verbosity means the
        # image is more important
        if verbosity <= self.verbosity:
            cv2.imshow(title, image)
            # Check to see if we should wait for a keypress
            if waitKey:
                cv2.waitKey(0)

    def _debug_print(self, text: object, verbosity) -> None:
        """
        Method print debug or result text

        @param text: Text to be printed
        @param verbosity: level of verbosity required to show the image
        """
        if verbosity <= self.verbosity:
            print(text)

    def _locate_license_plate_candidates(self, gray, keep=15) -> list[ResultLocation]:
        """
        This function searches for possible license plate candidates on an image. First , it looks for bright spots on
        the image as license plates have contrasting colors. Next, it will filter out the rectangular bright shapes
        because the license plates are always rectangular (only rectangles wit aspectratio's between minAR and maxAR are
        accepted). Most of the code used in this function was found on
        https://pyimagesearch.com/2020/09/21/opencv-automatic-license-number-plate-recognition-anpr-with-python/.

        @param gray: grayscale image to find candidates on.
        @param keep: how many candidates to return (at maximum).
        @return: list of contours of the detected candidates.
        """

        # perform a blackhat morphological operation that will allow
        # us to reveal dark regions (i.e., text) on light backgrounds
        # (i.e., the license plate itself)
        rectKern = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKern)
        self._debug_imshow("Blackhat", blackhat, 4)

        # next, find regions in the image that are light
        squareKern = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        light = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, squareKern)
        light = cv2.threshold(light, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        self._debug_imshow("Light Regions", light, 4)

        # compute the Scharr gradient representation of the blackhat
        # image in the x-direction and then scale the result back to
        # the range [0, 255]
        gradX = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
        gradX = np.absolute(gradX)
        (minVal, maxVal) = (np.min(gradX), np.max(gradX))
        gradX = 255 * ((gradX - minVal) / (maxVal - minVal))
        gradX = gradX.astype("uint8")
        self._debug_imshow("Scharr", gradX, 4)

        # blur the gradient representation, applying a closing
        # operation, and threshold the image using Otsu's method
        gradX = cv2.GaussianBlur(gradX, (5, 5), 0)
        gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKern)
        thresh = cv2.threshold(gradX, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        self._debug_imshow("Grad Thresh", thresh, 4)

        # take the bitwise AND between the threshold result and the
        # light regions of the image
        thresh = cv2.bitwise_and(thresh, thresh, mask=light)
        thresh = cv2.dilate(thresh, None, iterations=2)
        thresh = cv2.erode(thresh, None, iterations=1)
        self._debug_imshow("Final", thresh, 3, waitKey=True)

        # find contours in the thresholded image and sort them by
        # their size in descending order, keeping only the largest
        # ones
        contours = cv2.findContours(
            thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Get list of contours from cv2 result
        contours = contours[0]

        # Filter candidates based on aspect ratio
        accepted_contour_areas = []
        accepted_contour_locations = []
        for c in contours:
            (x, y, w, h) = cv2.boundingRect(c)

            ar = w / float(h)

            # check to see if the aspect ratio is rectangular
            if self.minAR <= ar <= self.maxAR:
                accepted_contour_areas.append(cv2.contourArea(c))
                location = ResultLocation((x, y), w, h)
                accepted_contour_locations.append(location)

        # Zip together contour area and location, the new list will contain tuples with the area at the 0 index and the
        # location on the 1 index.
        area_location_tuples = zip(accepted_contour_areas, accepted_contour_locations)

        # Sort and filter out the largest tuples
        keep = min(keep, len(accepted_contour_locations))
        largest_area_tuples = sorted(
            area_location_tuples, key=lambda tup: tup[0], reverse=True
        )[:keep]

        # Only return location on the image
        return [location for _, location in largest_area_tuples]

    def _pick_license_plate_location(
        self, gray: np.array, candidates: list[ResultLocation]  # type: ignore
    ) -> tuple[np.array, ResultLocation]:  # type: ignore
        """
        Pick the best estimation of the position of the license plate. Based on shape, contrast and presence of text.

        @param gray: grayscale image to find license plate on.
        @param candidates: list of locations with possible license plates.
        @return: tuple with cropped image and ResultLocation of the candidate that best fits the properties of a license plate.
        """

        # initialize the license plate contour and ROI
        lp_location = None
        roi = None
        # Variable to remember length of the longest string in license plate candidates
        longest_text_length = 0

        # loop over the license plate candidate contours
        self._debug_print(f"Picking out of {len(candidates)} candidates.", 2)
        for location in candidates:
            # store the license plate contour and extract the
            # license plate from the grayscale image and then
            # threshold it
            x, y = location.topLeft
            h = location.height
            w = location.width

            licensePlate = gray[y : y + h, x : x + w]

            roi_temp = cv2.threshold(
                licensePlate, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
            )[1]

            # Select the license plate with the longest text on it
            ocr_results = self.selection_ocr.get_text_from_image(roi_temp)  # Read text
            self._debug_print(
                f"Found Text on Candidate: {[r.text for r in ocr_results]}", 3
            )

            if len(ocr_results) > 0:
                self._debug_imshow("License Plate Candidate", licensePlate, 3)
                self._debug_imshow(
                    "ROI",
                    roi_temp,
                    3,
                    waitKey=True,
                )
                text_length = sum(len(r.text) for r in ocr_results)
                if text_length is None or longest_text_length < text_length:
                    longest_text_length = text_length
                    lp_location = location
                    roi = roi_temp

        # return a 2-tuple of the license plate ROI and the contour
        # associated with it
        if roi is not None:
            cv2.imshow("ROI", roi)
        return roi, lp_location  # type: ignore

    def find_and_ocr(
        self, image_path: str, doSelection: bool = True
    ) -> list[LicensePlateResult]:
        """
        Find license plate candidates and get the final text on it.

        @param image: image to find license plate on
        @param doSelection: boolean indicating whether the algorithm should first use the
        '_locate_license_plate_candidates' method to find rectangular candidates or just look for license plates formats
        in all the text on the image.
        @return: list of detected license plates
        """

        # Only OCR the license plate if the license plate ROI is not
        # empty
        if image_path is not None:
            # OCR the license plate
            ocr_results = self.result_ocr.get_text_from_image_path(image_path)  # type: ignore

            lp_results = [
                LicensePlateResult(result.text, result.location)
                for result in ocr_results
            ]

            # If formats are specified, look for these formats in the detected string
            if self.formats is not None:
                formatted_results = []
                for result in lp_results:
                    new_results = result.match_format(self.formats)
                    formatted_results += new_results
                lp_results = formatted_results

            self._debug_print([lp.text for lp in lp_results], 0)
            return lp_results


def cleanup_text(text: str) -> str:
    """
    strip out non-ASCII text so we can draw the text on the image using OpenCV

    @param text: text with a lot of possible characters
    @return: clean text with only characters that OpenCV can put on the image
    """
    return "".join([c if ord(c) < 128 else "" for c in text]).strip()


def show_text_on_image(
    image: np.array, text: str, location: ResultLocation, waitKey=True  # type: ignore
) -> None:
    """
    Show the text on the image with a rectangle surrounding it.

    @param image: image to show text on
    @param text: text to show
    @param location: location of the boundaries of the text:
    @param waitKey: whether the ui should wait for user input to cintinue
    """
    # Take a copy of the original image.
    image = image.copy()

    # Put the text and rectangle on the image.
    if text is not None and location is not None:
        # fit a rotated bounding box to the license plate contour and draw the bounding box on the license plate
        cv2.rectangle(image, location.topLeft, location.bottomRight, (0, 255, 0), 2)

        # compute a normal (unrotated) bounding box for the license plate and then draw the OCR'd license plate text on
        # the image
        cv2.putText(
            image,
            cleanup_text(text),
            (location.topLeft[0], location.topLeft[1] - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 255, 0),
            2,
        )
        # show the output ANPR image
        cv2.imshow(text, image)
        if waitKey:
            cv2.waitKey(0)
