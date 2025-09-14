import socket
import json
import threading

from InteractionData import InteractionData
from LLM import intention_analysis, send_operation


def start_udp_server(host='10.132.25.157', port=8080):  # 10.192.58.90  10.132.25.157
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"Listening on {host}:{port}")

    data_store = InteractionData()

    data_flag = True

    task_id = 8

    while True:
        data, addr = sock.recvfrom(65507)  # Buffer size
        json_data = data.decode('utf-8')

        # Parse JSON
        try:
            # print(json_data.strip().replace("'", "\""))
            data_package = json.loads(json_data.strip().replace("'", "\""))
            print(data_package)
            if data_package['type'] == 0 and data_flag:
                data_flag = False
                data_store.speech_data = data_package['speech_result']
                intention_analysis(data_store.get_gaze_data(),
                                   data_store.get_hand_data(),
                                   data_store.get_finger_data(),
                                   data_store.get_speech_data(),
                                   data_store.get_target_info(),
                                   data_store.task, sock, addr)
                data_store.save_data(task_id)
                # task_id += 1
                data_store.clear_data()
            elif data_package['type'] == 1:
                data_flag = True
                data_store.add_data(data_package)
            elif data_package['type'] == 2:
                print("User want: " + str(data_package['option_id']))
                send_operation(data_package['option_id'], data_package['task_id'], sock, addr)
                # threading.Thread(target=send_operation, args=(data_package['option_id'], sock, addr)).start()

        except Exception as e:
            print(f"Error parsing data: {e}")


if __name__ == "__main__":
    start_udp_server()
