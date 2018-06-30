#!/bin/bash
set -e
pid=()
proceso="uwsgi"
run="uwsgi /root/unAventon/uwsgi.ini"
pathLockFile="/var/run/"

### PRINT WRAPPERS FUNCTIONS #####################
function green {
        echo -e "\e[92m${1}\e[0m"
}

function bold {
        echo -e "\e[1m${1}\e[21m"
}

function logInfo {
        echo -e "\e[34m" "INFO:" "\e[0m "${1}
}

function logError {
        echo -e "\e[91m" "ERROR:" "\e[0m"$1
}
################################################

function isDown {
        result=$(pgrep $1 | wc -w)
        if [ $result == 0 ]; then
                echo 0
        else
                echo 1

        fi
}

# MAIN FUNCTIONS

function start {
        # debloqueo el proceso
        rm -rf ${pathLockFile}block_${1}
        $run &
}

function stop {
        #1 bloquear proceso (para no poder levantarlo)
        touch  ${pathLockFile}block_${1}
        #2 matar los procesos
        killall -INT uwsgi
}

function restart {
        stop $1
        sleep 10
        start $1
}



function status {
        if [ $(isDown $1) == 0 ]; then
                if [ -f ${pathLockFile}block_${1} ]; then
                        echo "unAventon -> status STOP & BLOCKED"
                else
                        echo "unAventon -> status STOP"
                fi
        else
                echo "unAventon -> status is "$(green "$(bold RUNNING)")
        fi
}

function upIfDown {
        if [ -f ${pathLockFile}block_${1} ]; then 
                exit 0
        else
                if [ $(isDown $1) == 0 ]; then
                        start $1
                fi
        fi
}

######################################################


case "$1" in
  --start | start)
          logInfo "unAventon -> iniciando ${proceso}"
          start $proceso
        ;;
  --restart | restart)
          logInfo "unAventon -> reiniciando ${proceso}"
          restart $proceso
        ;;
  --start-if-down | ifdown)
          upIfDown $proceso
        ;;
  --stop | stop)
          logInfo "unAventon -> deteniendo ${proceso}"
          stop $proceso
        ;;
  --status | status)
        status $proceso
        ;;
        *)
          echo "* Usage: (start|stop|ifdown|restart|status)"
esac
exit 0

