import json
import os
import re
from typing import Any

import pytest
import testinfra.utils.ansible_runner
from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def pp_json(json_thing, sort=True, indents=2):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


def base_directory():
    cwd = os.getcwd()

    if "group_vars" in os.listdir(cwd):
        directory = "../.."
        molecule_directory = "."
    else:
        directory = "."
        molecule_directory = f"molecule/{os.environ.get('MOLECULE_SCENARIO_NAME')}"

    return directory, molecule_directory


def read_ansible_yaml(file_name, role_name):
    """ """
    read_file = None

    for e in ["yml", "yaml"]:
        test_file = f"{file_name}.{e}"
        if os.path.isfile(test_file):
            read_file = test_file
            break

    return f"file={read_file} name={role_name}"


@pytest.fixture()
def get_vars(host):
    """
    parse ansible variables
    - defaults/main.yml
    - vars/main.yml
    - vars/${DISTRIBUTION}.yaml
    - molecule/${MOLECULE_SCENARIO_NAME}/group_vars/all/vars.yml
    """
    base_dir, molecule_dir = base_directory()
    distribution = host.system_info.distribution
    operation_system = None

    if distribution in ["debian", "ubuntu"]:
        operation_system = "debian"
    elif distribution in ["redhat", "ol", "centos", "rocky", "almalinux"]:
        operation_system = "redhat"
    elif distribution in ["arch", "artix"]:
        operation_system = f"{distribution}linux"

    # print(" -> {} / {}".format(distribution, os))
    # print(" -> {}".format(base_dir))

    file_defaults = read_ansible_yaml(f"{base_dir}/defaults/main", "role_defaults")
    file_vars = read_ansible_yaml(f"{base_dir}/vars/main", "role_vars")
    file_distibution = read_ansible_yaml(
        f"{base_dir}/vars/{operation_system}", "role_distibution"
    )
    file_molecule = read_ansible_yaml(
        f"{molecule_dir}/group_vars/all/vars", "test_vars"
    )
    # file_host_molecule = read_ansible_yaml("{}/host_vars/{}/vars".format(base_dir, HOST), "host_vars")

    defaults_vars = (
        host.ansible("include_vars", file_defaults)
        .get("ansible_facts")
        .get("role_defaults")
    )
    vars_vars = (
        host.ansible("include_vars", file_vars).get("ansible_facts").get("role_vars")
    )
    distibution_vars = (
        host.ansible("include_vars", file_distibution)
        .get("ansible_facts")
        .get("role_distibution")
    )
    molecule_vars = (
        host.ansible("include_vars", file_molecule)
        .get("ansible_facts")
        .get("test_vars")
    )
    # host_vars          = host.ansible("include_vars", file_host_molecule).get("ansible_facts").get("host_vars")

    ansible_vars = defaults_vars
    ansible_vars.update(vars_vars)
    ansible_vars.update(distibution_vars)
    ansible_vars.update(molecule_vars)
    # ansible_vars.update(host_vars)

    templar = Templar(loader=DataLoader(), variables=ansible_vars)
    result = templar.template(ansible_vars, fail_on_undefined=False)

    version = local_facts(host).get("version")

    # replace global all 'postgresql_version' strings
    result = replace_version(result, version)

    return result


def replace_version(obj: Any, version: str) -> Any:

    re_match = re.compile(r"\{\{\s*postgresql_version\s*\}\}")

    if isinstance(obj, str):
        return re_match.sub(version, obj)
    if isinstance(obj, list):
        return [replace_version(x, version) for x in obj]
    if isinstance(obj, tuple):
        return tuple(replace_version(x, version) for x in obj)
    if isinstance(obj, dict):
        return {k: replace_version(v, version) for k, v in obj.items()}
    return obj


def local_facts(host):
    """
    return local facts
    """
    ansible_facts = host.ansible("setup").get("ansible_facts", {})
    return ansible_facts.get("ansible_local").get("postgresql")


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
