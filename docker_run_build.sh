#!/bin/bash

# Zabbix Docker Compose Manager
# Usage: ./script.sh [start|stop|restart|status|logs]

CONFIG_FILE="docker-compose.yml"
NETWORK_NAME="zabbix-net"
MYSQL_VOLUME="./mysql-data"

case "$1" in
    start)
        echo "Starting Zabbix containers..."
        # Create network if not exists
        docker network inspect $NETWORK_NAME >/dev/null 2>&1 || docker network create $NETWORK_NAME
        
        # Create mysql data directory if not exists
        mkdir -p $MYSQL_VOLUME
        
        docker-compose -f $CONFIG_FILE up -d
        echo "Zabbix should be available at http://localhost:8051 (default credentials: Admin/zabbix)"
        ;;
    stop)
        echo "Stopping Zabbix containers..."
        docker-compose -f $CONFIG_FILE down
        ;;
    restart)
        echo "Restarting Zabbix containers..."
        docker-compose -f $CONFIG_FILE restart
        ;;
    status)
        echo "Container Status:"
        docker-compose -f $CONFIG_FILE ps
        ;;
    logs)
        echo "Showing logs (press Ctrl+C to exit)..."
        docker-compose -f $CONFIG_FILE logs -f
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac

exit 0
