import cv2
import numpy as np
import os
import sys

def make_coordinates(image, line_parameters):
    # if len(line_parameters) == 2:
    slope, intercept = line_parameters
    y1 = image.shape[0]
    y2 = int(y1*(3/5))
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)
    return np.array([x1, y1, x2, y2])


def averaged_slope_intercept(image, lines):
    # left_fit = [(-1,1)]
    # right_fit = [(-1,-1)]

    left_fit = []
    right_fit = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            parameters = np.polyfit((x1, x2), (y1, y2), 1)

            if parameters is not None and len(parameters) == 2:
                slope = parameters[0]
                intercept = parameters[1]
                if slope < 0:
                    left_fit.append((slope, intercept))
                else:
                    right_fit.append((slope, intercept))
        

    # line parameters -
    left_fit_average = np.average(left_fit, axis = 0)
    right_fit_average = np.average(right_fit, axis = 0)

    left_line = make_coordinates(image, left_fit_average)
    right_line = make_coordinates(image, right_fit_average)

    return np.array([left_line, right_line])

def canny(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    canny = cv2.Canny(blur, 50, 150)
    return canny

def display_lines (image, lines):
    # return an array of zeros with the same shape and type as a given array
    line_image = np.zeros_like(image)
    if lines is not None:
        for x1, y1, x2, y2 in lines:
            if abs(x1) < sys.maxsize and abs(y1) < sys.maxsize and abs(x2) < sys.maxsize and abs(y2) < sys.maxsize:
                cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 10)
    return line_image

def region_of_interest(image):
    height = image.shape[0]
    polygons = np.array([
    [(200, height), (1100, height), (550,250)]
    ])
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, polygons, 255)
    mask_image = cv2.bitwise_and(image, mask)
    return mask_image


def get_camera():
    return cv2.VideoCapture(0, cv2.CAP_DSHOW)

def analyze_image():
    
    file_name = "test_image.jpg"
    file_path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(file_name)))

    image = cv2.imread(file_path)
    lane_image = np.copy(image)
    canny_image = canny(lane_image)
    cropped_image = region_of_interest(canny_image)

    lines = cv2.HoughLinesP(cropped_image, 2, np.pi/180, 100, np.array([]), minLineLength = 40, maxLineGap = 5)
    
    averaged_lines = averaged_slope_intercept(lane_image, lines)
    line_image = display_lines(lane_image, averaged_lines)
    combo_image = cv2.addWeighted(lane_image, 0.8, line_image, 1, 1)
    cv2.imshow("result", combo_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def analyze_video():
    file_name = "test2.mp4"
    # file_path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(file_name)))
    # cap = cv2.VideoCapture(file_path)

    # cap = cv2.VideoCapture(file_name)
    cap = get_camera()
    try: 
        while(cap.isOpened()):
            _, frame = cap.read()

            canny_image = canny(frame)
            cropped_image = region_of_interest(canny_image)
            
            # TODO: delete this line
            # combo_image = cropped_image
            
            lines = cv2.HoughLinesP(cropped_image, 2, np.pi/180, 100, np.array([]), minLineLength = 40, maxLineGap = 5)
            averaged_lines = averaged_slope_intercept(frame, lines)

            print (averaged_lines)
            line_image = display_lines(frame, averaged_lines)
            combo_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)

            cv2.imshow("result", combo_image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        print ("Interrupted")
    finally: 
        cap.release()
        cv2.destroyAllWindows()


def capture_video_from_camera():
    print ("Running 'capture_video_from_camera")
    
    # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap = get_camera()
    try:
        while(cap.isOpened()):
            print ("Camera is open")

            # Capture frame-by-frame
            ret, frame = cap.read()

            # Our operations on the frame come here
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Display the resulting frame
            cv2.imshow('frame', gray)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                # When everything done, release the capture

    except KeyboardInterrupt:
        print ("Interrupted")
    finally: 
        cap.release()
        cv2.destroyAllWindows()


def check_camera():
    print("check if camera is open")

    # https://stackoverflow.com/questions/53888878/cv2-warn0-terminating-async-callback-when-attempting-to-take-a-picture
    # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap = get_camera()
    result = cap.isOpened()

    cap.release()
    cv2.destroyAllWindows()
    
    print (result)
    return result

def save_video_file():
    # source: https://github.com/mohaseeb/raspberrypi3-opencv-docker
    # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap = get_camera()

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('/videos/output.avi', fourcc, 20.0, (640, 480))
    n_frames = 200
    while n_frames > 0:
        ret, frame = cap.read()
        if ret == True:
            # write the flipped frame
            out.write(frame)
            n_frames -= 1
        else:
            break
        print('frames to capture: {}'.format(n_frames))

    # Release everything when done
    cap.release()
    out.release()

def main():
    if check_camera():
        print("")
        # analyze_image()
        # analyze_video()
        # save_video_file()
        capture_video_from_camera()

# run main
main()
