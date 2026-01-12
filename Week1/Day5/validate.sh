#!/bin/bash

mkdir -p logs
LOG_FILE="logs/validate.log"

if [ ! -d "src" ]; then
	echo "$(date) src folder missing " >>$LOG_FILE
	exit 1
fi

echo "$(date) ✅ Validation passed" >> $LOG_FILE
exit 0

