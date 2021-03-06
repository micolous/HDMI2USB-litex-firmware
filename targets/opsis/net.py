from litex.gen.fhdl.specials import Keep
from litex.soc.integration.soc_core import mem_decoder
from litex.soc.integration.soc_sdram import *

from liteeth.core.mac import LiteEthMAC

from gateware.s6rgmii import LiteEthPHYRGMII

from targets.utils import csr_map_update
from targets.opsis.base import SoC as BaseSoC


class NetSoC(BaseSoC):
    csr_peripherals = (
        "ethphy",
        "ethmac",
    )
    csr_map_update(BaseSoC.csr_map, csr_peripherals)

    interrupt_map = {
        "ethmac": 2,
    }
    interrupt_map.update(BaseSoC.interrupt_map)

    mem_map = {
        "ethmac": 0x30000000,  # (shadow @0xb0000000)
    }
    mem_map.update(BaseSoC.mem_map)

    def __init__(self, platform, *args, **kwargs):
        BaseSoC.__init__(self, platform, *args, **kwargs)

        self.submodules.ethphy = LiteEthPHYRGMII(
            platform.request("eth_clocks"),
            platform.request("eth"))
        self.platform.add_source("gateware/rgmii_if.vhd")
        self.submodules.ethmac = LiteEthMAC(
            phy=self.ethphy, dw=32, interface="wishbone")
        self.add_wb_slave(mem_decoder(self.mem_map["ethmac"]), self.ethmac.bus)
        self.add_memory_region("ethmac",
            self.mem_map["ethmac"] | self.shadow_base, 0x2000)

        self.specials += [
            Keep(self.ethphy.crg.cd_eth_rx.clk),
#            Keep(self.ethphy.crg.cd_eth_tx.clk),
        ]

        self.platform.add_period_constraint(self.ethphy.crg.cd_eth_rx.clk, 8.0)

        self.platform.add_false_path_constraints(
            self.crg.cd_sys.clk,
            self.ethphy.crg.cd_eth_rx.clk)

    def configure_iprange(self, iprange):
        iprange = [int(x) for x in iprange.split(".")]
        while len(iprange) < 4:
            iprange.append(0)
        # Our IP address
        self._configure_ip("LOCALIP", iprange[:-1]+[50])
        # IP address of tftp host
        self._configure_ip("REMOTEIP", iprange[:-1]+[100])

    def _configure_ip(self, ip_type, ip):
        for i, e in enumerate(ip):
            s = ip_type + str(i + 1)
            s = s.upper()
            self.add_constant(s, e)


SoC = NetSoC
