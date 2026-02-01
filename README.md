# Ansible Collection - bodsch.database

A collection of Ansible roles for MariadDB, Postgres and Tools.


## Requirements & Dependencies


## Included content


### Roles

| Role                                                                           | Build State | Description |
|:---------------------------------------------------------------------------    | :---------: | :----       |
| [bodsch.database.mariadb](./roles/mariadb/README.md)                           | [![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bodsch/ansible-collection-database/mariadb.yml?branch=main)][mariadb]                           | Ansible role to install and configure mariadb. |
| [bodsch.database.mariadb_backup](./roles/mariadb_backup/README.md)             | [![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bodsch/ansible-collection-database/mariadb_backup.yml?branch=main)][mariadb_backup]             | Installs and configures mariadb_backup. |
| [bodsch.database.postgres](./roles/postgres/README.md)                         | [![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bodsch/ansible-collection-database/postgres.yml?branch=main)][postgres]                         | Installs and configure postgres |
| [bodsch.database.postgresql_databases](./roles/postgresql_databases/README.md) | [![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bodsch/ansible-collection-database/postgresql_databases.yml?branch=main)][postgresql_databases] | create postgresql databases. |
| [bodsch.database.mysqltuner](./roles/mysqltuner/README.md)                           | [![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bodsch/ansible-collection-database/mysqltuner.yml?branch=main)][mysqltuner]               | Ansible role to install mysqltuner. |


[mariadb]: https://github.com/bodsch/ansible-collection-database/actions/workflows/mariadb.yml
[mariadb_backup]: https://github.com/bodsch/ansible-collection-database/actions/workflows/mariadb_backup.yml
[postgres]: https://github.com/bodsch/ansible-collection-database/actions/workflows/postgres.yml
[postgresql_databases]: https://github.com/bodsch/ansible-collection-database/actions/workflows/postgresql_databases.yml
[mysqltuner]: https://github.com/bodsch/ansible-collection-database/actions/workflows/mysqltuner.yml

### Modules

| Name                      | Description |
|:--------------------------|:----|
| [bodsch.database.mariadb_bootstrap](./plugins/modules/mariadb_bootstrap.py)                     | |
| [bodsch.database.mariadb_data_directory](./plugins/modules/mariadb_data_directory.py)           | |
| [bodsch.database.mariadb_replication](./plugins/modules/mariadb_replication.py)                 | |
| [bodsch.database.mariadb_root_password](./plugins/modules/mariadb_root_password.py)             | |
| [bodsch.database.mariadb_secure](./plugins/modules/mariadb_secure.py)                           | |
| [bodsch.database.mariadb_tls_certificates](./plugins/modules/mariadb_tls_certificates.py)       | |
| [bodsch.database.postgres_connection](./plugins/modules/postgres_connection.py)       | |


## Installing this collection

You can install the memsource collection with the Ansible Galaxy CLI:

```bash
#> ansible-galaxy collection install bodsch.database
```

To install directly from GitHub:

```bash
#> ansible-galaxy collection install git@github.com:bodsch/ansible-collection-database.git
```


You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: bodsch.database
```


## Contribution

Please read [Contribution](CONTRIBUTING.md)

## Development,  Branches (Git Tags)

The `master` Branch is my *Working Horse* includes the "latest, hot shit" and can be complete broken!

If you want to use something stable, please use a [Tagged Version](https://github.com/bodsch/ansible-collection-database/tags)!


## Author

- Bodo Schulz

## License

[Apache](LICENSE)

**FREE SOFTWARE, HELL YEAH!**
