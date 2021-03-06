#
# Copyright (c) 2017 Juniper Networks, Inc. All rights reserved.
#

"""
Mesos network manager
"""
import gevent
import sys
import greenlet
from gevent.queue import Queue
import common.args as mesos_args
import common.logger as logger
from cfgm_common import vnc_cgitb
import vnc.vnc_mesos as vnc_mesos
import mesos.cni.cni_request_server as cni_server


class MesosNetworkManager(object):
    '''Starts all background process'''

    _mesos_network_manager = None

    def __init__(self, args=None, mesos_api_connected=False, queue=None):
        self.greenlets = []
        self.args = args
        if queue:
            self.queue = queue
        else:
            self.queue = Queue()

        #TODO: Sync DB with current state using mesos agent api

        self.logger = logger.MesosManagerLogger(args)
        self.cni_server = cni_server.MesosCniServer(args=self.args,
                                           logger=self.logger,
                                           queue=self.queue)
    # end __init__

    def start_tasks(self):
        self.logger.info("Starting all tasks.")
        self.greenlets.append(gevent.spawn(self.cni_server.start_server))
        #TODO: Add VNC server listener
        gevent.joinall(self.greenlets)
    # end start_tasks

    def run_mesos_manager(self):
        self.logger.info("Starting mesos manager.")
        self.vnc = vnc_mesos.VncMesos(self.args, self.logger, self.queue)


# end class MesosNetworkManager


def main(args_str=None, mesos_api_skip=False, event_queue=None):
    vnc_cgitb.enable(format='text')
    args = mesos_args.parse_args(args_str)
    mesos_nw_mgr = MesosNetworkManager(args, mesos_api_connected=mesos_api_skip,
                                       queue=event_queue)
    MesosNetworkManager._mesos_network_manager = mesos_nw_mgr
    mesos_nw_mgr.start_tasks()


if __name__ == '__main__':
    sys.exit(main())
