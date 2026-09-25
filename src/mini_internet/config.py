hosts = {"h1": {"port": 35100, "router": "r1"}, "h2": {"port": 35101, "router": "r2"}}
routers = {
    "r1": {"port": 35102, "dest_to_hop": {"h2": "r2", "h1": "h1"}},
    "r2": {"port": 35103, "dest_to_hop": {"h2": "h2", "h1": "r1"}},
}
