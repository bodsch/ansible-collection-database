from __future__ import annotations, unicode_literals

import os

import testinfra.utils.ansible_runner
from helper.molecule import get_vars, infra_hosts, local_facts

testinfra_hosts = infra_hosts(host_name="instance")

# --- tests -----------------------------------------------------------------


def test_directories(host):
    """ """
    directories = ["/etc/mariadb_backup"]

    for dirs in directories:
        d = host.file(dirs)
        assert d.is_directory


def test_files(host):
    """ """
    files = [
        "/etc/mariadb_backup/mariadb_backup.yml",
        "/usr/local/bin/mariadb_backup.py",
    ]

    for _file in files:
        f = host.file(_file)
        assert f.is_file
