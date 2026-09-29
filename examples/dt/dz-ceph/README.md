# Distributed Zones with BGP and Ceph

This deployment topology is for testing only. It reuses the [dz-storage](../dz-storage)
network, networker, and VM definitions, but replaces the external storage arrays with
three independent single-node Ceph clusters.

Each rack assigns `r*-compute-0` to Nova and `r*-compute-1` to Ceph first. After
the Ceph cluster is configured, the post-Ceph deployment configures both hosts
as Nova computes. The Ceph hosts retain their existing VM names so the topology
can directly reuse the `dz-storage` infrastructure definitions. A production
deployment requires additional Ceph nodes for redundancy and normally has more
Nova computes per availability zone.

The automation in `automation/vars/dz-ceph.yaml` defines these phases:

1. Deploy the shared `dz-storage` networking and a pre-Ceph control plane
   with its storage-backed services disabled.
2. Create compute and networker data-plane NodeSets. Each compute NodeSet
   contains both compute VMs and prepares Ceph services on both.
3. Deploy one Ceph cluster per rack on each rack's `compute-1` host.
4. Reapply the control plane with the generated Ceph configuration and run
   the post-Ceph Nova compute node deployments.

## Shared configuration

This topology intentionally references the `dz-storage` networking, topology,
networker, and VM definitions instead of copying them. Customize the values in
`examples/dt/dz-storage` when directed by the deployment guides, but build the
compute NodeSets from the `dz-ceph` overlays. Each rack's NodeSet includes both
compute VMs, applies the shared EDPM services to both, and prepares Ceph
services on both. The Ceph deployment hook targets only `compute-1`; the
post-Ceph deployment configures Nova on both VMs.

The shared environment preparation is also documented by `dz-storage`:

- [Configure the tester-node taints](../dz-storage/configure-taints.md)
- [Disable reverse-path filtering](../dz-storage/disable-rp-filters.md)
- [Install the OpenStack K8S operators and their dependencies](../../common/)
- [Apply metallb customization required to run a speaker pod on the OCP tester node](metallb/)
- [Define zones and topologies](../dz-storage/topology/)
- [Create the BGPConfiguration](../dz-storage/bgp-configuration.md)

## Deployment stages

Run the stages in this order:

1. [Configure networking and deploy the pre-Ceph control plane](control-plane.md).
2. [Create the compute and networker NodeSets and run the initial EDPM
   deployment](data-plane.md).
3. Deploy Ceph in each Availability Zone
4. [Update the control plane for Ceph and finish the Nova
   deployments](post-ceph.md).
