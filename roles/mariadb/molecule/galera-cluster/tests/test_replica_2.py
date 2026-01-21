from __future__ import annotations, unicode_literals

import os

import testinfra.utils.ansible_runner
from helper.molecule import get_vars, pp_json

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("replica_2")

# --- tests -----------------------------------------------------------------


def local_facts(host):
    """
    return local facts
    """
    local_fact = host.ansible("setup").get("ansible_facts").get("ansible_local")

    print(f"local_fact     : {local_fact}")

    if local_fact:
        return local_fact.get("mariadb", {})
    else:
        return dict()


def test_data_directory(host, get_vars):
    """
    configured datadir
    """
    directory = get_vars.get("mariadb_config_mysqld", {}).get(
        "datadir", "/var/lib/mysql"
    )
    user = "mysql"

    dir = host.file(directory)
    assert dir.is_directory
    assert dir.user == user
    assert dir.group == user


def test_tmp_directory(host, get_vars):
    """
    configured tmpdir
    """
    directory = get_vars.get("mariadb_config_mysqld", {}).get("tmpdir", "/tmp")

    dir = host.file(directory)
    assert dir.is_directory


def test_log_directory(host, get_vars):
    """
    configured logdir
    """
    error_log_file = get_vars.get("mariadb_config_mysqld", {}).get(
        "log_error", "/var/log/mysql/error.log"
    )
    user = "mysql"

    dir = host.file(os.path.dirname(error_log_file))
    assert dir.is_directory
    assert dir.user == user


def test_directories(host, get_vars):
    """
    used config directory

    debian based: /etc/mysql
    redhat based: /etc/my.cnf.d
    arch based  : /etc/my.cnf.d
    """
    pp_json(get_vars)

    directories = [
        get_vars.get("mariadb_config_dir"),
        get_vars.get("mariadb_config_include_dir"),
    ]

    for dirs in directories:
        d = host.file(dirs)
        assert d.is_directory


def test_files(host, get_vars):
    """
    created config files
    """
    files = [
        get_vars.get("mariadb_config_file"),
        "{}/mysql.cnf".format(get_vars.get("mariadb_config_include_dir")),
    ]

    for _file in files:
        f = host.file(_file)
        assert f.is_file


def test_user(host, get_vars):
    """
    created user
    """
    shell = "/bin/false"

    distribution = host.system_info.distribution

    if distribution in ["redhat", "ol", "centos", "rocky", "almalinux"]:
        shell = "/sbin/nologin"
    elif distribution in ["arch", "artix"]:
        shell = "/usr/bin/nologin"

    user_name = "mysql"
    u = host.user(user_name)
    g = host.group(user_name)

    assert g.exists
    assert u.exists
    assert user_name in u.groups
    assert u.shell == shell


def test_service_running_and_enabled(host, get_vars):
    """
    running service
    """
    service_name = get_vars.get("mariadb_service")

    service = host.service(service_name)
    assert service.is_running
    assert service.is_enabled


def test_listening_socket(host, get_vars):
    """ """
    listening = host.socket.get_listening_sockets()

    for i in listening:
        print(i)

    distribution = host.system_info.distribution
    release = host.system_info.release

    socket_name = get_vars.get("mariadb_socket", None)

    f = host.file(socket_name)
    assert f.exists

    listen = []
    # mariadb
    listen.append("tcp://10.29.0.22:3306")
    # wsrep
    listen.append("tcp://0.0.0.0:4567")

    if socket_name and not (distribution == "ubuntu" and release == "18.04"):
        listen.append(f"unix://{socket_name}")

    for spec in listen:
        socket = host.socket(spec)
        assert socket.is_listening
