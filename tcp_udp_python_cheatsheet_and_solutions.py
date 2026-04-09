# =========================================
# PYTHON TCP/UDP + STRUCT CHEATSHEET
# =========================================

# ----------- IMPORTOK -----------
import socket      # hálózati kommunikáció
import struct      # bináris adatkezelés
import random      # véletlen szám
import json        # JSON fájl
import select      # több kliens kezelése (server)


# =========================================
# STRUCT ALAPOK
# =========================================

# Pack (küldés előtt)
# 20s = 20 byte string, i = integer
# FONTOS: string -> encode!
packed = struct.pack("20s i", b"almafa", 4)

# Unpack (fogadás után)
data = packed
text, number = struct.unpack("20s i", data)
text = text.decode().strip('\x00')  # null byte eltávolítás


# =========================================
# TCP KLIENS (ALAP)
# =========================================

def tcp_client_example():
    HOST = "127.0.0.1"
    PORT = 12345

    text = input("Szöveg: ")
    number = random.randint(1, len(text))

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    packed = struct.pack("20s i", text.encode(), number)
    client.send(packed)

    data = client.recv(1024)

    result = struct.unpack(f"{number}s", data)[0].decode()
    print("Válasz:", result)

    client.close()


# =========================================
# TCP SZERVER (SELECT - több kliens)
# =========================================

def tcp_server_select():
    HOST = "0.0.0.0"
    PORT = 12345

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    inputs = [server]

    while True:
        readable, _, _ = select.select(inputs, [], [])

        for s in readable:
            if s == server:
                client_socket, addr = server.accept()
                print("Kapcsolódott:", addr)
                inputs.append(client_socket)
            else:
                data = s.recv(1024)

                if not data:
                    inputs.remove(s)
                    s.close()
                    continue

                text, number = struct.unpack("20s i", data)
                text = text.decode().strip('\x00')

                # FELADAT LOGIKA
                result = text[:number][::-1]

                s.send(struct.pack(f"{len(result)}s", result.encode()))


# =========================================
# TXT BEOLVASÁS
# =========================================

def load_from_txt():
    with open("input.txt") as f:
        lines = f.readlines()

    index = random.randint(0, 2)
    text, number = lines[index].strip().split()

    return text, int(number)


# =========================================
# JSON BEOLVASÁS
# =========================================

def load_from_json():
    with open("input.json") as f:
        data = json.load(f)

    key = str(random.randint(1, 3))
    return data[key]


# =========================================
# UDP KLIENS
# =========================================

def udp_client_example():
    HOST = "127.0.0.1"
    PORT = 12345

    text = "almafa"
    number = 4

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    packed = struct.pack("20s i", text.encode(), number)
    client.sendto(packed, (HOST, PORT))

    data, _ = client.recvfrom(1024)
    result = struct.unpack(f"{number}s", data)[0].decode()

    print(result)


# =========================================
# PARANCSOS TCP SZERVER (IN / INCR / DECR)
# =========================================

def command_server():
    HOST = "0.0.0.0"
    PORT = 12346

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    value = 0

    while True:
        client, addr = server.accept()
        data = client.recv(1024)

        cmd, num = struct.unpack("4s i", data)
        cmd = cmd.decode().strip()

        if cmd == "IN":
            value = num
        elif cmd == "INCR":
            value += num
        elif cmd == "DECR":
            value -= num

        client.send(str(value).encode())
        client.close()


# =========================================
# UDP SZERVER (PUSH / PLUS / MINUS)
# =========================================

def udp_server():
    HOST = "0.0.0.0"
    PORT = 12347

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))

    value = 0

    while True:
        data, addr = server.recvfrom(1024)

        cmd, num = struct.unpack("5s i", data)
        cmd = cmd.decode().strip()

        if cmd == "PUSH":
            value = num
        elif cmd == "PLUS":
            value += num
        elif cmd == "MINUS":
            value -= num

        # válasz struct formátumban!
        server.sendto(struct.pack("i", value), addr)


# =========================================
# PROXY TCP SZERVER (UDP felé továbbít)
# =========================================

def proxy_server():
    TCP_PORT = 12348
    UDP_PORT = 12347

    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(("0.0.0.0", TCP_PORT))
    tcp.listen()

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        client, _ = tcp.accept()
        data = client.recv(1024)

        # továbbítás UDP-nek
        udp.sendto(data, ("127.0.0.1", UDP_PORT))

        response, _ = udp.recvfrom(1024)

        client.send(response)
        client.close()


# =========================================
# FUTTATÁS
# =========================================

# Terminál:
# python file.py

# FONTOS:
# - először szerver!
# - aztán kliens!

# =========================================
# TIPIKUS HIBÁK
# =========================================

# - encode() hiányzik
# - decode() hiányzik
# - struct méret nem egyezik
# - port már foglalt
# - TCP vs UDP keverés


# =========================================
# VÉGE
# =========================================
