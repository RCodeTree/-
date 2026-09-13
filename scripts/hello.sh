#!/bin/bash
username=$(whoami)
dir=$(pwd)
time=$(date "+%Y-%m-%d %H:%M:%S")
kernel=$(uname -r)
os=$(cat /etc/os-release)
ip=$(ip a | grep -E "inet" | awk '{print $2}' | grep "24" | awk -F/ '{print $1}')
osname=$(echo $os | grep "PRETTY_NAME" | awk -F"=" '{print $2}')



printf "欢迎来到Linux的世界，%s\n" "$username"
printf "当前IP地址：%s\n" "$ip"
printf "当前目录：%s\n" "$dir"
printf "当前内核：%s\n" "$kernel"
printf "当前操作系统：%s\n" "$osname"
printf "当前时间：%s\n" "$time"


