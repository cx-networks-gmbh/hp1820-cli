#!/usr/bin/python
# Copyright: 2025 Leo Künne <leo.kuenne@cx-networks.com>
from __future__ import (absolute_import, division, print_function)
import lib.cli
import sys
from lib.cli import SpanningTreeVersion
from lib.cli import SpanningTreeModes
from ansible.module_utils.basic import AnsibleModule
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: Spanning Tree Configuration on HP ProCurve Switches

short_description: Configure Spanning Tree on HPE 1820 

#  version_added: "2.4"

description:
    - "This module provides declarative management of VLANs on HPE 1820 switches."
    - "Known limitation: The switch does not clear the session which means it runs out of sessions after 5 runs?."
    - "Known limitation: No option to remove VLANs from the table exists yet."

options:
    port_vlans:
        description:
            - Port to VLANs mapping dict. See example for the structure.
        required: true
    remove_unused_vlans:
        description:
            - Remove all VLANs that are not used by any port. Note that --diff
              mode will be wrong when VLANs are added by port_vlans that were
              unused.
        default: true
    host:
        description:
            - Hostname of the switch.
        required: true
    username:
        description:
            - Username to login on the switch as.
        default: admin
    password:
        description:
            - Password to use for login.
        required: true

author:
    - Leo Künne (leo.kuenne@cx-networks.com)
'''

EXAMPLES = '''
- name: Ensure port 2 has two VLANs assigned and 3 none
  hp-procurve:
    port_vlans:
      '2':
        untagged: 2900
        tagged:
          - 295
      '3':
        untagged: null
        tagged: []
    host: '{{ inventory_hostname }}'
    username: '{{ hpe1820__username | d(omit) }}'
    password: '{{ hpe1820__password }}'
  delegate_to: 'localhost'

# The --diff output might look like this:
#
# --- before
# +++ after
# @@ -0,0 +1,3 @@
# +vlan_per_port('untagged', '2', 2900)
# +vlan_per_port('tagged', '2', 295)
# +vlan_per_port('exclude', '2', 2902)
'''

#  RETURN = '''
#  port_vlans:
#      description: All port VLANs of the switch after modifications.
#      type: dict
#  '''


sys.path.append('..')


def run_module():

    result = {
        'changed': False,
    }

    module = AnsibleModule(
        argument_spec=dict(
            secure=dict(type='bool', default=False),
            enabled=dict(type='bool', default=True),
            mode=dict(type='str', choices=[
                      'ieee_802_1d', 'ieee_802_1w'], default='ieee_802_1w'),
            priority=dict(type='int', default=32768),
            host=dict(required=True, type='str'),
            username=dict(type='str', default='admin'),
            password=dict(required=True, type='str', no_log=True),
        ),
        supports_check_mode=True,
    )

    secure = module.params['secure']
    mode = SpanningTreeVersion(module.params['mode'])
    priority = module.params['priority']
    username = module.params['username']
    password = module.params['password']
    host = module.params['host']

    enabled = module.params['enabled']
    if module.params['enabled'] is 'true':
        enabled = SpanningTreeModes.enabled
    else:
        enabled = SpanningTreeModes.disabled

    # Always try https first!
    if secure and lib.cli.Cli.testConnection('https', host):
        cli = lib.cli.Cli('https', host)
    else:
        if lib.cli.Cli.testConnection('http', host):
            cli = lib.cli.Cli('http', host)
        else:
            module.fail_json(
                msg="Error: Cannot connect to remote host through HTTP and HTTPS.", **result)

    cli.login(username, password)

    change_actions = cli.setSpanningTree(
        enabled, mode, priority)

    cli.logout()
    cli.close()

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
