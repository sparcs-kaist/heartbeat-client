# Heartbeat Client for SPARCS Services
# VERSION 0.5.1: 2016-10-08-001


from datetime import datetime
import json
import psutil
import pprint
import os
import time
import requests


try:
    from settings import *
except:
    NETWORK_REPORT = False
    SERVER_NAME = 'TEST'
    SERVER_KEY = 'secret_key'
    API_ENDPOINT = 'https://example.com/'


# get cpu info
# - user, system, idle (1 sec)
def get_cpu():
    cpu = psutil.cpu_times_percent(interval=1, percpu=False)

    info = {
        'user': cpu.user,
        'system': cpu.system,
        'idle': cpu.idle,
    }

    return info


# get memory info
# - virtual (total, available, used)
# - swap (total, used)
def get_mem():
    virt_mem = psutil.virtual_memory()
    swap_mem = psutil.swap_memory()

    info = {
        'virtual': {
            'total': virt_mem.total,
            'available': virt_mem.available,
            'used': virt_mem.used,
        },
        'swap': {
            'total': swap_mem.total,
            'used': swap_mem.used,
        },
    }

    return info


# get disk info
# - devide (mountpoint, fstype, total, used)
def get_disk():
    info = {}

    disk_list = psutil.disk_partitions()
    for disk in disk_list:
        usage = psutil.disk_usage(disk.mountpoint)
        info[disk.device] = {
            'mountpoint': disk.mountpoint,
            'fstype': disk.fstype,
            'total': usage.total,
            'used': usage.used,
        }

    return info


# get network info
# - bytes (sent, recv) (1 sec)
# - packet (sent, recv) (1 sec)
def get_net():
    info = {
        'bytes_sent': 0,
        'bytes_recv': 0,
        'packets_sent': 0,
        'packets_recv': 0,
    }

    c1 = psutil.net_io_counters()
    time.sleep(1)
    c2 = psutil.net_io_counters()

    info['bytes_sent'] = c2.bytes_sent - c1.bytes_sent
    info['bytes_recv'] = c2.bytes_recv - c1.bytes_recv
    info['packets_sent'] = c2.packets_sent - c1.packets_sent
    info['packets_recv'] = c2.packets_recv - c1.packets_recv

    return info


# get process info
# - name (top 5 cpu usages)
# - name (top 5 mem usages)
def get_proc():
    self_pid = psutil.Process().pid

    proc_list = []
    for p in psutil.process_iter():
        try:
            if p.pid == self_pid:
                continue

            proc_list.append({
                'name': p.name(),
                'cpu': p.cpu_percent(interval=0.1),
                'mem': p.memory_percent(),
            })
        except:
            pass

    def top_n(n, l, key):
        return list(reversed(sorted(l, key=key)))[:n]

    info = {
        'top_cpu': top_n(5, proc_list, lambda x: x['cpu']),
        'top_mem': top_n(5, proc_list, lambda x: x['mem']),
    }

    return info


# get system info
# - boot time
def get_sys():
    info = {
        'boot_time': psutil.boot_time()
    }

    return info


# report info to server
def report(info):
    payload = {
        'server': {
            'name': SERVER_NAME,
            'key': SERVER_KEY,
        },
        'info': info,
        'errors': {},
    }

    for i in range(3):
        timestamp = int(time.time())
        try:
            req = requests.post(API_ENDPOINT, json=payload)
            if req.status_code == 200:
                resp = req.json()
                if 'success' in resp:
                    return resp['success'], payload['errors']
                error = resp['error'] if 'error' in resp else 'unknown'
            else:
                error = 'Server returned %d instead of 200' % req.status_code
            payload['errors'][timestamp] = error

        except Exception as e:
            payload['errors'][timestamp] = str(e)

        time.sleep(5)
    return False, payload['errors']


# our main routine
def main():
    BASE = os.path.abspath(os.path.dirname(__file__))
    LOCK = os.path.join(BASE, 'lock')
    if os.path.exists(LOCK):
        exit(1)

    with open(LOCK, 'w') as f:
        f.write(str(psutil.Process().pid))

    info = {
        'cpu': get_cpu(),
        'mem': get_mem(),
        'disk': get_disk(),
        'net': get_net(),
        'proc': get_proc(),
        'sys': get_sys(),
    }

    if not NETWORK_REPORT:
        pprint.pprint(info)
        return

    success, errors = report(info)
    if not success:
        print('=ERROR ON HEARTBEAT CLIENT %s=' % SERVER_NAME)
        for k, v in errors.items():
            print('Time: %s, Reason: %s' %
                  (datetime.fromtimestamp(k).isoformat(), v))
    os.remove(LOCK)


if __name__ == '__main__':
    main()
