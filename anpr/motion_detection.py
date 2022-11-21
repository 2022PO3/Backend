import numpy as np
import cv2


def get_background(file_path):
    cap = cv2.VideoCapture(file_path)
    # we will randomly select 50 frames for the calculating the median
    frame_indices = range(0, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 1)
    # we will store the frames in array
    frames = []
    for idx in frame_indices:
        print(idx)
        # set the frame id to read that particular frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        frames.append(frame)
    # calculate the median
    median_frame = np.median(frames, axis=0).astype(np.uint8)
    return median_frame


def detect(input_file, background_file, group_size=8):

    # get the background model
    background = get_background(background_file)
    # cv2.imshow('Background', background)
    # cv2.waitKey(0)

    # convert the background model to grayscale format
    background = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
    frame_count = 0

    cap = cv2.VideoCapture(input_file)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frame_count += 1
            print(frame_count)
            orig_frame = frame.copy()
            # IMPORTANT STEP: convert the frame to grayscale first
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if frame_count % group_size == 0 or frame_count == 1:
                frame_diff_list = []
            # find the difference between current frame and base frame
            frame_diff = cv2.absdiff(gray, background)
            cv2.imshow("diff", frame_diff)
            # thresholding to convert the frame to binary
            ret, thres = cv2.threshold(frame_diff, 50, 255, cv2.THRESH_BINARY)
            # dilate the frame a bit to get some more white area...
            # ... makes the detection of contours a bit easier
            dilate_frame = cv2.dilate(thres, None, iterations=2)
            # append the final result into the `frame_diff_list`
            frame_diff_list.append(dilate_frame)  # type: ignore
            # if we have reached `consecutive_frame` number of frames
            if len(frame_diff_list) == group_size:  # type: ignore
                # add all the frames in the `frame_diff_list`
                sum_frames = sum(frame_diff_list)  # type: ignore
                # find the contours around the white segmented areas
                contours, hierarchy = cv2.findContours(
                    sum_frames, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE  # type: ignore
                )
                # draw the contours, not strictly necessary
                for i, cnt in enumerate(contours):
                    cv2.drawContours(frame, contours, i, (0, 0, 255), 3)
                for contour in contours:
                    # continue through the loop if contour area is less than 500...
                    # ... helps in removing noise detection
                    if cv2.contourArea(contour) < 500:
                        continue
                    # get the xmin, ymin, width, and height coordinates from the contours
                    (x, y, w, h) = cv2.boundingRect(contour)
                    # draw the bounding boxes
                    cv2.rectangle(orig_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                cv2.imshow("Detected Objects", orig_frame)
                if cv2.waitKey(100) & 0xFF == ord("q"):
                    break
        else:
            break
    cap.release()
    cv2.destroyAllWindows()


directory = "/Users/runeverachtert/Documents/Universiteit/P&O/3/Backend/utils/ANPR"
detect(directory + "/input.mov", directory + "/bg.mov")
