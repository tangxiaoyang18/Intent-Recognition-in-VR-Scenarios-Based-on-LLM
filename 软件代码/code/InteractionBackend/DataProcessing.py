import csv
import json


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


# 打开文件
with open('data.txt', 'r') as f:
    # 使用 readlines() 读取所有行并存储在 lines 列表中
    lines = f.readlines()

csv_path = './output/'
csv_idx = 0

# prev_time = int(json.loads(lines[0].strip().replace("'", "\""))['timestamp'])
prev_time = 0
cnt = 0

gaze_file = open(csv_path + str(csv_idx) + '_gaze.csv', 'w', newline='', encoding='utf-8')
gaze_writer = csv.writer(gaze_file)

hand_file = open(csv_path + str(csv_idx) + '_hand.csv', 'w', newline='', encoding='utf-8')
hand_writer = csv.writer(hand_file)

finger_file = open(csv_path + str(csv_idx) + '_finger.csv', 'w', newline='', encoding='utf-8')
finger_writer = csv.writer(finger_file)

for line in lines:
    data = json.loads(line.strip().replace("'", "\""))
    gaze_data = data['gaze_info']
    hand_data = data['hand_info']
    finger_data = data['finger_info']
    gaze_res = dict()
    hand_res = dict()
    finger_res = dict()
    gaze_res['timestamp'] = cnt // 5
    hand_res['timestamp'] = cnt // 5
    finger_res['timestamp'] = cnt // 5
    gaze_res.update(flatten_dict(gaze_data))
    hand_res.update(flatten_dict(hand_data))
    finger_res.update(flatten_dict(finger_data))

    if int(data['timestamp']) - prev_time > 1000:
        csv_idx += 1
        gaze_file.close()
        hand_file.close()
        finger_file.close()
        cnt = 0
        gaze_res['timestamp'] = cnt // 5
        hand_res['timestamp'] = cnt // 5
        finger_res['timestamp'] = cnt // 5

        gaze_file = open(csv_path + str(csv_idx) + '_gaze.csv', 'w', newline='', encoding='utf-8')
        gaze_writer = csv.writer(gaze_file)
        hand_file = open(csv_path + str(csv_idx) + '_hand.csv', 'w', newline='', encoding='utf-8')
        hand_writer = csv.writer(hand_file)
        finger_file = open(csv_path + str(csv_idx) + '_finger.csv', 'w', newline='', encoding='utf-8')
        finger_writer = csv.writer(finger_file)

        gaze_writer.writerow(gaze_res.keys())
        hand_writer.writerow(hand_res.keys())
        finger_writer.writerow(finger_res.keys())

    if cnt % 5 == 0:
        gaze_writer.writerow(gaze_res.values())
        hand_writer.writerow(hand_res.values())
        finger_writer.writerow(finger_res.values())
        prev_time = int(data['timestamp'])
    cnt += 1

gaze_file.close()
hand_file.close()
finger_file.close()

# for line in lines:
#     data = json.loads(line.strip().replace("'", "\""))
#     gaze_data = data['gaze_info']
#     hand_data = data['hand_info']
#     res = dict()
#     res['timestamp'] = data['timestamp']
#     res.update(flatten_dict(gaze_data))
#     res.update(flatten_dict(hand_data))
#     if int(res['timestamp']) - prev_time > 1000:
#         csv_idx += 1
#         f.close()
#         cnt = 0
#         f = open(csv_path + str(csv_idx) + '.csv', 'w', newline='', encoding='utf-8')
#         writer = csv.writer(f)
#         writer.writerow(res.keys())
#     if cnt % 5 == 0:
#         writer.writerow(res.values())
#         prev_time = int(res['timestamp'])
#     cnt += 1
#
# f.close()

# with open(csv_file, 'w', newline='', encoding='utf-8') as f:
#     writer = csv.writer(f)
#     flag = True
#     for line in lines:
#         data = json.loads(line.strip().replace("'", "\""))
#         gaze_data = data['gaze_info']
#         hand_data = data['hand_info']
#         res = dict()
#         res['timestamp'] = data['timestamp']
#         res.update(flatten_dict(gaze_data))
#         res.update(flatten_dict(hand_data))
#         if flag:
#             writer.writerow(res.keys())
#             flag = False
#         writer.writerow(res.values())


# 遍历每一行并处理
# for line in lines:
#     # 处理每一行数据，例如打印或者其他操作
#     output = json.loads(line.strip().replace("'", "\"").replace("True", "true").replace("False", "false"))
#     print(output)  # 使用 strip() 方法去除每行末尾的换行符
