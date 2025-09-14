import csv
import json
import math

from scipy.spatial.transform import Rotation as R
import numpy as np


def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            if isinstance(v, float):
                items.append((new_key, round(v, 2)))
            else:
                items.append((new_key, v))
    return dict(items)
def compute_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2 + (point1[2] - point2[2]) ** 2)
def compute_angle(quat1, quat2):
    # 将两个四元数转换为旋转对象
    r1 = R.from_quat(quat1)
    r2 = R.from_quat(quat2)

    # 计算两个旋转之间的相对旋转
    relative_rotation = r2 * r1.inv()

    # 获取旋转角度（弧度转度数）
    angle = relative_rotation.magnitude() * (180 / np.pi)
    return angle
def processing_hand_info(hand_info, pre_left_hand_rot, pre_right_hand_rot):
    temp = dict()
    temp['left_hand_pos_x'] = round(hand_info['left_hand_pos']['x'], 2)
    temp['left_hand_pos_y'] = round(hand_info['left_hand_pos']['y'], 2)
    temp['left_hand_pos_z'] = round(hand_info['left_hand_pos']['z'], 2)
    temp['right_hand_pos_x'] = round(hand_info['right_hand_pos']['x'], 2)
    temp['right_hand_pos_y'] = round(hand_info['right_hand_pos']['y'], 2)
    temp['right_hand_pos_z'] = round(hand_info['right_hand_pos']['z'], 2)

    temp['left_hand_rot_angle'] = round(compute_angle([pre_left_hand_rot['x'],
                                                       pre_left_hand_rot['y'],
                                                       pre_left_hand_rot['z'],
                                                       pre_left_hand_rot['w']],
                                                      [hand_info['left_hand_rot']['x'],
                                                       hand_info['left_hand_rot']['y'],
                                                       hand_info['left_hand_rot']['z'],
                                                       hand_info['left_hand_rot']['w']]), 2)
    temp['right_hand_rot_angle'] = round(compute_angle([pre_right_hand_rot['x'],
                                                        pre_right_hand_rot['y'],
                                                        pre_right_hand_rot['z'],
                                                        pre_right_hand_rot['w']],
                                                       [hand_info['right_hand_rot']['x'],
                                                        hand_info['right_hand_rot']['y'],
                                                        hand_info['right_hand_rot']['z'],
                                                        hand_info['right_hand_rot']['w']]), 2)

    temp['leftHand_head_dist'] = round(compute_distance(
        [hand_info['left_hand_pos']['x'], hand_info['left_hand_pos']['y'], hand_info['left_hand_pos']['z']],
        [0, 0, 0]), 2)
    temp['rightHand_head_dist'] = round(compute_distance(
        [hand_info['right_hand_pos']['x'], hand_info['right_hand_pos']['y'], hand_info['right_hand_pos']['z']],
        [0, 0, 0]), 2)
    temp['leftHand_rightHand_dist'] = round(compute_distance(
        [hand_info['left_hand_pos']['x'], hand_info['left_hand_pos']['y'], hand_info['left_hand_pos']['z']],
        [hand_info['right_hand_pos']['x'], hand_info['right_hand_pos']['y'], hand_info['right_hand_pos']['z']]), 2)
    return temp
def processing_finger_info(finger_info):
    temp = dict()
    temp['left_thumb_flex'] = finger_info['left_state'][0]
    temp['left_index_flex'] = finger_info['left_state'][1]
    temp['left_middle_flex'] = finger_info['left_state'][2]
    temp['left_ring_flex'] = finger_info['left_state'][3]
    temp['left_pinky_flex'] = finger_info['left_state'][4]
    temp['left_thumb_curl'] = finger_info['left_state'][5]
    temp['left_index_curl'] = finger_info['left_state'][6]
    temp['left_middle_curl'] = finger_info['left_state'][7]
    temp['left_ring_curl'] = finger_info['left_state'][8]
    temp['left_pinky_curl'] = finger_info['left_state'][9]

    temp['right_thumb_flex'] = finger_info['right_state'][0]
    temp['right_index_flex'] = finger_info['right_state'][1]
    temp['right_middle_flex'] = finger_info['right_state'][2]
    temp['right_ring_flex'] = finger_info['right_state'][3]
    temp['right_pinky_flex'] = finger_info['right_state'][4]
    temp['right_thumb_curl'] = finger_info['right_state'][5]
    temp['right_index_curl'] = finger_info['right_state'][6]
    temp['right_middle_curl'] = finger_info['right_state'][7]
    temp['right_ring_curl'] = finger_info['right_state'][8]
    temp['right_pinky_curl'] = finger_info['right_state'][9]

    temp['left_pinching'] = finger_info['left_pinching']
    temp['left_pointing'] = finger_info['left_pointing']
    temp['right_pinching'] = finger_info['right_pinching']
    temp['right_pointing'] = finger_info['right_pointing']

    return temp
class InteractionData:
    def __init__(self):
        self.is_empty = True
        self.cnt = 0
        self.task = ""
        self.gaze_data = ""
        self.hand_data = ""
        self.finger_data = ""
        self.speech_data = ""
        self.target_info = dict()
        self.prev_left_hand_rot = [0, 0, 0, 0]
        self.prev_right_hand_rot = [0, 0, 0, 0]

    def add_data(self, data):
        # data = json.loads(line.strip().replace("'", "\""))
        if self.cnt == 0:
            self.prev_left_hand_rot = data['hand_info']['left_hand_rot']
            self.prev_right_hand_rot = data['hand_info']['right_hand_rot']

        if self.cnt % 5 == 0:
            gaze_res = dict()
            hand_res = dict()
            finger_res = dict()
            gaze_res['timestamp'] = self.cnt // 5
            hand_res['timestamp'] = self.cnt // 5
            finger_res['timestamp'] = self.cnt // 5
            gaze_res.update(data['gaze_info'])
            hand_res.update(processing_hand_info(data['hand_info'], self.prev_left_hand_rot, self.prev_right_hand_rot))
            finger_res.update(processing_finger_info(data['finger_info']))

            self.task = data['task']

            self.prev_left_hand_rot = data['hand_info']['left_hand_rot']
            self.prev_right_hand_rot = data['hand_info']['right_hand_rot']

            if self.is_empty:
                self.gaze_data = ','.join(gaze_res.keys())
                self.hand_data = ','.join(hand_res.keys())
                self.finger_data = ','.join(finger_res.keys())
                self.is_empty = False

            self.gaze_data += '\n' + ','.join(str(value) for value in gaze_res.values())
            self.hand_data += '\n' + ','.join(str(value) for value in hand_res.values())
            self.finger_data += '\n' + ','.join(str(value) for value in finger_res.values())
            self.target_info[data['gaze_info']['target_name']] = data['target_info']

        self.cnt += 1

    def clear_data(self):
        self.is_empty = True
        self.cnt = 0
        self.task = ""
        self.gaze_data = ""
        self.hand_data = ""
        self.finger_data = ""
        self.target_info = dict()
        self.prev_left_hand_rot = [0, 0, 0, 0]
        self.prev_right_hand_rot = [0, 0, 0, 0]

    def get_gaze_data(self):
        return self.gaze_data

    def get_hand_data(self):
        return self.hand_data

    def get_finger_data(self):
        return self.finger_data

    def get_speech_data(self):
        return self.speech_data

    def get_target_info(self):
        return self.target_info

    def get_target_state(self, target_name):
        if target_name in self.target_info:
            return self.target_info[target_name]["state"]
        else:
            return None

    def save_data(self, id):
        with open('data/' + str(id) + 'task.txt', 'w', encoding='utf-8') as f:
            f.write(self.task)
        with open('data/' + str(id) + 'gaze.txt', 'w', encoding='utf-8') as f:
            f.write(self.gaze_data)
        with open('data/' + str(id) + 'hand.txt', 'w', encoding='utf-8') as f:
            f.write(self.hand_data)
        with open('data/' + str(id) + 'finger.txt', 'w', encoding='utf-8') as f:
            f.write(self.finger_data)
        with open('data/' + str(id) + 'speech.txt', 'w', encoding='utf-8') as f:
            f.write(self.speech_data)
        with open('data/' + str(id) + 'target.txt', 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.target_info, ensure_ascii=False))
