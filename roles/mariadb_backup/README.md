
# Ansible Role:  `mariadb_backup`

Installs and confige mariadb_backup script.


[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bodsch/ansible-mariadb_backup/main.yml?branch=main)][ci]
[![GitHub issues](https://img.shields.io/github/issues/bodsch/ansible-mariadb_backup)][issues]
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/bodsch/ansible-mariadb_backup)][releases]
[![Ansible Downloads](https://img.shields.io/ansible/role/d/bodsch/mariadb_backup?logo=ansible)][galaxy]


[ci]: https://github.com/bodsch/ansible-mariadb_backup/actions
[issues]: https://github.com/bodsch/ansible-mariadb_backup/issues?q=is%3Aopen+is%3Aissue
[releases]: https://github.com/bodsch/ansible-mariadb_backup/releases
[galaxy]: https://galaxy.ansible.com/ui/standalone/roles/bodsch/mariadb_backup/


## Requirements & Dependencies

Ansible Collections

- [bodsch.core](https://github.com/bodsch/ansible-collection-core)

```bash
ansible-galaxy collection install bodsch.core
```
or
```bash
ansible-galaxy collection install --requirements-file collections.yml
```

## Operating systems

Tested on

* Arch Linux
* Debian based
    - Debian 10 / 11 / 12
    - Ubuntu 20.10 / 22.04

> **RedHat-based systems are no longer officially supported! May work, but does not have to.**


## Contribution

Please read [Contribution](CONTRIBUTING.md)

## Development,  Branches (Git Tags)

The `master` Branch is my *Working Horse* includes the "latest, hot shit" and can be complete broken!

If you want to use something stable, please use a [Tagged Version](https://github.com/bodsch/ansible-mariadb_backup/tags)!


## usage

```yaml
mariadb_backup_version: 3.1.1

mariadb_backup_client_package:

mariadb_backup_pre_script:
  file: ''
  content: ''

mariadb_backup_post_script:
  file: ''
  content: ''

mariadb_backup_backup_directory: /srv/backup/mysql

mariadb_backup_source: archive

mariadb_backup_archive: "https://github.com/bodsch/AutoMySQLBackup/archive/refs/tags/{{ mariadb_backup_version }}.zip"
mariadb_backup_git:
  repository: 'https://github.com/bodsch/AutoMySQLBackup'
  version: master

mariadb_backup_dump:
  debug: false
  dry_run: false
  create_database: true
  full_schema: true
  dbstatus: true
  use_separate_dirs: true
  host_friendly: true
  compression: bzip2
  latest: true
  latest_clean_filenames: true

mariadb_backup_connection:
  encrypted_login: false
  username: ''
  password: ''
  host: ''
  port: ''
  socket: /run/mysqld/mysqld.sock
  commpress_communication: true
  login_cnf_file: ''
  use_ssl: false
  max_allowed_packet: ''
  single_transaction: true

# notifications
mariadb_backup_notification:
  enabled: false
  # - log   : send only log file
  # - files : send log file and sql files as attachments (see docs)
  # - stdout : will simply output the log to the screen if run manually.
  # - quiet : Only send logs if an error occurs to the MAILADDR.
  mail_content: 'stdout'
  # Set the maximum allowed email size in k. (4000 = approx 5MB email [see docs])
  mail_maxattsize: 4000
  # Allow packing of files with tar and splitting it in pieces of mail_maxattsize.
  mail_splitandtar: true
  # Use uuencode instead of mutt. WARNING: Not all email clients work well with uuencoded attachments.
  mail_use_uuencoded_attachments: false
  # Email Address to send mail to? (user@domain.com)
  mail_address: root

# Encryption
mariadb_backup_encryption:
  enabled: false

mariadb_backup_multicore:
  enabled: false
  threads: 2

mariadb_backup_rotation:
  # Set rotation of daily backups. VALUE*24hours
  # If you want to keep only today's backups, you could choose 1, i.e. everything older than 24hours will be removed.
  daily: 6
  # Set rotation for weekly backups. VALUE*24hours
  weekly: 12
  # Set rotation for monthly backups. VALUE*24hours
  monthly: 3
  # Which day do you want monthly backups? (01 to 31)
  # If the chosen day is greater than the last day of the month, it will be done
  # on the last day of the month.
  # Set to 0 to disable monthly backups.
  do_monthly: "01"
  # Which day do you want weekly backups? (1 to 7 where 1 is Monday)
  # Set to 0 to disable weekly backups.
  do_weekly: "5"

mariadb_backup_exclude:
  databases:
    - performance_schema
    - information_schema
  tables: []

mariadb_backup_include:
  databases: []
  tables: []

mariadb_backup_cron:
  type: cron          # alternative: systemd
  daemon: ""          # "{{ 'cron' if ansible_os_family | lower == 'debian' else 'cronie' }}"
  enabled: true       # [true, false]
  minute: "58"        # 58
  hour: "2"           # 2
  weekday: ""         # *

mariadb_backup_backup_local_files: []
```

### use a pre running script

```yaml
mariadb_backup_pre_script:
  file: '/tmp/pre.sh'
  content: |
  #!/bin/bash
  echo "foo"
```


## Author and License

- Bodo Schulz

## License

[Apache](LICENSE)

**FREE SOFTWARE, HELL YEAH!**
