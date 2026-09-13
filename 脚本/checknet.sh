#!/bin/bash
ping -c 1 -W 1 192.168.142.1

result=$?

echo "$result"
