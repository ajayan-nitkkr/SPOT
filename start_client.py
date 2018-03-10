import cv2
import json
try:
    import configparser
except:
    import ConfigParser as configparser
import time
import threading
try:
    from tensorflow_serving.apis import predict_pb2, prediction_service_pb2
    print('Using installed tensorflow_serving  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
except:
    print('Error using installed tensorflow_serving ***************************************')
    from tools.tf_serving_deployment.tensorflow_serving.apis import predict_pb2, prediction_service_pb2
# from tools.tf_serving_deployment.tensorflow_serving.apis import predict_pb2, prediction_service_pb2
import tensorflow as tf
from grpc.beta import implementations
from os.path import join
from google.protobuf.json_format import MessageToJson
try:
    from queue import Queue, Full
except:
    from Queue import Queue, Full

import os
import shutil



class ResultHandler(object):
    """Counter for the prediction results."""

    def __init__(self, concurrency):
        self._concurrency = concurrency
        self._responses = {}
        self._active = 0
        self._condition = threading.Condition()

    def add_response(self, id, response):
        with self._condition:
            self._responses[id] = response

    def dec_active(self):
        with self._condition:
            self._active -= 1
            self._condition.notify()

    def throttle(self):
        with self._condition:
            while self._active == self._concurrency:
                self._condition.wait()
            self._active += 1

    def get_response(self, id):
        with self._condition:
            while id not in self._responses:
                self._condition.wait()
            return self._responses[id]


def _create_rpc_callback(id, result_handler):
    """Creates RPC callback function.
    Args:
      label: The correct label for the predicted example.
      result_counter: Counter for the prediction result.
    Returns:
      The callback function.
    """

    def _callback(result_future):
        """Callback function.
        Calculates the statistics for the prediction result.
        Args:
          result_future: Result future of the RPC.
        """
        exception = result_future.exception()
        if exception:
            print(exception)
        else:
            response = result_future.result()
            result_handler.add_response(id, response)
        result_handler.dec_active()

    return _callback


class VideoClient(object):
    """ Splits and sends video to host server """

    def __init__(self, use_jpeg=True):
        ## Read configurations
        Config = configparser.ConfigParser()
        Config.read("config.ini")
        # self.video_file = join("..", "original_client", "demo.mp4")
        # self.video_file = join("/Users/donna/Documents/Teamcore/faster RCNN/poacher-recognition/tools", "original_client", "demo.mp4")

        self.host, self.port = "13.84.187.192", 9000
        self.concurrency = 8
        self.use_jpeg = use_jpeg

        self.channel = implementations.insecure_channel(self.host, self.port)
        self.stub = prediction_service_pb2.beta_create_PredictionService_stub(self.channel)
        self.result_handler = ResultHandler(self.concurrency)

        self.q = Queue()

    def send_frame(self, id, frame):
        request = predict_pb2.PredictRequest()
        request.model_spec.name = 'saved_model'
        if self.use_jpeg:
            request.model_spec.signature_name = "predict_post_jpeg"
            request.inputs['image'].CopyFrom(
                tf.contrib.util.make_tensor_proto(frame, shape=[]))
        else:
            request.model_spec.signature_name = "predict_post"
            request.inputs['image'].CopyFrom(
                tf.contrib.util.make_tensor_proto(frame, shape=frame.shape))

        self.result_handler.throttle()
        result_future = self.stub.Predict.future(request, 30.0)#10.0)
        result_future.add_done_callback(_create_rpc_callback(id, self.result_handler))

    def get_result(self, id):
        return self.result_handler.get_response(id)

    def get_next_frame(self, cap, skip=1):
        ## Capture frames from video
        ret, frame = cap.read()
        for _ in range(skip):
            cap.grab()
            ret, frame = cap.retrieve()

        if self.crop_info['invert']:
            frame = 255 - frame

        if self.use_jpeg:
            ret, buffer = cv2.imencode(".jpg", frame)
            return buffer.tobytes(), frame
        else:
            return frame, frame

    def annotate_image(self, frames, responses, ids):
        for i in xrange(len(responses)):
            bboxes, labels = self.get_boxes(responses[i])
            img = self.get_annotated_image(frames[i], bboxes, labels)
            
            #write frames to folder
            file_name = 'results/result_' + str(ids[i]) + '.jpg'
            file_path = join(self.app_path, file_name)
            cv2.imwrite(file_path, img)
            self.q.put(file_name)
            # while True:
            #     try:
            #         self.q.put(file_name, False, 1)
            #         break
            #     except Full:
            #         continue

    def get_boxes(self, response):
        jsonStr = MessageToJson(response)
        jsonObj = json.loads(jsonStr)['outputs']

        ## BOUNDING BOX
        try:
            bboxes = jsonObj['fin_bbox']['floatVal']
        except KeyError:
            #print('No bounding box!')                              
            return [],[]

        ## CLASS
        labels = jsonObj['fin_cls']['intVal']
        return bboxes, labels

    def get_annotated_image(self, im, bboxes, labels):
        """Draw detected bounding boxes."""
        if len(labels) == 0:
            return im

        overlay = im.copy()
        returnIm = im.copy()
        for i in xrange(len(bboxes)/4):
            box_index = i*4
            bbox = bboxes[box_index : box_index + 4]
            if labels[i] == 1:
                cv2.rectangle(overlay, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), \
                              (255,0,0), -1)
            else:
                cv2.rectangle(overlay, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), \
                              (0,255,0), -1)
            i += 4
        returnIm = cv2.addWeighted(overlay, 0.2, im, 1-0.2, 0)
        if self.crop_info['crop']:
            x1 = int(self.crop_info['cropLeft'])
            y1 = int(self.crop_info['cropTop'])
            x2 = int(self.crop_info['cropRight'])
            y2 = int(self.crop_info['cropBottom'])
            returnIm = returnIm[y1:y2, x1:x2]
        # cv2.imshow('TEST',returnIm)
        # cv2.waitKey(1)
        return returnIm

    def update_crop_info(self, crop_info):
        self.crop_info = crop_info
        print(self.crop_info)

    def start_client(self, max_frames=50, batch_size=2):
        shutil.rmtree('results')
        os.mkdir('results')
        cap = cv2.VideoCapture(self.video_file)
        try:
            id = 0
            while cap.isOpened() and (max_frames is None or id < max_frames):
                ids = []
                frames = []
                for _ in range(batch_size):
                    if id < max_frames:
                        image, frame = self.get_next_frame(cap)
                        id += 1
                        self.send_frame(id, image)
                        frames.append(frame)
                        ids.append(id)

                responses = [self.get_result(id) for id in ids]
                self.annotate_image(frames, responses, ids)
                print("received responses for ids: {}".format(ids))
        finally:
            cap.release()

vh = VideoClient(use_jpeg=True)

def get_video_client():
    global vh
    return vh

def start_video_client():
    global vh
    max_images = 100
    start = time.time()
    vh.start_client(max_images)
    print("processing {} images took {} seconds".format(max_images, time.time() - start))

if __name__ == '__main__':
    vh = VideoClient(use_jpeg=True)
    max_images = 100
    start = time.time()
    vh.start_client(max_images)
    print("processing {} images took {} seconds".format(max_images, time.time() - start))
