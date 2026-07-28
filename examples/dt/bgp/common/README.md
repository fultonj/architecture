# Shared BGP DT fragments

This directory holds content shared by BGP deployment topologies
(`bgp_dt01`, `bgp_dt02`, and intended for `bgp_dt04_ipv6` / `bgp_dt05` / …).

## EDPM nodeset values

Shared kustomization roots emit the `edpm-nodeset-values` ConfigMap (SSH
placeholders, FRR/OVN ansible defaults, `edpm_network_config_template`,
networks list, and role services):

| Base | Used by | Agent / services style |
| ---- | ------- | ---------------------- |
| `edpm-compute/` / `edpm-networker/` | `bgp_dt01` | `neutron-ovn` + ovn-bgp extension |
| `edpm-compute-bgp-agent/` / `edpm-networker-bgp-agent/` | `bgp_dt02` | `ovn-bgp-agent` + `neutron-metadata` |

Each rack under `examples/dt/bgp_dt*/edpm/{computes,networkers}/rN/` keeps only
rack-specific data and merges it via a nested `values/` kustomization:

```text
edpm/computes/r0/
  kustomization.yaml          # components: dt/bgp/edpm/nodeset, resources: [values]
  values/
    kustomization.yaml        # resources: [bgp/common/<base>], patches: [values.yaml]
    values.yaml               # hostname, IPs, BGP peers, NIC mapping (+ variant vars)
```

### Why nested `values/`?

`lib/dataplane/nodeset` replacements read `edpm-nodeset-values` during component
accumulation. Parent-level patches on that ConfigMap run too late. Building the
merged ConfigMap in a child kustomization first avoids that ordering problem.

Do **not** put the shared ConfigMap inside `dt/bgp/edpm/nodeset` and patch it
from `examples/` — that pattern fails for the same reason.

### Adding a BGP DT variant (e.g. eBGP or EVPN)

1. Pick the matching shared base (or add a new one under `common/` when many
   keys diverge — strategic merge cannot delete base ansibleVars).
2. Copy the slim `values/` overlay layout from an existing BGP DT; change only
   inventory (IPs/peers) and any variant ansibleVars.
3. For small CR-level deltas (MetalLB ASN, neutron `service_plugins`), prefer
   JSON6902 patches on the built CRs rather than forking the shared base.
4. Prove parity with `kustomize build` against previous golden CRs.

Automation stage paths stay under `examples/dt/bgp_dtNN/...`. Point EDPM
nodeset `src_file` at `values/values.yaml` (see `automation/vars/bgp_dt01.yaml`
and `bgp_dt02.yaml`).

### Example: eBGP ansibleVars overlay (`bgp_dt02` racks r1/r2)

```yaml
data:
  nodeset:
    ansible:
      ansibleVars:
        edpm_frr_bgp_asn: 64899
        edpm_frr_bgp_graceful_shutdown: false
        edpm_ovn_bgp_agent_bgp_as: 64899
        edpm_frr_bgp_uplinks_scope: external
        edpm_frr_bgp_neighbor_ttl_security_hops: 0
        edpm_network_config_os_net_config_mappings:
          edpm-r1-compute-0:
            nic2: 6a:fe:54:3f:8a:02  # CHANGEME
    nodes:
      edpm-r1-compute-0:
        # hostname, IPs, peers …
```
