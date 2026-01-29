from __future__ import annotations, unicode_literals

import os

import testinfra.utils.ansible_runner
from helper.molecule import get_vars, infra_hosts, local_facts

testinfra_hosts = infra_hosts(host_name="database")

# --- tests -----------------------------------------------------------------


def test_postgres_user(host, get_vars):
    """ """
    shell = "/bin/bash"

    distribution = host.system_info.distribution

    if distribution in ["arch", "artix"]:
        shell = "/usr/bin/bash"

    user_name = "postgres"
    u = host.user(user_name)
    g = host.group(user_name)

    assert g.exists
    assert u.exists
    assert user_name in u.groups
    assert u.shell == shell


def test_listening_socket(host, get_vars):
    """ """
    listening = host.socket.get_listening_sockets()

    _postgres_facts = local_facts(host=host, fact="postgresql")

    for i in listening:
        print(i)

    distribution = host.system_info.distribution
    release = host.system_info.release

    bind_address = "127.0.0.1"
    bind_port = 5432
    socket_name = f"/run/postgresql/.s.PGSQL.{bind_port}"
    pid_name = f"/run/postgresql/{_postgres_facts.get('platform_version')}-main.pid"

    print(f"socket: {socket_name}")
    print(f"pid   : {pid_name}")

    f = host.file(socket_name)
    assert f.exists

    f = host.file(pid_name)
    assert f.exists

    listen = []
    listen.append(f"tcp://{bind_address}:{bind_port}")

    for spec in listen:
        socket = host.socket(spec)
        assert socket.is_listening
