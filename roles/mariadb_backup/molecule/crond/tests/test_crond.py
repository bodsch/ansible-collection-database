from __future__ import annotations, unicode_literals

import os

from helper.molecule import get_vars, local_facts, pp_json

# --- tests -----------------------------------------------------------------


@pytest.mark.parametrize("files", ["/etc/cron.d/mariadb_backup"])
def test_files(host, files):
    f = host.file(files)
    assert f.is_file
