# Shared BGP DT fragments

This directory holds content shared by BGP deployment topologies
(`bgp_dt01`, `bgp_dt05`, and intended for `bgp_dt02` / `bgp_dt04_ipv6` / …).

## EDPM nodeset values

Shared kustomization roots emit the `edpm-nodeset-values` ConfigMap (SSH
placeholders, FRR/OVN ansible defaults, `edpm_network_config_template`,
networks list, and role services):

| Base | Used by | Agent / services style |
| ---- | ------- | ---------------------- |
| `edpm-compute/` / `edpm-networker/` | `bgp_dt01` | `neutron-ovn` + ovn-bgp extension |
| `edpm-compute-evpn/` / `edpm-networker-evpn/` | `bgp_dt05` | `neutron-ovn` + ovn-evpn / L2VPN |

Each rack under `examples/dt/bgp_dt*/edpm/{computes,networkers}/rN/` keeps only
rack-specific data and merges it via a nested `values/` kustomization:

```text
edpm/computes/r0/
  kustomization.yaml          # components: dt/bgp/edpm/nodeset, resources: [values]
  values/
    kustomization.yaml        # resources: [bgp/common/<base>], patches: [values.yaml]
    values.yaml               # hostname, IPs, BGP peers, NIC mapping only
```

### Why nested `values/`?

`lib/dataplane/nodeset` replacements read `edpm-nodeset-values` during component
accumulation. Parent-level patches on that ConfigMap run too late. Building the
merged ConfigMap in a child kustomization first avoids that ordering problem.

Do **not** put the shared ConfigMap inside `dt/bgp/edpm/nodeset` and patch it
from `examples/` — that pattern fails for the same reason.

### Adding a BGP DT variant

1. Pick the matching shared base (or add a new one under `common/` when many
   keys diverge — strategic merge cannot delete base ansibleVars).
2. Copy the slim `values/` overlay layout from an existing BGP DT; change only
   inventory (IPs/peers) and any variant ansibleVars.
3. For small CR-level deltas (MetalLB ASN, neutron `service_plugins`), prefer
   editing the DT-local control-plane values rather than forking EDPM bases.
4. Prove parity with `kustomize build` against previous golden CRs.

Automation stage paths stay under `examples/dt/bgp_dtNN/...`. Point EDPM
nodeset `src_file` at `values/values.yaml` (see `automation/vars/bgp_dt01.yaml`
and `bgp_dt05.yaml`).
