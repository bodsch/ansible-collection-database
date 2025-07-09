
from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar

import json
import pytest
import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def pp_json(json_thing, sort=True, indents=2):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


def base_directory():
    cwd = os.getcwd()

    if ('group_vars' in os.listdir(cwd)):
        directory = "../.."
        molecule_directory = "."
    else:
        directory = "."
        molecule_directory = f"molecule/{os.environ.get('MOLECULE_SCENARIO_NAME')}"

    return directory, molecule_directory


@pytest.fixture()
def get_vars(host):
    """

    """
    base_dir, molecule_dir = base_directory()
    distribution = host.system_info.distribution
    operation_system = None

    if distribution in ['debian', 'ubuntu']:
        operation_system = "debian"
    elif distribution in ['redhat', 'ol', 'centos', 'rocky', 'almalinux']:
        operation_system = "redhat"
    elif distribution in ['arch', 'artix']:
        operation_system = "archlinux"

    file_defaults = f"file={base_dir}/defaults/main.yml name=role_defaults"
    file_vars = f"file={base_dir}/vars/main.yml name=role_vars"
    file_molecule = f"file={molecule_dir}/group_vars/all/vars.yml name=test_vars"
    file_distibution = f"file={base_dir}/vars/{operation_system}.yml name=role_distibution"

    defaults_vars = host.ansible("include_vars", file_defaults).get("ansible_facts").get("role_defaults")
    vars_vars = host.ansible("include_vars", file_vars).get("ansible_facts").get("role_vars")
    distibution_vars = host.ansible("include_vars", file_distibution).get("ansible_facts").get("role_distibution")
    molecule_vars = host.ansible("include_vars", file_molecule).get("ansible_facts").get("test_vars")

    ansible_vars = defaults_vars
    ansible_vars.update(vars_vars)
    ansible_vars.update(distibution_vars)
    ansible_vars.update(molecule_vars)

    templar = Templar(loader=DataLoader(), variables=ansible_vars)
    result = templar.template(ansible_vars, fail_on_undefined=False)

    return result


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


def test_tmp_directory(host, get_vars):
    """
      configured tmpdir
    """
    directory = get_vars.get("postgresql_data_dir", "/var/lib/postgres/data")

    dir = host.file(directory)
    assert dir.is_directory


def test_files(host, get_vars):
    """
      created config files
    """
    directory = get_vars.get("postgresql_data_dir", "/var/lib/postgres/data")

    files = [
        f"{directory}/pg_hba.conf"
    ]

    for _file in files:
        f = host.file(_file)
        assert f.is_file


def test_user(host, get_vars):
    """
      created user
    """
    shell = '/bin/false'

    distribution = host.system_info.distribution

    if distribution in ['redhat', 'ol', 'centos', 'rocky', 'almalinux']:
        shell = "/sbin/nologin"
    elif distribution in ['arch', 'artix']:
        shell = "/usr/bin/bash"

    user_name = "postgres"
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
    service_name = "postgresql"

    service = host.service(service_name)
    assert service.is_running
    assert service.is_enabled


def test_listening_socket(host, get_vars):
    """
    """
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
