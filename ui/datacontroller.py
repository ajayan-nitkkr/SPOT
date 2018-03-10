import json
# import cv2


class DataController:
    def __init__(self, controller):
        print 'initialize data controller'
        print 'controller:', controller
        self.controller = controller

    def preprocess_video(self):
        print 'preprocess video'
        # payload = json.loads(request.get_data().decode('utf-8'))

        global vh, video_path
        # try:
        #     video_path = int(payload['video_path'])
        # except:
        #     video_path = payload['video_path']
        video_path = self.controller.view.text_video_path
        # update video and app path in reomte client
        # vh.video_file = video_path
        vh.video_file = video_path
        vh.app_path = app.root_path

        # update video and app path in local client
        local_vh.update_paths(video_path, app.root_path)

        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        curr = int(round(time.time() * 1000))
        first_img = 'frames/first.jpg'
        first_img_path = os.path.join(app.root_path, first_img)
        cv2.imwrite(first_img_path, frame)
        #
        # return first_img + '?r=' + str(curr)