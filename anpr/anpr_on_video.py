"""
!!! This code was made for testing earlier versions of the ANPR class. It now re-implements features already supported by
the ANPR class and tries to solve problems that are already solved !!!
"""


from anpr.license_plate_recognition import ANPR
import cv2
import numpy as np


class VideoANPR:
    def __init__(self, anpr: ANPR, imshow: bool = False):
        self.anpr = anpr

        # Open Webcam
        self.cap = cv2.VideoCapture(1)

        self.detected_strings = []

        self.imshow = imshow

        # Check if the webcam is opened correctly
        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")

    def detect_on_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            # frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            if ret:
                frame = resize_to_MP(frame)
                # Show input image
                if self.imshow:
                    cv2.imshow("Input", frame)
                # Get license plate texts from anpr
                (lpText, lpCnt) = self.anpr.find_and_ocr(frame, clearBorder=True)

                # Add texts to list of detected string
                if lpText is not None and len(lpText) > 0:
                    self.detected_strings += lpText
                if self.imshow:
                    self.anpr.show_text_on_image(frame, lpText, lpCnt, waitKey=False)
        else:
            raise IOError("Cannot open webcam")

    def check_for_license_plate(self, formats: list[str]):

        best_match = combine_strings(self.detected_strings, formats)

        if best_match is not None:
            self.detected_strings = []
            return best_match

    def __del__(self):
        self.cap.release()


def resize_to_MP(image, MP=5):
    height, width, channels = image.shape

    current_MP = width * height
    scale_factor = min(1, np.sqrt(MP * 1_000_000 / current_MP))

    # calculate the 50 percent of original dimensions
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)

    # dsize
    dsize = (new_width, new_height)

    # resize image
    output = cv2.resize(image, dsize)

    return output


def combine_strings(all_strings: list[str], formats: list[str]):
    strings = all_strings  # remove_doubles(all_strings)

    if formats is None:
        return sorted(strings, key=lambda x: len(x))
    else:
        # Convert strings to formats, the format and the actual string are stored in a dict
        formatted_strings_dict = {
            string: convert_to_format(string) for string in strings
        }

        # Go over all formats to find direct matches
        for format in formats:
            matches = dict(
                filter(lambda item: item[1] == format, formatted_strings_dict.items())
            )
            # Check original strings to find better option between matches
            # bv. if "1-ABC-123" and "1-ADC-123" match and "ABC" was also detected, the function should return "1-ABC-123"
            if len(matches) > 1:
                scoring_dict = {string: 0 for string in matches.keys()}
                for detected_string in all_strings:
                    for match_string in matches.keys():
                        if detected_string in match_string:
                            scoring_dict[match_string] += 1
                # Return the license plate with the most substring matches
                sorted_dict = sorted(
                    scoring_dict.items(), key=lambda item: item[1], reverse=True
                )
                return sorted_dict[0][0]
            elif len(matches) == 1:
                return list(matches.values())[0]

        # TODO: Check if a format can be matched by combining strings (backtracking?)


def combine_images(images, anpr: ANPR, formats: list[str]):
    """
    Combine texts from multiple images into 1 result.
    """
    all_strings = []

    for image in images:
        lpText, lpCnt = anpr.find_and_ocr(image)
        all_strings.append(lpText)

    return combine_strings(all_strings, formats)


def convert_to_format(string: str):
    """This function converts a string to a license plate format.
    - -: -
    - L: letter
    - N: number
    """
    format_string = ""
    for c in string:
        if c == "-":
            format_string += "-"
        elif c.isnumeric():
            format_string += "N"
        elif c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            format_string += "L"
    return format_string


def compare_to_format(string: str, format: str):
    """This function checks if a string matches the given licens plate format. The format can consist of the following
    characters:
        - -: -
        - L: letter
        - N: number
    """
    if len(string) != len(format):
        return False

    for i in range(len(string)):
        str_char = string[i]
        format_char = format[i]

        if format_char == "-":
            if str_char != "-":
                return False
        elif format_char == "L":
            if str_char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                return False
        elif format_char == "N":
            if not str_char.isnumeric():
                return False
    return True


def remove_doubles(strings):
    """
    This function removes all duplicate string from the list. For example: ["12", "123"] -> delete "12"
    """
    strings = set(strings)
    unique = strings.union()

    for string1 in strings:
        for string2 in strings:
            if string1 != string2 and string1 in string2:
                if string1 in unique:
                    unique.remove(string1)

    return unique


if __name__ == "__main__":
    # print("start")
    # strings = ['1-AB', '1-AB', '63', '21', '1-ABC', '123', '1-ABC123', '1-ABC123', '1-ABC', '123', '1-ABC123', '1-ABC-123', '1-ABC-123', '1ABC-123', '1-ABC', '123', '1-ABC-123', '1-ABC', '123', '1-ADC-123', '1-ABC-123', '1-ADC123', 'ABC', '123', 'ADC', '123', 'ADC', '123', '1-ABC', '123', '1-ADC-123', '1-ABC-123', '1-ABC', '123', '1-ABC', '123', '1-ABC-123', 'AI-']
    # print(combine_strings(strings, ["N-LLL-NNN"]))

    anpr = ANPR(debug=False)

    video_anpr = VideoANPR(anpr, imshow=False)

    while True:
        video_anpr.detect_on_frame()

        if len(video_anpr.detected_strings) > 5:
            print("Checking for license plate")
            lp = video_anpr.check_for_license_plate(["N-LLL-NNN"])
            print(lp)
            if lp is not None:
                break

        c = cv2.waitKey(1)
        if c == 113:
            break
