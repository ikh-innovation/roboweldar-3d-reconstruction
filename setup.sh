#!/usr/bin/env bash         

# login as root and run this script via bash:

apt-get update
apt-get install python3.6 wget
mkdir -p deps && cd deps

echo "Downloading Meshroom..."
wget https://db.3dscan.io/static/Meshroom-2019.2.0-linux.tar.gz

if [ $? -eq 0 ]; then
   echo "Meshroom successfully downloaded!"
else
   echo "Error!"
fi


echo "Extracting Meshroom to deps..."
tar -xvf Meshroom-2019.2.0-linux.tar.gz
if [ $? -eq 0 ]; then
   echo "Meshroom successfully extracted to deps!" 
else
   echo "Error!"
fi


