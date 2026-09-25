from pathlib import Path
import pickle
import os
import subprocess
import time
import uuid
import socket

from mini_internet import config
from mini_internet.packet import Packet


def main() -> None:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    routers: list[subprocess.Popen[bytes]] = []

    try:
        for router_id in config.routers:
            log_path = log_dir / f"{router_id}.log"
            with log_path.open("a", encoding="utf-8") as log_file:
                routers.append(
                    subprocess.Popen(
                        ["uv", "run", "router", "--id", router_id],
                        stdout=log_file,
                        stderr=subprocess.STDOUT,
                        env={**os.environ, "PYTHONUNBUFFERED": "1"},
                        text=True,
                    )
                )

        # Give the router sockets a moment to bind before sending the sample packet.
        time.sleep(0.5)
        packet = Packet(
            source_addr="h1",
            destination_addr="h2",
            hops=8,
            message_type="string",
            message_id=str(uuid.uuid4()),
            payload=b"fake request from h1 to h2",
        )
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(
                pickle.dumps(packet), ("127.0.0.1", config.routers["r1"]["port"])
            )

        # Let the packet reach the destination router so its log entry is written.
        time.sleep(0.5)
    finally:
        for router in routers:
            if router.poll() is None:
                router.terminate()
        for router in routers:
            try:
                router.wait(timeout=2)
            except subprocess.TimeoutExpired:
                router.kill()
                router.wait()
