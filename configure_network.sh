# configure_network.sh
#!/bin/bash

# Set network interface as DHCP
function set_dhcp {
    sudo bash -c "cat > /etc/dhcpcd.conf" <<EOL
interface $1
static ip_address=$2/24
static routers=$3
static domain_name_servers=$4
EOL
    sudo systemctl restart dhcpcd
}

# Set network interface as static IP
function set_static_ip {
    sudo bash -c "cat > /etc/dhcpcd.conf" <<EOL
interface $1
static ip_address=$2/24
static routers=$3
static domain_name_servers=$4
EOL
    sudo systemctl restart dhcpcd
}
# chmod +x network_setup.sh
# ./network_setup.sh eth0 # For DHCP
# ./network_setup.sh eth1 192.168.1.10 255.255.255.0 # For static IP
