import cv2
from sys import exit
import time

from modules import pose_module, video_module

video_path = "dances/video_test_14/annotated_dance_video.mp4"
pose_sequence_path = "dances/video_test_14/pose_sequence_data.json"

video_handler = video_module.Video_Capture_Handler(video_path)
print(f"FPS: {video_handler.get_framerate()}")
webcam_handler = video_module.Video_Capture_Handler(0)
if not webcam_handler.is_opened():
    print("Error: Unable to open video source.")
    exit()

pose_model = pose_module.Pose_Landmarker_Model("models/pose_landmarker_full.task")
pose_model.initialize()
video_pose_sequence = pose_module.Pose_Sequence.load_from_json_file(pose_sequence_path)

start_time_ms = time.time() * 1000

fps = video_handler.get_framerate()
frame_delay = int(1000/fps)
print(f"FPS: {fps}. Delay: {frame_delay}")
prev_dist = 20

last_real_time = time.time() * 1000

x = 0
while True:
    x+=1
    cur_real_time = time.time() * 1000
    real_time_since_start = int(cur_real_time-last_real_time)
    current_video_timestamp_ms = int(video_handler.cap.get(cv2.CAP_PROP_POS_MSEC))

    #video_ret, video_frame = video_handler.read_frame()
    video_handler.cap.set(cv2.CAP_PROP_POS_MSEC, real_time_since_start)
    video_ret, video_frame  = video_handler.read_frame()
    web_ret, web_frame = webcam_handler.read_frame()

    print(video_handler.cap.get(cv2.CAP_PROP_POS_MSEC))

    if not web_ret:
        break

    video_frame = cv2.flip(video_frame, 1)

    if web_frame is not None:
        t1 = time.time()
        #cv2.imshow("webcam", web_frame)
        #print(f"processing at {time_since_start_ms}")
        rgb_frame = cv2.cvtColor(web_frame, cv2.COLOR_BGR2RGB)

        pose_model.process_frame(rgb_frame, real_time_since_start)

        result = pose_model.get_latest_result()

        if result is not None:

            web_pose = pose_module.Pose(result.pose_landmarks, real_time_since_start)
            video_pose = video_pose_sequence.get_closest_pose_at(current_video_timestamp_ms)

            dist = pose_module.compare_poses(web_pose, video_pose)
            if dist is None: dist = prev_dist
            prev_dist = dist

            #print(dist)
            if dist > 0.5: cv2.putText(video_frame, str(round(dist, 2)), (50,100), cv2.FONT_HERSHEY_SIMPLEX, 4, (0,0,255), thickness=3)
            if dist < 0.5: cv2.putText(video_frame, str(round(dist, 2)), (50,100), cv2.FONT_HERSHEY_SIMPLEX, 4, (0,255,0), thickness=3)
        
        t2 = time.time()
        #print(t2-t1)
    if video_frame is not None:
        cv2.imshow("Test", video_frame)
    
    if cv2.waitKey(frame_delay) & 0xFF == ord("q"):
        break
video_handler.release()
webcam_handler.release()
cv2.destroyAllWindows()