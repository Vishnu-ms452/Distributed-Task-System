from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel


def create_topology():

    net = Mininet(
        controller=None,
        switch=OVSSwitch,
        autoSetMacs=True,
        build=False
    )

    net.addController(
        "c0",
        controller=RemoteController,
        ip="127.0.0.1",
        port=6653
    )

    # Task Manager and four workers.
    h1 = net.addHost("h1", ip="10.0.0.1/24")
    h2 = net.addHost("h2", ip="10.0.0.2/24")
    h3 = net.addHost("h3", ip="10.0.0.3/24")
    h4 = net.addHost("h4", ip="10.0.0.4/24")
    h5 = net.addHost("h5", ip="10.0.0.5/24")

    # Two OpenFlow 1.3 switches.
    s1 = net.addSwitch(
        "s1",
        dpid="0000000000000001",
        protocols="OpenFlow13"
    )

    s2 = net.addSwitch(
        "s2",
        dpid="0000000000000002",
        protocols="OpenFlow13"
    )

    # Manager and two workers on s1.
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)

    # Two workers on s2.
    net.addLink(h4, s2)
    net.addLink(h5, s2)

    # Two redundant links between switches.
    net.addLink(s1, s2)
    net.addLink(s1, s2)

    try:

        net.build()
        net.start()

        # Allow STP BPDU frames through OVS.
        for sw in (s1, s2):
            sw.cmd(
                "ovs-vsctl set Bridge %s other_config:forward-bpdu=true"
                % sw.name
            )

        print("\n*** DYNAMIC SDN TOPOLOGY STARTED")
        print("*** h1 = Task Manager")
        print("*** h2 = Worker W1")
        print("*** h3 = Worker W2")
        print("*** h4 = Worker W3")
        print("*** h5 = Worker W4")
        print("*** s1 and s2 have TWO redundant links")
        print("*** Run: pingall | net | links | exit")

        CLI(net)

    finally:
        net.stop()


if __name__ == "__main__":

    setLogLevel("info")
    create_topology()
