#!/usr/bin/python
# Copyright: 2025 Leo Künne <leo.kuenne@cx-networks.com>
from __future__ import (absolute_import, division, print_function)
import lib.cli
import sys
from ansible.module_utils.basic import AnsibleModule
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: my_sample_module

short_description: Assign VLANs to ports on HPE 1820 web managed switches.

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
            port_vlans=dict(required=True, type='dict'),
            remove_unused_vlans=dict(type='bool', default=True),
            host=dict(required=True, type='str'),
            username=dict(type='str', default='admin'),
            password=dict(required=True, type='str', no_log=True),
        ),
        supports_check_mode=True,
    )

    secure = module.params['secure']
    port_vlans = module.params['port_vlans']
    remove_unused_vlans = module.params['remove_unused_vlans']
    host = module.params['host']
    username = module.params['username']
    password = module.params['password']

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

    change_actions = cli.ensure_interfaces_vlan_membership(
        port_vlans, dry_run=module.check_mode)

    if remove_unused_vlans:
        change_actions += cli.remove_unused_vlans(dry_run=module.check_mode)

    # This only slows it down. Could be made conditional if anybody has a valid use case for it.
    #  result['port_vlans'] = cli.get_interfaces_vlan_membership()

    if len(change_actions) > 0:
        result['changed'] = True
        result['diff'] = {
            'before': '',
            'after': '\n'.join([f"vlan_per_port{s}" for s in change_actions]) + '\n',
        }

    cli.logout()
    cli.close()

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
