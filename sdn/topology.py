
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel


def create_topology():
    net = Mininet(
        controller=None,
        switch=OVSSwitch,
        autoSetMacs=True
    )

    net.addController(
        'c0',
        controller=RemoteController,
        ip='127.0.0.1',
        port=6653
    )

    # Two switches
    s1 = net.addSwitch('s1', protocols='OpenFlow13')
    s2 = net.addSwitch('s2', protocols='OpenFlow13')

    # One manager host and four worker hosts
    manager = net.addHost('h1', ip='10.0.0.1/24')
    w1 = net.addHost('h2', ip='10.0.0.2/24')
    w2 = net.addHost('h3', ip='10.0.0.3/24')
    w3 = net.addHost('h4', ip='10.0.0.4/24')
    w4 = net.addHost('h5', ip='10.0.0.5/24')

    # Manager and two workers on switch 1
    net.addLink(manager, s1)
    net.addLink(w1, s1)
    net.addLink(w2, s1)

    # Connect the two switches
    net.addLink(s1, s2)

    # Two workers on switch 2
    net.addLink(w3, s2)
    net.addLink(w4, s2)

    net.start()

    print("\n*** Two-switch topology started")
    print("*** Manager: h1 (10.0.0.1)")
    print("*** Workers: h2, h3, h4, h5")
    print("*** Switches: s1, s2")
    print("*** Type 'pingall' to test connectivity")
    print("*** Type 'exit' to stop Mininet\n")

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    create_topology()

