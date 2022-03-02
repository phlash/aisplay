#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: AIS receiver
# Author: Phlash
# Copyright: Phil Ashby, 2022
# Description: AIS reception via SoapyTCP (dual channel)
# GNU Radio version: 3.8.2.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import eng_notation
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
import math
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import zeromq
from gnuradio.qtgui import Range, RangeWidget
import soapy
import distutils
from distutils import util

from gnuradio import qtgui

class AIS(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "AIS receiver")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("AIS receiver")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "AIS")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 192000
        self.zmq_address = zmq_address = "tcp://127.0.0.1:7533"
        self.xlate_taps = xlate_taps = firdes.low_pass(1, samp_rate, 15000, 5000, firdes.WIN_HAMMING, 6.76)
        self.rf_gain = rf_gain = 10
        self.ais_string = ais_string = '--'

        ##################################################
        # Blocks
        ##################################################
        self._rf_gain_range = Range(0, 50, 1, 10, 200)
        self._rf_gain_win = RangeWidget(self._rf_gain_range, self.set_rf_gain, 'RF gain (dB)', "counter_slider", int)
        self.top_grid_layout.addWidget(self._rf_gain_win)
        self.zeromq_push_sink_0 = zeromq.push_sink(gr.sizeof_short, 1, zmq_address, 100, False, -1)
        self.soapy_source_0 = None
        # Make sure that the gain mode is valid
        if('Overall' not in ['Overall', 'Specific', 'Settings Field']):
            raise ValueError("Wrong gain mode on channel 0. Allowed gain modes: "
                  "['Overall', 'Specific', 'Settings Field']")

        dev = 'driver=tcpremote'

        # Stream arguments for every activated stream
        tune_args = ['']
        settings = ['']

        # Setup the device arguments
        dev_args = ''

        self.soapy_source_0 = soapy.source(1, dev, dev_args, '',
                                  tune_args, settings, samp_rate, "fc32")



        self.soapy_source_0.set_dc_removal(0,bool(distutils.util.strtobool('False')))

        # Set up DC offset. If set to (0, 0) internally the source block
        # will handle the case if no DC offset correction is supported
        self.soapy_source_0.set_dc_offset(0,0)

        # Setup IQ Balance. If set to (0, 0) internally the source block
        # will handle the case if no IQ balance correction is supported
        self.soapy_source_0.set_iq_balance(0,0)

        self.soapy_source_0.set_agc(0,False)

        # generic frequency setting should be specified first
        self.soapy_source_0.set_frequency(0, 162.0e6)

        self.soapy_source_0.set_frequency(0,"BB",0)

        # Setup Frequency correction. If set to 0 internally the source block
        # will handle the case if no frequency correction is supported
        self.soapy_source_0.set_frequency_correction(0,0)

        self.soapy_source_0.set_antenna(0,'RX')

        self.soapy_source_0.set_bandwidth(0,192000)

        if('Overall' != 'Settings Field'):
            # pass is needed, in case the template does not evaluare anything
            pass
            self.soapy_source_0.set_gain(0,rf_gain)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_c(
            2048, #size
            firdes.WIN_HAMMING, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            1 #number of inputs
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.05)
        self.qtgui_waterfall_sink_x_0.enable_grid(False)
        self.qtgui_waterfall_sink_x_0.enable_axis_labels(True)



        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_0.set_intensity_range(-120, 0)

        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_waterfall_sink_x_0_win)
        self.freq_xlating_fft_filter_ccc_0_0 = filter.freq_xlating_fft_filter_ccc(4, xlate_taps, 25000, samp_rate)
        self.freq_xlating_fft_filter_ccc_0_0.set_nthreads(1)
        self.freq_xlating_fft_filter_ccc_0_0.declare_sample_delay(0)
        self.freq_xlating_fft_filter_ccc_0 = filter.freq_xlating_fft_filter_ccc(4, xlate_taps, -25000, samp_rate)
        self.freq_xlating_fft_filter_ccc_0.set_nthreads(1)
        self.freq_xlating_fft_filter_ccc_0.declare_sample_delay(0)
        self.blocks_udp_sink_0 = blocks.udp_sink(gr.sizeof_short*1, '127.0.0.1', 7355, 1400, True)
        self.blocks_interleave_0 = blocks.interleave(gr.sizeof_short*1, 1)
        self.blocks_float_to_short_0_0 = blocks.float_to_short(1, 65536)
        self.blocks_float_to_short_0 = blocks.float_to_short(1, 65536)
        self.analog_quadrature_demod_cf_0_0 = analog.quadrature_demod_cf(.3)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(.3)
        self._ais_string_tool_bar = Qt.QToolBar(self)
        self._ais_string_tool_bar.addWidget(Qt.QLabel('AIS' + ": "))
        self._ais_string_line_edit = Qt.QLineEdit(str(self.ais_string))
        self._ais_string_tool_bar.addWidget(self._ais_string_line_edit)
        self._ais_string_line_edit.returnPressed.connect(
            lambda: self.set_ais_string(str(str(self._ais_string_line_edit.text()))))
        self.top_grid_layout.addWidget(self._ais_string_tool_bar)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.blocks_float_to_short_0_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0_0, 0), (self.blocks_float_to_short_0, 0))
        self.connect((self.blocks_float_to_short_0, 0), (self.blocks_interleave_0, 1))
        self.connect((self.blocks_float_to_short_0_0, 0), (self.blocks_interleave_0, 0))
        self.connect((self.blocks_interleave_0, 0), (self.blocks_udp_sink_0, 0))
        self.connect((self.blocks_interleave_0, 0), (self.zeromq_push_sink_0, 0))
        self.connect((self.freq_xlating_fft_filter_ccc_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.freq_xlating_fft_filter_ccc_0_0, 0), (self.analog_quadrature_demod_cf_0_0, 0))
        self.connect((self.soapy_source_0, 0), (self.freq_xlating_fft_filter_ccc_0, 0))
        self.connect((self.soapy_source_0, 0), (self.freq_xlating_fft_filter_ccc_0_0, 0))
        self.connect((self.soapy_source_0, 0), (self.qtgui_waterfall_sink_x_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "AIS")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_xlate_taps(firdes.low_pass(1, self.samp_rate, 15000, 5000, firdes.WIN_HAMMING, 6.76))
        self.qtgui_waterfall_sink_x_0.set_frequency_range(0, self.samp_rate)

    def get_zmq_address(self):
        return self.zmq_address

    def set_zmq_address(self, zmq_address):
        self.zmq_address = zmq_address

    def get_xlate_taps(self):
        return self.xlate_taps

    def set_xlate_taps(self, xlate_taps):
        self.xlate_taps = xlate_taps
        self.freq_xlating_fft_filter_ccc_0.set_taps(self.xlate_taps)
        self.freq_xlating_fft_filter_ccc_0_0.set_taps(self.xlate_taps)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.soapy_source_0.set_gain(0, self.rf_gain)

    def get_ais_string(self):
        return self.ais_string

    def set_ais_string(self, ais_string):
        self.ais_string = ais_string
        Qt.QMetaObject.invokeMethod(self._ais_string_line_edit, "setText", Qt.Q_ARG("QString", str(self.ais_string)))





def main(top_block_cls=AIS, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
