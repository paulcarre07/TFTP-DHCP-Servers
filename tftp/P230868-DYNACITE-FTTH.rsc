/interface bridge
add name=bridge1 protocol-mode=none vlan-filtering=yes
/interface ethernet
set [find default-name=ether1] comment="* INTERCO SWITCH *"
set [find default-name=ether2] comment="* NOT-USED *"
set [find default-name=ether3] comment="* NOT-USED *"
set [find default-name=ether4] comment="* NOT-USED *"
set [find default-name=ether5] comment="* NOT-USED *"
set [find default-name=ether6] comment="* NOT-USED *"
set [find default-name=ether7] comment="* NOT-USED *"
set [find default-name=ether8] comment="* OIP-FTTH-ORANGE *"
/interface vlan
add interface=ether2 name=ID10-DATA vlan-id=10
add interface=ether2 name=ID20-ADMIN vlan-id=20
add interface=ether2 name=ID70-SECU-BAT vlan-id=70
/interface pppoe-client
add add-default-route=yes disabled=no interface=ether8 max-mtu=1432 name="* OIP-FTTH-ORANGE *" use-peer-dns=yes user=P232558-IPL1393@ipline.openip.oip
/interface wireless security-profiles
set [find default=yes] supplicant-identity=MikroTik
/port
set 0 name=serial0
/snmp community
set [ find default=yes ] addresses=169.254.0.0/16,100.64.0.0/10,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,195.28.195.108/32 name=DYNACITE
/interface bridge port
add bridge=bridge1 interface=ether1
add bridge=bridge1 interface=ether2
/interface bridge vlan
add bridge=bridge1 tagged=ether1 vlan-ids=10,20,70
add bridge=bridge1 tagged=ether2 vlan-ids=20,70
/ip address
add address=172.29.136.254/24 interface=ID10-DATA network=172.29.136.0
add address=172.29.137.254/24 interface=ID20-ADMIN network=172.29.137.0
add address=172.29.142.254/24 interface=ID70-SECU-BAT network=172.29.142.0
add address=169.254.28.0/31 interface=ether8 network=169.254.28.0
/ip firewall address-list
add address=172.29.136.0 list=bgp-network
add address=172.29.137.0 list=bgp-network
add address=172.29.142.0 list=bgp-network
add address=169.254.28.0 list=bgp-network
/ip service
set telnet disabled=yes
set ftp disabled=yes
set www disabled=yes
set ssh address=169.254.0.0/16,100.64.0.0/10,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
set www-ssl address=169.254.0.0/16,100.68.0.0/16,100.67.0.0/16,10.0.0.0/8,172.0.0.0/9,192.168.0.0/16,100.66.3.0/24
set api disabled=yes
set winbox disabled=yes
set api-ssl disabled=yes
/routing bgp connection
add as=65015 connect=yes disabled=no hold-time=20s keepalive-time=5s listen=yes local.address=169.254.28.0 .role=ebgp multihop=yes name=DYNACITE output.filter-chain=LAN .keep-sent-attributes=yes .network=bgp-network remote.address=169.254.28.1 .as=65535 router-id=169.254.28.0
/snmp
set contact=support.entreprises@dstny.fr enabled=yes location=Rillieux_REGIE
/system clock
set time-zone-name=Europe/Paris
/system identity
set name=P230868-DYNACITE-Rillieux_REGIE
/system note
set note="*********************************\
    \nIPLINE ADMINISTRATION\
    \nFor further information\
    \nMail : support.entreprises@dstny.fr\
    \nPhone : +334 27 70 90 00\
    \n*********************************" show-at-login=no
/system routerboard settings
set enter-setup-on=delete-key
/tool bandwidth-server
set enabled=no
/tool mac-server ping
set enabled=no
/interface vrrp add interface=ADMIN vrid=1 priority=110
/ip address add address=172.29.136.254/24 interface=vrrp1 
/interface vrrp add interface=SECU-BAT vrid=2 priority=5
/ip address add address=172.29.142.254/24 interface=vrrp2 