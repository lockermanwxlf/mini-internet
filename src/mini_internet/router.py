import argparse
from dataclasses import dataclass
import pickle
import socket
from mini_internet import config
from mini_internet.packet import Packet

DEFAULT_PACKET_LOSS = 0.1


@dataclass
class Arguments:
    id: str
    packet_loss: float


@dataclass
class RouterConfig:
    port: int
    dest_to_hop: dict[str, str]


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--id", type=str, required=True)
    parser.add_argument("--packet-loss", default=DEFAULT_PACKET_LOSS)

    args = parser.parse_args()
    return Arguments(args.id, args.packet_loss)


def main():
    args = parse_args()
    if args.id not in config.routers:
        print("Router not defined in config")
        exit(1)
    router_config = RouterConfig(**config.routers[args.id])

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("0.0.0.0", router_config.port))
        ip_address, assigned_port = sock.getsockname()
        print(ip_address, assigned_port)

        while True:
            data, addr = sock.recvfrom(1024)
            print("Datagram received from", addr)

            packet: Packet = pickle.loads(data)
            if packet.hops == 1:
                print("TTL reached")
                continue

            hop_id = router_config.dest_to_hop[packet.destination_addr]
            hop = config.routers.get(hop_id, config.hosts.get(hop_id))
            if not hop:
                print("No hop for destination")
                continue

            packet.hops -= 1
            print("Forwarding message to", hop_id, hop["port"])
            sock.sendto(pickle.dumps(packet), ("127.0.0.1", hop["port"]))


if __name__ == "__main__":
    main()
