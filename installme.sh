vi /home/nunpa/xblock-file-storage/setup.py;
sudo -u edxapp /edx/bin/pip.edxapp install /home/nunpa/xblock-file-storage;
sudo /edx/bin/supervisorctl -c /edx/etc/supervisord.conf restart edxapp:;
tail -f /edx/var/log/supervisor/cmstderr.log
