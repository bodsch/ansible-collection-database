#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
PgSettingsReader: liest PostgreSQL-Settings als Dict.
Strategie:
1) Socket-Verbindung, falls Socket vorhanden.
2) TCP zu localhost:5432.
3) Fallback: postgresql.conf + Includes parsen.

Abhängigkeiten:
- psycopg2 (bevorzugt) ODER psycopg (psycopg3). Wenn beides fehlt, wird direkt geparst.
"""
from __future__ import annotations

import glob
# import json
import os
# import pathlib
import re
# import socket
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

# --- Hauptklasse -------------------------------------------------------------


@dataclass
class PgSettingsReader:

    module: Any
    keys: Optional[Iterable[str]] = None
    dbname: str = "postgres"
    user: Optional[str] = None  # None => lib Default
    connect_timeout: int = 5
    socket_dirs: Tuple[str, ...] = ("/var/run/postgresql", "/run/postgresql", "/tmp")
    tcp_host: str = "127.0.0.1"
    tcp_port: int = 5432
    conf_path: Optional[str] = None  # wenn None => auto

    def __post_init__(self):

        # self. module = module
        self.module.log(msg="PostgresConnection::__post_init__()")

        self._INCLUDE_RE = re.compile(
            r"""^\s*(include|include_if_exists)\s*=?\s*(['"])(.*?)\2\s*$"""
        )
        self._INCLUDE_DIR_RE = re.compile(
            r"""^\s*include_dir\s*=?\s*(['"])(.*?)\1\s*$"""
        )
        self._ASSIGN_RE = re.compile(r"""^\s*([a-zA-Z0-9_.]+)\s*=\s*(.+?)\s*$""")

    def read(self) -> Dict[str, str]:

        self.module.log(msg="PgSettingsReader::read()")

        # 1) Socket
        self.module.log("- socket ...")
        for d, port in self._discover_unix_sockets(self.socket_dirs):
            try:
                # dbname: str, user: Optional[str], host: Optional[str], port: Optional[int], timeout
                conn, kind = self._connect(
                    dbname=self.dbname,
                    user=self.user,
                    host=d,
                    port=port,
                    timeout=self.connect_timeout,
                )

                self.module.log(f"- kind {kind}")

                try:
                    return self._fetch_settings(conn, kind, self.keys)
                finally:
                    try:
                        conn.close()
                    except Exception as e:
                        self.module.log(f" ERROR close socket: {e}")
                        pass

            except Exception as e:
                self.module.log(msg=f"sql:failed host={d} port={port} error={e}")
                continue

        # 2) TCP
        self.module.log("- tcp ...")
        try:
            conn, kind = self._connect(
                self.dbname,
                self.user,
                self.tcp_host,
                self.tcp_port,
                self.connect_timeout,
            )
            try:
                return self._fetch_settings(conn, kind, self.keys)
            finally:
                try:
                    conn.close()
                except Exception as e:
                    self.module.log(f" ERROR close TCP: {e}")
                    pass
        except Exception as e:
            self.module.log(f" ERROR fetch settings over TCP: {e}")
            pass

        # 3) Datei-Parser
        self.module.log("- config ...")
        conf = self.parse_postgresql_conf(self.conf_path)
        if not conf:
            return {}

        return {k: conf[k] for k in self.keys if k in conf} if self.keys else conf

        if self.keys:
            return {k: v for k, v in conf.items() if k in set(self.keys)}

        return conf

    def _strip_comments(self, line: str) -> str:
        """Entfernt '#' Kommentare außerhalb von einfachen Quotes."""
        out, in_q = [], False
        i = 0
        while i < len(line):
            c = line[i]
            if c == "'" and (i == 0 or line[i - 1] != "\\"):
                in_q = not in_q
                out.append(c)
            elif c == "#" and not in_q:
                break
            else:
                out.append(c)
            i += 1
        return "".join(out).strip()

    def _unquote(self, value: str) -> str:
        v = value.strip()
        # Entferne optionale Quotes
        if len(v) >= 2 and v[0] == "'" and v[-1] == "'":
            v = v[1:-1]
            v = v.replace("\\'", "'")
        # Entferne trailing/leading Quotesfragmente
        return v.strip()

    def _parse_file(self, path: str, seen: set[str], result: Dict[str, str]) -> None:
        """ """
        # self.module.log(msg=f"PgSettingsReader::_parse_file(path: {path}, seen: {seen}, result:{result})")

        base_dir = os.path.dirname(path)

        if path in seen:
            return
        seen.add(path)

        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            return

        for raw in lines:
            line = self._strip_comments(raw)
            if not line:
                continue

            m_dir = self._INCLUDE_DIR_RE.match(line)
            if m_dir:
                inc_dir = m_dir.group(2)
                if not os.path.isabs(inc_dir):
                    inc_dir = os.path.join(base_dir, inc_dir)
                for fp in sorted(glob.glob(os.path.join(inc_dir, "*.conf"))):
                    self._parse_file(fp, seen, result)

                continue

            m_inc = self._INCLUDE_RE.match(line)
            if m_inc:
                kind, inc = m_inc.group(1), m_inc.group(3)
                if not os.path.isabs(inc):
                    inc = os.path.join(base_dir, inc)
                if kind == "include" or os.path.exists(
                    inc
                ):  # include_if_exists nur wenn vorhanden
                    self._parse_file(inc, seen, result)
                continue

            m_set = self._ASSIGN_RE.match(line)
            if m_set:
                key, val = m_set.group(1), self._unquote(m_set.group(2))
                result[key] = val

    def parse_postgresql_conf(self, conf_path: Optional[str] = None) -> Dict[str, str]:
        """Sucht conf automatisch, wenn nicht angegeben, und parst inkl. Includes."""

        self.module.log(
            msg=f"PgSettingsReader::parse_postgresql_conf(conf_path: {conf_path})"
        )

        candidates = []
        if conf_path:
            candidates.append(conf_path)
        else:
            candidates += [
                "/var/lib/pgsql/data/postgresql.conf",
                "/var/lib/pgsql/*/data/postgresql.conf",
                "/usr/local/pgsql/data/postgresql.conf",
                "/etc/postgresql/*/*/postgresql.conf",
                "/etc/postgresql/*/main/postgresql.conf",
            ]

        files = []

        for c in candidates:
            if "*" in c:
                files += glob.glob(c)
            elif os.path.exists(c):
                files.append(c)

        files = [f for f in files if os.path.isfile(f)]
        # uniq files
        files = list(set(files))
        # self.module.log(msg=f" - files: {files}")

        if not files:
            return {}

        settings: Dict[str, str] = {}
        seen: set[str] = set()

        self._parse_file(sorted(files)[0], seen, settings)

        return settings

    # --- DB Adapter --------------------------------------------------------------

    def _connect(
        self,
        dbname: str,
        user: Optional[str],
        host: Optional[str],
        port: Optional[int],
        timeout: int,
    ):
        """Versucht psycopg2, sonst psycopg3. Gibt (conn, kind) zurück, kind in {'pg2','pg3'}."""
        self.module.log(
            msg=f"PgSettingsReader::_connect(dbname: {dbname}, user: {user}, host: {host}, port: {port}, timeout: {timeout})"
        )

        try:
            import psycopg2  # type: ignore

            conn = psycopg2.connect(
                dbname=dbname, user=user, host=host, port=port, connect_timeout=timeout
            )
            return conn, "pg2"

        except Exception as e_pg2:
            try:
                import psycopg  # type: ignore

                conn = psycopg.connect(
                    dbname=dbname,
                    user=user,
                    host=host,
                    port=port,
                    connect_timeout=timeout,
                )
                return conn, "pg3"

            except Exception as e_pg3:
                raise RuntimeError(f"DB-Verbindung fehlgeschlagen: {e_pg2} / {e_pg3}")

    def _fetch_settings_OLD(
        self, conn, kind: str, keys: Optional[Iterable[str]]
    ) -> Dict[str, str]:
        """ """
        self.module.log(
            msg=f"PgSettingsReader::_fetch_settings(conn, kind: {kind}, keys: {keys})"
        )

        sql = (
            "SELECT name, setting FROM pg_settings"
            if not keys
            else "SELECT name, setting FROM pg_settings WHERE name = ANY(%s)"
        )

        self.module.log(msg=f"= sql: {sql}")

        _sql = sql, (list(keys),)

        self.module.log(msg=f"= _sql: {_sql}")

        if kind == "pg2":
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (list(keys),) if keys else None)

                    return {name: val for name, val in cur.fetchall()}
        else:  # pg3
            with conn:
                with conn.cursor() as cur:
                    try:
                        cur.execute(sql, (list(keys),) if keys else None)
                    except Exception as e:
                        self.module.log(msg=f"ERROR: {e}")

                    return {name: val for name, val in cur.fetchall()}

    def _fetch_settings(
        self, conn, kind: str, keys: Optional[Iterable[str]]
    ) -> Dict[str, str]:
        """ """
        self.module.log(
            msg=f"PgSettingsReader::_fetch_settings(conn, kind: {kind}, keys: {keys})"
        )

        if keys is not None:
            names = list(keys)
            if not names:
                return {}
            sql = "SELECT name, setting FROM pg_settings WHERE name = ANY(%s::text[])"
            params = (names,)
        else:
            sql = "SELECT name, setting FROM pg_settings"
            params = ()

        self.module.log(msg=f"= sql: {sql}")
        self.module.log(msg=f"= params: {params}")

        with conn:
            # psycopg3: binary=False erzwingen (sonst ggf. bytes)
            if kind == "pg3":
                cur = conn.cursor(binary=False)
            else:
                cur = conn.cursor()

            with cur:
                cur.execute(sql, params)
                rows = cur.fetchall()

                self.module.log(f" type {type(rows)}")
                self.module.log(f" {rows}")

                out: Dict[str, str] = {}
                for name, val in rows:
                    k = self._decode_db_value(conn, name)
                    v = self._decode_db_value(conn, val)
                    out[str(k)] = "" if v is None else str(v)

                self.module.log(f" {out}")
                return out

    # --- Socket-Erkennung --------------------------------------------------------

    def _discover_unix_sockets(
        self, extra_dirs: Optional[Iterable[str]] = None
    ) -> List[Tuple[str, int]]:
        """Finde .s.PGSQL.* in üblichen Verzeichnissen. Liefert (dir, port)."""

        self.module.log(
            msg=f"PgSettingsReader::_discover_unix_sockets(extra_dirs: {extra_dirs})"
        )

        dirs = list(
            filter(
                None,
                ["/var/run/postgresql", "/run/postgresql", "/tmp", *(extra_dirs or [])],
            )
        )

        self.module.log(msg=f" - dirs: {dirs}")

        # Verzeichnisse deduplizieren: Symlinks -> Zielpfad
        canon_dirs, seen_dirs = [], set()
        for d in dirs:
            rp = os.path.realpath(d)
            if rp not in seen_dirs:
                seen_dirs.add(rp)
                canon_dirs.append(rp)

        # Sockets finden und per Inode deduplizieren
        found_by_inode: dict[tuple[int, int], tuple[str, int]] = {}
        for d in canon_dirs:
            try:
                for p in glob.glob(os.path.join(d, ".s.PGSQL.*")):
                    base, _, port_s = p.rpartition(".")
                    try:
                        port = int(port_s)
                    except ValueError:
                        continue
                    try:
                        st = os.stat(p)
                        key = (st.st_dev, st.st_ino)  # eindeutig pro Socket
                    except OSError:
                        key = (-1, hash(os.path.realpath(p)))
                    found_by_inode[key] = (d, port)
            except Exception:
                continue

        out = list(found_by_inode.values())
        out.sort(key=lambda x: (x[1] != 5432, x[1]))  # 5432 zuerst

        self.module.log(msg=f"= found: {out}")
        return out

    # --- postgresql.conf Parser --------------------------------------------------

    def _decode_db_value(self, conn: Any, v: Any) -> Any:
        """Normalisiert DB-Werte für JSON: bytes -> str (mit DB-Encoding)."""
        if v is None or isinstance(v, str):
            return v

        if isinstance(v, (bytes, bytearray, memoryview)):
            enc = "utf-8"
            try:
                # psycopg2
                if getattr(conn, "encoding", None):
                    enc = conn.encoding
                # psycopg3
                elif getattr(getattr(conn, "info", None), "encoding", None):
                    enc = conn.info.encoding
            except Exception:
                pass
            return bytes(v).decode(enc, errors="replace")

        # Fallback: in String wandeln (pg_settings.setting ist text, aber sicher ist sicher)
        return str(v)


# --- CLI-Demo ---------------------------------------------------------------
"""
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="PostgreSQL Settings als JSON ausgeben")
    ap.add_argument("--keys", nargs="*", help="Schlüssel filtern, z.B. listen_addresses port unix_socket_directories")
    ap.add_argument("--conf", help="Pfad zu postgresql.conf (optional)")
    ap.add_argument("--user", help="DB-User (optional)")
    ap.add_argument("--db", default="postgres", help="DB-Name (default: postgres)")
    ap.add_argument("--timeout", type=int, default=5)
    args = ap.parse_args()

    reader = PgSettingsReader(
        keys=args.keys,
        dbname=args.db,
        user=args.user,
        connect_timeout=args.timeout,
        conf_path=args.conf,
    )
    data = reader.read()
    print(json.dumps(data, ensure_ascii=False))
"""
