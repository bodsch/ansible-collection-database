tail -F /var/log/mysql/*.log

rm -rfv /var/lib/mysql/*log-bin* /var/lib/mysql/galera.cache /var/lib/mysql/grastate.dat /var/lib/mysql/bootstrapped
