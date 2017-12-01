#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import getopt
import getpass
import os
import sys
import logging
import ovirtsdk4 as sdk
import ovirtsdk4.types as types
from ovirtsdk4 import ConnectionBuilder

logging.basicConfig(level=logging.DEBUG, filename='example.log')

# This example will import a VM from an export domain using a
# target domain, the example assumes there is an exported vm in
# the export storage domain


def usage():
    prog_name = sys.argv[0]
    print('\n')
    print(prog_name)
    print('\t-l <url>, --url=<url>')
    print('\t-u <username>, --username=<username>')
    print('\t-c <cert_file>, --certfile=<cert_file path>')
    sys.exit(-1)

def process_opts():
    opts, args = getopt.getopt(args=sys.argv[1:],
                               shortopts='hl:u:c',
                               longopts=['url=', 'username=', 'certfile='])

    url = username = cert_file = None

    for opt, arg in opts:
        if opt == '-h':
            usage()
        elif opt in ('-l', '--url'):
            url = arg
        elif opt in ('-u', '--username'):
            username = arg
        elif opt in ('-c', '--certfile'):
            cert_file = arg
        else:
            print('Unknown parameter: %s' % opt)

    if url and username:
        return url, username, cert_file

    usage()

def process(api_url, username, password, cert_file):
    connection = ConnectionBuilder(
        url=api_url,
        username=username,
        password=password,
        ca_file=cert_file,
        # debug=True
    ).build()

    # Get storage domains service
    sds_service = connection.system_service().storage_domains_service()
    # Grab the first export domain
    export_sd = sds_service.list(search='name=export')[0]
    # Get the target storage domain, where the VM will be imported to
    target_sd = sds_service.list(search='name=data')[0]
    # Get the cluster service
    clusters_service = connection.system_service().clusters_service()
    # Find the cluster to be used for the import
    cluster = clusters_service.list(search='LabOvirt41')[0]
    # Get the storage domain VM service
    vms_service = sds_service \
        .storage_domain_service(export_sd.id) \
        .vms_service()

    # Get an All exported VM, assuming we have at least one
    if vms_service.list():
#        exported_vm = vms_service.list()[0]
        exported_vm = vms_service.list()
        print(vms_service.list())
        # Import the VM that was exported to the export storage domain and import it to
        # the target storage domain which in our case is 'mydata' on the cluster
        # 'mycluster'
        for exported_vm.list in exported_vm:
            vms_service.vm_service(exported_vm.list.id).import_(
                storage_domain=types.StorageDomain(
                   id=target_sd.id

                ),
                cluster=types.Cluster(
                    id=cluster.id
                ),
                vm=types.Vm(
                    id=exported_vm.list.id
                )
            )
    else:
        print("Warning: no vms to export")
    connection.close()


def get_password():
    password = os.getenv("OVIRT_PASSWORD")
    if not password:
        password = getpass.getpass("Please enter your password: ")
    return password

def main():
    api_url, username, cert_file = process_opts()

    password = get_password()

    process(api_url, username, password, cert_file)




if __name__ == '__main__':
    main()
