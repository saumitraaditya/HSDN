#!/bin/bash
cd /mnt/mydrive
unzip remote_config.zip
sudo ovs-vsctl add-br CLO-br
# have to connect the bridge to controller
sudo ovs-vsctl set-controller CLO-br tcp:127.0.0.1:6653
cp dns-config.json deployment/namingSupport
cp ipop-config.json deployment/perso-ipop/
sudo cp -r deployment/namingSupport /mnt/mydrive/Linuxcontainers/ubuntu_lxc/rootfs/
sudo lxc-start -n ubuntu_lxc
lxc-start -n ubuntu_lxc
lxc-attach -n ubuntu_lxc -- echo "nameserver 127.0.0.1" | sudo tee -a /mnt/mydrive/Linuxcontainers/ubuntu_lxc/rootfs/etc/resolvconf/resolv.conf.d/head > /dev/null
lxc-attach -n ubuntu_lxc -- resolvconf -u
sudo docker container run -t -d  -p 6633:6633 -p 6653:6653 --name onos1 saumitraaditya/social_gateway:1.1
sleep 60
sudo docker exec onos1 ./script.sh
sudo docker inspect --format '{{ .NetworkSettings.IPAddress }}' onos1>/mnt/mydrive/onos_ip.txt
onos_ip=$(</mnt/mydrive/onos_ip.txt)
curl --user onos:rocks -X POST -H "Content-Type: application/json" http://${onos_ip}:8181/onos/v1/network/configuration/ -d @onos-dhcp-config.json
curl --user onos:rocks -X POST -H "Content-Type: application/json" http://${onos_ip}:8181/onos/v1/network/configuration/ -d @onos-osnBridge-config.json
sudo ovs-vsctl add-port CLO-br camera
sudo ovs-vsctl add-port CLO-br compute
sudo lxc-attach -n ubuntu_lxc -- dhclient  camera
sudo lxc-attach -n ubuntu_lxc -- dhclient  compute
sleep 5
# start naming inside container
sudo lxc-attach -n ubuntu_lxc -- nohup ./namingSupport/script.sh
#sudo lxc-attach -n ubuntu_lxc -- nohup 	python /namingSupport/dnschef.py --fakeip 127.0.0.1 --socialAccount /namingSupport/dns-config.json -q
cd deployment/perso-ipop
sudo ./ipop-tincan &
python3 -m controller.Controller -c ipop-config.json &
cd ..
python3 admin_main.py -s ../social-config-admin.json -r ../static-resources.json &
