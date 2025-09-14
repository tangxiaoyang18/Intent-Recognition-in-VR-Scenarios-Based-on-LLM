import json
import time
import ast
import asyncio
import threading
import concurrent.futures

from zhipuai import ZhipuAI
from PromptTemplate import gaze_prompt, hand_prompt, finger_prompt
# from PromptTemplate import gaze_data, hand_data, finger_data
from PromptTemplate import intention_prompt_begin_1, intention_prompt_begin_2, intention_prompt_end
from PromptTemplate import operation_prompt_begin, operation_prompt_end


client = ZhipuAI(api_key="3cc617941e3f40db98a930f8712734d9.mpKQZ7lKPKi9Sqd6")
result = dict()

operation_res = dict()


def round_dict(d):
    for k, v in d.items():
        if isinstance(v, dict):
            round_dict(v)
        else:
            if isinstance(v, float):
                d[k] = round(v, 2)
    return d


def extract_substring1(s):
    # 找到第一个 '{' 的位置
    start = s.find('[')

    # 找到最后一个 '}' 的位置
    end = s.rfind(']')

    # 如果都找到，截取子字符串
    if start != -1 and end != -1 and start < end:
        return s[start:end + 1]
    else:
        return ("[{\"intention\": \"无法检测交互意图\", \"possibility\": 10}, "
                "{\"intention\": \"null\", \"possibility\": 0}, "
                "{\"intention\": \"null\", \"possibility\": 0}]")


def extract_substring2(s):
    # 找到第一个 '{' 的位置
    start = s.find('{')

    # 找到最后一个 '}' 的位置
    end = s.rfind('}')

    # 如果都找到，截取子字符串
    if start != -1 and end != -1 and start < end:
        return s[start:end + 1]
    else:
        return "{\"type\": 0}"


def gaze_session(gaze_data):
    response = client.chat.completions.create(
        model="glm-4-0520",
        messages=[
            {"role": "system", "content": gaze_prompt},
            {"role": "user", "content": gaze_data}
        ]
    )
    return response.choices[0].message.content


def gaze_handel(gaze_data):
    print("Gaze session started")
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(gaze_session, gaze_data)
        try:
            res = future.result(timeout=8)
        except concurrent.futures.TimeoutError:
            res = "无注视信息分析结果"
    result["gaze"] = res
    print("Gaze session finished in {} seconds".format(time.time() - start))


def hand_session(hand_data):
    response = client.chat.completions.create(
        model="glm-4-0520",
        messages=[
            {"role": "system", "content": hand_prompt},
            {"role": "user", "content": hand_data}
        ]
    )
    return response.choices[0].message.content


def hand_handel(hand_data):
    print("Hand session started")
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(hand_session, hand_data)
        try:
            res = future.result(timeout=8)
        except concurrent.futures.TimeoutError:
            res = "无手部信息分析结果"
    result["hand"] = res
    print("Hand session finished in {} seconds".format(time.time() - start))


def finger_session(finger_data):
    response = client.chat.completions.create(
        model="glm-4-0520",
        messages=[
            {"role": "system", "content": finger_prompt},
            {"role": "user", "content": finger_data}
        ]
    )
    return response.choices[0].message.content


def finger_handel(finger_data):
    print("Finger session started")
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(finger_session, finger_data)
        try:
            res = future.result(timeout=8)
        except concurrent.futures.TimeoutError:
            res = "无手势信息分析结果"
    result["finger"] = res
    print("Finger session finished in {} seconds".format(time.time() - start))


def intention_session(intention_prompt):
    response = client.chat.completions.create(
        model="glm-4-0520",
        messages=[
            {"role": "user", "content": intention_prompt}
        ]
    )
    try:
        res = ast.literal_eval(extract_substring1(response.choices[0].message.content))
    except Exception as e:
        res = ast.literal_eval("""[{"intention": 交互意图1, "possibility": 交互意图1的可能性分数}, 
        {"intention": 分析超时, "possibility": 0}, 
        {"intention": 分析超时, "possibility": 0}, 
        {"intention": 分析超时, "possibility": 0}, 
        {"intention": 分析超时, "possibility": 0}, 
        {"intention": 分析超时, "possibility": 0}]
        """)
    return res


def intention_handel(event):
    event.wait()
    print("Intention session started")
    start = time.time()
    # intention_prompt = (intention_prompt_begin_1 +
    #                     "\n注视信息:\n" + result["gaze"] +
    #                     "\n手部信息:\n" + result["hand"] +
    #                     "\n手势信息:\n" + result["finger"] +
    #                     "\n物体状态信息:\n" + result["state"] +
    #                     "\n" + intention_prompt_end)
    intention_prompt = (intention_prompt_begin_2 +
                        "\n注视信息:\n" + result["gaze"] +
                        "\n语音信息:\n" + result["speech"] +
                        "\n物体状态信息:\n" + result["state"] +
                        "\n" + intention_prompt_end)
    print(intention_prompt)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(intention_session, intention_prompt)
        try:
            res = future.result(timeout=10)
        except concurrent.futures.TimeoutError:
            res = ast.literal_eval("""[{"intention": 交互意图1, "possibility": 交互意图1的可能性分数}, 
            {"intention": 分析超时, "possibility": 0}, 
            {"intention": 分析超时, "possibility": 0}, 
            {"intention": 分析超时, "possibility": 0}, 
            {"intention": 分析超时, "possibility": 0}, 
            {"intention": 分析超时, "possibility": 0}]
            """)
    result["intention"] = res
    print("Intention session finished in {} seconds".format(time.time() - start))


def intention_analysis(gaze_data, hand_data, finger_data, speech_data, target_data, task, sock, addr):
    event = threading.Event()

    gaze_thread = threading.Thread(target=gaze_handel, args=(gaze_data,))
    hand_thread = threading.Thread(target=hand_handel, args=(hand_data,))
    finger_thread = threading.Thread(target=finger_handel, args=(finger_data,))

    intention_thread = threading.Thread(target=intention_handel, args=(event,))

    gaze_thread.start()
    hand_thread.start()
    finger_thread.start()

    gaze_thread.join()
    hand_thread.join()
    finger_thread.join()

    state_info = ""
    for k in target_data.keys():
        if k in result["gaze"] and target_data[k]["state"] != "无特定状态":
            state_info += (k + ": " + target_data[k]["state"] + "\n")
    if state_info == "":
        state_info = "注视对象均无需要说明的特殊状态"
    result["state"] = state_info

    result["speech"] = speech_data

    event.set()

    intention_thread.start()
    intention_thread.join()

    print(result["intention"])

    # conn.sendall(str(result["intention"]).encode('utf-8'))
    sock.sendto(str(result["intention"]).encode('utf-8'), addr)

    result["intention"].append({"intention": task, "possibility": 100})

    operation_analysis(result["intention"], target_data)


def operation_session(operation_prompt):
    response = client.chat.completions.create(
        model="glm-4-0520",
        messages=[
            {"role": "user", "content": operation_prompt}
        ]
    )
    try:
        res = ast.literal_eval(extract_substring2(response.choices[0].message.content))
    except Exception as e:
        res = ast.literal_eval("{\"type\": 0}")

    return res


def operation_handel(option_id, operation_data):
    global operation_res

    print("Operation" + str(option_id) + " session started")
    # print(operation_data)
    start = time.time()
    operation_prompt = operation_prompt_begin + '\n' + str(operation_data) + '\n' + operation_prompt_end
    # print(operation_prompt)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(operation_session, operation_prompt)
        try:
            res = future.result(timeout=10)
        except concurrent.futures.TimeoutError:
            res = ast.literal_eval("{\"type\": 0}")

    temp = dict()
    temp["option_id"] = option_id
    temp["type"] = res["type"]
    temp["content"] = json.dumps(res, ensure_ascii=False)
    print(str(option_id) + " " + str(temp))

    operation_res[option_id] = temp

    # conn.sendall((str(temp) + "\n").encode('utf-8'))
    # sock.sendto(str(temp).encode('utf-8'), addr)
    print("Operation" + str(option_id) + " session finished in {} seconds".format(time.time() - start))


def operation_analysis(intention_data, target_data):
    global operation_res
    operation_res = dict()

    for i in range(7):
        operation_data = dict()
        operation_data["intention"] = intention_data[i]['intention']
        objects_info = list()
        for k in target_data.keys():
            if k in intention_data[i]['intention']:
                obj_info = dict()
                obj_info["name"] = k
                obj_info["movable"] = target_data[k]["movable"]
                obj_info["position"] = target_data[k]["position"]
                # obj_info["rotation"] = target_data[k]["rotation"]
                # obj_info["size"] = target_data[k]["size"]
                obj_info["api_list"] = target_data[k]["api_list"]
                objects_info.append(obj_info)
        operation_data["objects_info"] = objects_info
        operation_thread = threading.Thread(target=operation_handel, args=(i, operation_data,))
        operation_thread.start()


def send_operation(id, task_id, sock, addr):
    global operation_res
    start_time = time.time()
    while time.time() - start_time < 10:
        if id in operation_res.keys():
            operation_res[id]['task_id'] = task_id
            print("send: " + str(operation_res[id]))
            sock.sendto(str(operation_res[id]).encode('utf-8'), addr)
            return
        time.sleep(0.1)
    temp = dict()
    temp['option_id'] = id
    temp['type'] = 0
    temp['task_id'] = task_id
    temp['content'] = json.dumps(ast.literal_eval("{\"type\": 0}"), ensure_ascii=False)
    print("send: " + str(temp))
    sock.sendto(str(temp).encode('utf-8'), addr)
    return
