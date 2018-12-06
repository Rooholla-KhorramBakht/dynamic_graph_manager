# -*- coding: utf-8 -*-
# Copyright 2011, Florent Lamiraux, Thomas Moulard, JRL, CNRS/AIST
#
# This file is part of dynamic-graph.
# dynamic-graph is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# dynamic-graph is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Lesser Public License for more details.  You should have
# received a copy of the GNU Lesser General Public License along with
# dynamic-graph. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import rospy

from dynamic_graph import plug
from dynamic_graph.tracer_real_time import TracerRealTime
from dynamic_graph.tools import addTrace
from dynamic_graph_manager.ros import Ros

# Internal helper tool.
def matrixToTuple(M):
    tmp = M.tolist()
    res = []
    for i in tmp:
        res.append(tuple(i))
    return tuple(res)

class Robot(object):
    """
    This class instantiates a robot
    """

    init_pos = (0.0)
    init_vel = (0.0)
    init_acc = (0.0)

    """
    Tracer used to log data.
    """
    tracer = None

    """
    How much data will be logged.
    """
    tracerSize = 2**20

    """
    Automatically recomputed signals through the use
    of device.after.
    This list is maintained in order to clean the
    signal list device.after before exiting.
    """
    autoRecomputedSignals = []

    """
    Robot timestep
    """
    timeStep = 0.005

    def __init__(self, name, device = None, tracer = None):
        self.name = name
        self.device = device
        # Initialize tracer if necessary.
        if tracer:
            self.tracer = tracer
        self.initialize_tracer()

        # We trace by default all signals of the device.
        self.tracedSignals = {'device': []}
        self.device_signals_names = []
        for signal in self.device.signals():
          signal_name = signal.name.split('::')[-1]
          self.tracedSignals['device'].append(signal_name)
          self.device_signals_names.append(signal_name)

        # Device
        for s in self.tracedSignals['device']:
            self.add_trace(self.device.name, s)

        # Prepare potential ros import/export
        self.ros = Ros(self)
        self.device.after.addDownsampledSignal('rosPublish.trigger', 1)
        self.export_device_dg_to_ros()

    def __del__(self):
        if self.tracer:
            self.stop_tracer()

    def add_trace(self, entityName, signalName):
        if self.tracer:
            self.autoRecomputedSignals.append(
                '{0}.{1}'.format(entityName, signalName))
            addTrace(self, self.tracer, entityName, signalName)

    def initialize_tracer(self):
        """
        Initialize the tracer and by default dump the files in
         ~/.dynamic_graph/[date_time]/
        """
        if not self.tracer:
            self.tracer = TracerRealTime('trace')
            self.tracer.setBufferSize(self.tracerSize)
            try:
                log_dir = rospy.get_param("/dynamic_graph/log_dir")
            except:
                import os.path
                import time
                log_dir = os.path.join(os.path.expanduser("~"),
                                       ".dynamic_graph_manager",
                                       time.strftime("%Y_%m_%d_%H_%M_%S"))
            self.tracer.open(log_dir, 'dg_', '.dat')
            # Recompute trace.triger at each iteration to enable tracing.
            self.device.after.addSignal('{0}.triger'.format(self.tracer.name))

    def start_tracer(self):
        """
        Start the tracer if it has not already been stopped.
        """
        if self.tracer:
            self.tracer.start()

    def stop_tracer(self):
        """
        Stop and destroy tracer.
        """
        if self.tracer:
            self.tracer.dump()
            self.tracer.stop()
            self.tracer.close()
            self.tracer.clear()
            for s in self.autoRecomputedSignals:
                self.device.after.rmSignal(s)
            self.tracer = None

    def export_signal_to_ros(self, signal, topic_name=None):
        if topic_name is None:
            topic_name = signal.name

        self.ros.rosPublish.add ("vector", topic_name, "/dg__" + topic_name)
        plug(signal, self.ros.rosPublish.signal(topic_name))

    def export_device_dg_to_ros(self):
        """
        Import in ROS the signal from the dynamic graph device.
        """
        for sig_name in self.device_signals_names:
            self.export_signal_to_ros(
                    self.device.signal(sig_name), 'device__' + sig_name);


__all__ = ["Robot"]
