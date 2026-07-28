# Shared BGP DT fragments

This directory holds content shared by BGP deployment topologies
(`bgp_dt01`, and intended for `bgp_dt02` / `bgp_dt04_ipv6` / `bgp_dt05` / …).

## EDPM nodeset values

`edpm-compute/` and `edpm-networker/` are kustomization roots that emit the
shared `edpm-nodeset-values` ConfigMap (SSH placeholders, FRR/OVN ansible
defaults, `edpm_network_config_template`, networks list, and role services).

Each rack under `examples/dt/bgp_dt*/edpm/{computes,networkers}/rN/` keeps only
rack-specific data and merges it via a nested `values/` kustomization:

```text
edpm/computes/r0/
  kustomization.yaml          # components: dt/bgp/edpm/nodeset, resources: [values]
  values/
    kustomization.yaml        # resources: [bgp/common/edpm-compute], patches: [values.yaml]
    values.yaml               # hostname, IPs, BGP peers, NIC mapping only
```

### Why nested `values/`?

`lib/dataplane/nodeset` replacements read `edpm-nodeset-values` during component
accumulation. Parent-level patches on that ConfigMap run too late. Building the
merged ConfigMap in a child kustomization first avoids that ordering problem.

Do **not** put the shared ConfigMap inside `dt/bgp/edpm/nodeset` and patch it
from `examples/` — that pattern fails for the same reason.

### Adding a BGP DT variant (e.g. eBGP or EVPN)

1. Reuse `examples/dt/bgp/common/edpm-{compute,networker}` (do not copy the
   full ansible/template blocks).
2. Copy the slim `values/` overlay layout from `bgp_dt01` racks; change only
   inventory (IPs/peers) and any variant ansibleVars.
3. For small CR-level deltas (MetalLB ASN, neutron `service_plugins`, FRR EVPN
   flags), prefer JSON6902 patches on the built NodeSet / BGPPeer / control
   plane rather than forking the shared base.
4. Prove parity with:

   ```bash
   kustomize build examples/dt/bgp_dtNN/<stage> > /tmp/out.yaml
   # compare against your previous golden CRs
   ```

Automation stage paths stay under `examples/dt/bgp_dtNN/...`. Point
`src_file` at `values/values.yaml` (see `automation/vars/bgp_dt01.yaml`).

### Example: EVPN ansibleVars overlay (bgp_dt05-style)

Add keys in the rack `values/values.yaml` strategic-merge patch (they merge
into the shared `ansibleVars`):

```yaml
data:
  nodeset:
    ansible:
      ansibleVars:
        edpm_frr_bgp_asn: 65000
        edpm_frr_bgp_l2vpn: true
        edpm_frr_bgp_l2vpn_peers: []
        edpm_frr_bgp_l2vpn_uplink_activate: true
        edpm_frr_bgp_uplinks_scope: internal
        edpm_neutron_ovn_agent_agent_extensions: "metadata,ovn-evpn"
        edpm_neutron_ovn_agent_ovn_evpn_bgp_as: 65000
        edpm_neutron_ovn_agent_ovn_evpn_bgp_local_interface: br-bgp-0
        edpm_neutron_ovn_agent_ovn_evpn_child_vxlan_port: 60010
```

Removing base keys (e.g. `edpm_frr_ovn_vrf_learn`) is not possible with
strategic merge alone — use a JSON6902 patch on the built
`OpenStackDataPlaneNodeSet` after the nodeset component, or introduce a
variant base under `common/` if many keys diverge.
