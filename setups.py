usb_hub_prefix = "1:9"

ftdi_mapping = {
    'A': ','.join([usb_hub_prefix, '1,1']),
    'B': ','.join([usb_hub_prefix, '1,2']),
    'C': ','.join([usb_hub_prefix, '1,3']),
    'D': ','.join([usb_hub_prefix, '1,4']),
    'E': ','.join([usb_hub_prefix, '2']),
    'F': ','.join([usb_hub_prefix, '3']),
    'X': None
}

ip_mapping = {
    'A': '192.168.95.213',
    'B': '192.168.95.214',
    'C': '192.168.95.215',
    'D': '192.168.95.216',
    'E': '192.168.95.217',
    'F': '192.168.95.218',
    'X': '192.168.1.70'
}

scope_ip_mapping = {
    'A': '192.168.95.166',
    'B': '192.168.95.181',
    'C': '192.168.95.158',
    'D': '192.168.95.141',
    'E': '192.168.95.142',
    'F': '192.168.95.157',
    'X': None
}

scope_controller_ports = {
    'A': 4000,
    'B': 4001,
    'C': 4002,
    'D': 4003,
    'E': 4004,
    'F': 4005,
    'X': None
}

corelog_controller_ports = {
    'A': 2000,
    'B': 2001,
    'C': 2002,
    'D': 2003,
    'E': 2004,
    'F': 2005,
    'X': 1068   # default
}

moninj_controller_ports = {
    'A': 1483,
    'B': 1484,
    'C': 1485,
    'D': 1486,
    'E': 1487,
    'F': 1488,
    'X': 1384   # default
}

moninj_proxy_ports = {
    'A': 1583,
    'B': 1584,
    'C': 1585,
    'D': 1586,
    'E': 1587,
    'F': 1588,
    'X': 1383   # default
}

coreanalyzer_controller_ports = {
    'A': 1683,
    'B': 1684,
    'C': 1685,
    'D': 1686,
    'E': 1687,
    'F': 1688,
    'X': 1384   # default
}

coreanalyzer_proxy_ports = {
    'A': 1783,
    'B': 1784,
    'C': 1785,
    'D': 1786,
    'E': 1787,
    'F': 1788,
    'X': 1383   # default
}

master_notify_ports = {
    'A': 3250,
    'B': 3251,
    'C': 3252,
    'D': 3253,
    'E': 3254,
    'F': 3255,
    'X': 3250   # default
}

master_control_ports = {
    'A': 3261,
    'B': 3262,
    'C': 3263,
    'D': 3264,
    'E': 3265,
    'F': 3266,
    'X': 3251   # default
}

master_logging_ports = {
    'A': 1060,
    'B': 1061,
    'C': 1062,
    'D': 1063,
    'E': 1064,
    'F': 1065,
    'X': 1066   # default
}

master_broadcast_ports = {
    'A': 1160,
    'B': 1161,
    'C': 1162,
    'D': 1163,
    'E': 1164,
    'F': 1165,
    'X': 1067   # default
}

ctlmgr_control_ports = {
    'A': 3271,
    'B': 3272,
    'C': 3273,
    'D': 3274,
    'E': 3275,
    'F': 3276,
    'X': 3249   # default
}
