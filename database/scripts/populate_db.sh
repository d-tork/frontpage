#!/bin/bash

gunzip < /tmp/gs_backup.sql.gz | mysql -u root -pmy-secret-pw gutensearch
