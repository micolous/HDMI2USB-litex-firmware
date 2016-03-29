#!/usr/bin/env python3

from litex.soc.tools.remote import RemoteClient
from litescope.software.driver.analyzer import LiteScopeAnalyzerDriver

wb = RemoteClient(debug=False, csr_data_width=8)
wb.open()

# # #

logic_analyzer = LiteScopeAnalyzerDriver(wb.regs, "analyzer", debug=True)

cond = {"ethphy_sink_valid": 1, "ethphy_sink_ready": 1}
logic_analyzer.configure_trigger(cond=cond)
logic_analyzer.run(offset=16, length=512)

while not logic_analyzer.done():
    pass
logic_analyzer.upload()

logic_analyzer.save("dump.vcd")

# # #

wb.close()