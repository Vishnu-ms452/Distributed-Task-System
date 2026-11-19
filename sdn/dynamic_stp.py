from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import (
    CONFIG_DISPATCHER,
    MAIN_DISPATCHER,
    set_ev_cls
)
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib import stplib
from os_ken.lib import dpid as dpid_lib
from os_ken.lib.packet import packet, ethernet, ether_types


class DynamicSTPController(app_manager.OSKenApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    _CONTEXTS = {
        "stplib": stplib.Stp
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.stp = kwargs["stplib"]
        self.mac_to_port = {}

        # Two-switch configuration.
        # s1 has higher priority and becomes the root bridge.
        config = {
            dpid_lib.str_to_dpid("0000000000000001"): {
                "bridge": {"priority": 0x8000}
            },

            dpid_lib.str_to_dpid("0000000000000002"): {
                "bridge": {"priority": 0x9000}
            }
        }

        self.stp.set_config(config)

        self.logger.info("Dynamic STP Controller initialized")

    def add_flow(self, dp, priority, match, actions):

        parser = dp.ofproto_parser
        ofp = dp.ofproto

        instructions = [
            parser.OFPInstructionActions(
                ofp.OFPIT_APPLY_ACTIONS,
                actions
            )
        ]

        dp.send_msg(
            parser.OFPFlowMod(
                datapath=dp,
                priority=priority,
                match=match,
                instructions=instructions
            )
        )

    @set_ev_cls(
        ofp_event.EventOFPSwitchFeatures,
        CONFIG_DISPATCHER
    )
    def switch_features(self, ev):

        dp = ev.msg.datapath
        parser = dp.ofproto_parser
        ofp = dp.ofproto

        self.mac_to_port.setdefault(dp.id, {})

        actions = [
            parser.OFPActionOutput(
                ofp.OFPP_CONTROLLER,
                ofp.OFPCML_NO_BUFFER
            )
        ]

        self.add_flow(
            dp,
            0,
            parser.OFPMatch(),
            actions
        )

        self.logger.info(
            "Switch connected: %s",
            dp.id
        )

    @set_ev_cls(
        stplib.EventPacketIn,
        MAIN_DISPATCHER
    )
    def packet_in(self, ev):

        msg = ev.msg
        dp = msg.datapath

        ofp = dp.ofproto
        parser = dp.ofproto_parser

        in_port = msg.match["in_port"]

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth is None:
            return

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        dpid = dp.id

        table = self.mac_to_port.setdefault(dpid, {})

        # Learn source MAC address.
        table[eth.src] = in_port

        # Find destination port.
        out_port = table.get(
            eth.dst,
            ofp.OFPP_FLOOD
        )

        actions = [
            parser.OFPActionOutput(out_port)
        ]

        data = None

        if msg.buffer_id == ofp.OFP_NO_BUFFER:
            data = msg.data

        dp.send_msg(
            parser.OFPPacketOut(
                datapath=dp,
                buffer_id=msg.buffer_id,
                in_port=in_port,
                actions=actions,
                data=data
            )
        )

    @set_ev_cls(
        stplib.EventTopologyChange,
        MAIN_DISPATCHER
    )
    def topology_changed(self, ev):

        # Clear MAC learning after topology changes.
        self.mac_to_port.clear()

        self.logger.warning(
            "DYNAMIC SDN: Topology change detected on switch %s",
            ev.dp.id
        )

    @set_ev_cls(
        stplib.EventPortStateChange,
        MAIN_DISPATCHER
    )
    def port_state_changed(self, ev):

        states = {
            stplib.PORT_STATE_DISABLE: "DISABLE",
            stplib.PORT_STATE_BLOCK: "BLOCK",
            stplib.PORT_STATE_LISTEN: "LISTEN",
            stplib.PORT_STATE_LEARN: "LEARN",
            stplib.PORT_STATE_FORWARD: "FORWARD"
        }

        state = states.get(
            ev.port_state,
            str(ev.port_state)
        )

        self.logger.info(
            "DYNAMIC SDN: Switch=%s Port=%s State=%s",
            ev.dp.id,
            ev.port_no,
            state
        )
