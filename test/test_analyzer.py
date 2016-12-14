#!/usr/bin/env python3

from litex.soc.tools.remote import RemoteClient
from litescope.software.driver.analyzer import LiteScopeAnalyzerDriver

wb = RemoteClient("192.168.100.50", 1234, csr_csv='build/opsis_video/test/csr.csv', csr_data_width=8, debug=False)
wb.open()

# # #

analyzer = LiteScopeAnalyzerDriver(wb.regs, "analyzer", config_csv='build/opsis_video/test/analyzer.csv', debug=True)
analyzer.configure_trigger(cond={'hdmi_in0_chansync_data_in0_de': 0})
analyzer.configure_subsampler(1)
analyzer.run(offset=16, length=2048)
while not analyzer.done():
    pass
analyzer.upload()
analyzer.save("dump.vcd")

# # #

wb.close()
