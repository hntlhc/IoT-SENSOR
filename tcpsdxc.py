import socket
import csv
from datetime import datetime, date
from threading import Thread

def save_to_csv(data, filename):
    # 打开CSV文件（如果不存在则创建新文件）
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)

        # 写入数据行
        for row in data:
            writer.writerow(row)

    print("数据已保存到", filename)

def parse_data(data):
    # 解析数据，数据格式为：设备编号,电池电压,温度值,湿度值,设备IP地址
    parts = data.split(',')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 返回数据行，包括时间戳、设备编号、温度值、湿度值和设备IP地址
    return [timestamp] + parts

def generate_filename(data_number):
    today = date.today().strftime("%Y-%m-%d")
    return f"{data_number}_{today}.csv"

def handle_client(client_socket, client_address):
    print("客户端已连接：", client_address)

    received_data = []  # 存储接收到的数据

    try:
        while True:
            # 接收数据
            data = client_socket.recv(1024)
            if not data:
                break

            # 解码收到的数据并存储
            decoded_data = data.decode()
            parsed_data = parse_data(decoded_data)
            received_data.append(parsed_data)
            print("收到数据：", parsed_data)

        # 生成文件名
            data_number = parsed_data[1]  # 设备编号作为文件名的一部分
            filename = generate_filename(data_number)

        # 保存数据到CSV文件
            save_to_csv(received_data, filename)

        # 发送响应消息给客户端
            client_socket.send(b"tcp ok")

    except Exception as e:
        print("发生异常：", str(e))

    finally:
        # 关闭与客户端的连接
        client_socket.close()
        print("客户端连接已关闭。")

def start_server(host, port):
    # 创建TCP套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 绑定服务器地址和端口
    server_socket.bind((host, port))

    # 监听连接
    server_socket.listen(5)
    print("服务器启动，等待客户端连接...")

    while True:
        # 等待客户端连接
        client_socket, client_address = server_socket.accept()

        # 使用新线程处理客户端连接
        client_thread = Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    host = '192.168.148.100'  # 服务器IP地址
    port = 10089  # 服务器端口
    start_server(host, port)
