"""A Python Pulumi program"""

import pulumi
import pulumi_openstack as compute

CLUSTER_NAME = "lala"
NODE_CIDR = "192.168.42.0/24"

MASTER_NODE = ["node1", "node2"]
IMAGE = "Ubuntu_18.04"

EXT_NET_ID = "970ace5c-458f-484a-a660-0903bcfd91ad"
EXT_NET_NAME = "floating-net"

network1 = compute.networking.Network(CLUSTER_NAME + "-network-1", admin_state_up="true")

subnet1 = compute.networking.Subnet(CLUSTER_NAME + "-subnet-1",
  cidr=NODE_CIDR,
  ip_version=4,
  network_id=network1.id)

router1 = compute.networking.Router("router1", external_network_id=EXT_NET_ID)
router_interface1 = compute.networking.RouterInterface(CLUSTER_NAME + "router-1",
    router_id=router1.id,
    subnet_id=subnet1.id)


secgroup1 = compute.compute.SecGroup(CLUSTER_NAME + "-sec-1",
  description="a security group",
  rules=[{
    "cidr": "0.0.0.0/0",
    "fromPort": 22,
    "ipProtocol": "tcp",
    "toPort": 22,
  }])

for vm in MASTER_NODE:
  port1 = compute.networking.Port(vm + "port1",
    admin_state_up="true",
    fixed_ips=[{
      "subnet_id": subnet1.id,
    }],
    network_id=network1.id,
    security_group_ids=[secgroup1.id])

  floatip1 = compute.networking.FloatingIp(CLUSTER_NAME + " " + vm, pool=EXT_NET_NAME)

  instance1 = compute.compute.Instance(vm,
    flavor_name='c1.2',
    image_name=IMAGE,
    networks=[{"port": port1.id,}],
    security_groups=[secgroup1.name]
  )

  fip1 = compute.networking.FloatingIpAssociate(CLUSTER_NAME + " " + vm,
      floating_ip=floatip1.address,
      port_id=port1.id)

