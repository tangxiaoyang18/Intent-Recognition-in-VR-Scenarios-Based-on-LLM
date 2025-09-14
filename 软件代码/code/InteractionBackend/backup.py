import socket
import json
import threading

from InteractionData import InteractionData
from LLM import intention_analysis, send_operation


def start_tcp_server(host='10.192.192.223', port=8080):  # 10.192.58.90
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.bind((host, port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(1)
    print(f"Listening on {host}:{port}")

    data_store = InteractionData()

    data_flag = True

    while True:
        print("Waiting for a connection...")
        conn, addr = sock.accept()
        print(f"Connected by {addr}")

        with conn:
            buffer = ""
            while True:
                try:
                    data = conn.recv(1024).decode('utf-8')
                except:
                    continue
                if not data:
                    break
                buffer += data

                if '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                else:
                    continue

                json_data = message
                print(json_data)
                # Parse JSON
                try:
                    # print(json_data.strip().replace("'", "\""))
                    data_package = json.loads(json_data.strip().replace("'", "\""))
                    # print(data_package)
                    if data_package['type'] == 0 and data_flag:
                        print("Finish receive data")
                        data_flag = False
                        intention_analysis(data_store.get_gaze_data(),
                                           data_store.get_hand_data(),
                                           data_store.get_finger_data(),
                                           data_store.get_target_info(),
                                           data_store.task, conn)
                        data_store.clear_data()
                        # buffer = ""
                    elif data_package['type'] == 1:
                        data_store.add_data(data_package)
                        data_flag = True
                    elif data_package['type'] == 2:
                        threading.Thread(target=send_operation, args=(data_package['option_id'], conn,)).start()

                except Exception as e:
                    print(f"Error parsing data: {e}")

    # while True:
    #     data, addr = sock.recvfrom(65507)  # Buffer size
    #     json_data = data.decode('utf-8')
    #
    #     # Parse JSON
    #     try:
    #         # print(json_data.strip().replace("'", "\""))
    #         data_package = json.loads(json_data.strip().replace("'", "\""))
    #         # print(data_package)
    #         if data_package['type'] == 0:
    #             intention_analysis(data_store.get_gaze_data(),
    #                                data_store.get_hand_data(),
    #                                data_store.get_finger_data(),
    #                                data_store.get_target_info(),
    #                                data_store.task, sock, addr)
    #             data_store.clear_data()
    #         elif data_package['type'] == 1:
    #             data_store.add_data(data_package)
    #         # elif data_package['type'] == 2:
    #         #     result = operation_analysis(data_package)
    #         #     sock.sendto(str(result).encode('utf-8'), addr)
    #
    #     except Exception as e:
    #         print(f"Error parsing data: {e}")


