from __future__ import annotations, unicode_literals

import os

import testinfra.utils.ansible_runner
from helper.molecule import get_vars

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("database")

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


def test_data_directory(host, get_vars):
    """
    configured datadir
    """
    directory = get_vars.get("postgresql_data_dir", "/var/lib/postgres/data")

    user = "postgres"

    dir = host.file(directory)
    assert dir.is_directory
    assert dir.user == user
    assert dir.group == user


def test_config_directory(host, get_vars):
    """ """
    directory = get_vars.get("postgresql_config_path", "/var/lib/postgres/data")

    dir = host.file(directory)
    assert dir.is_directory

    dir = host.file(f"{directory}/postgresql.conf.d")
    assert dir.is_directory


def test_config_files(host, get_vars):
    """
    created config files
    """
    directory = get_vars.get("postgresql_config_path", "/var/lib/postgres/data")

    files = [
        f"{directory}/pg_hba.conf",
        f"{directory}/postgresql.conf.d/pg_autovacuum.conf",
        f"{directory}/postgresql.conf.d/pg_client_connections.conf",
        f"{directory}/postgresql.conf.d/pg_compatibility.conf",
        f"{directory}/postgresql.conf.d/pg_connections.conf",
        f"{directory}/postgresql.conf.d/pg_error_handling.conf",
        f"{directory}/postgresql.conf.d/pg_file_locations.conf",
        f"{directory}/postgresql.conf.d/pg_lock_management.conf",
        f"{directory}/postgresql.conf.d/pg_query_tuning.conf",
        f"{directory}/postgresql.conf.d/pg_replication.conf",
        f"{directory}/postgresql.conf.d/pg_reporting.conf",
        f"{directory}/postgresql.conf.d/pg_ressources.conf",
        f"{directory}/postgresql.conf.d/pg_statistics.conf",
        f"{directory}/postgresql.conf.d/pg_write_ahead.conf",
    ]

    for _file in files:
        f = host.file(_file)
        assert f.is_file


def test_service_running_and_enabled(host, get_vars):
    """
    running service
    """
    daemon = get_vars.get("postgresql_daemon", "postgresql")

    service = host.service(daemon)
    assert service.is_running
    assert service.is_enabled


def test_listening_socket(host, get_vars):
    """ """
    listening = host.socket.get_listening_sockets()

    for i in listening:
        print(i)

    distribution = host.system_info.distribution
    release = host.system_info.release

    bind_address = "127.0.0.1"
    bind_port = 5432
    socket_name = "/run/postgresql/.s.PGSQL.5432"

    f = host.file(socket_name)
    assert f.exists

    listen = []
    listen.append(f"tcp://{bind_address}:{bind_port}")

    for spec in listen:
        socket = host.socket(spec)
        assert socket.is_listening
