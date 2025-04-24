# Distributed Zones with BGP and Ceph

This Deployed Topology (DT) is the same as [bgp-l3-xl](../bgp-l3-xl)
but it also has the following:

- Three zones:
  - zone A CoreOS: ocp-worker-0 ocp-worker-1 ocp-worker-2
  - zone B CoreOS: ocp-worker-3 ocp-worker-4 ocp-worker-5
  - zone C CoreOS: ocp-worker-6 ocp-worker-7 ocp-worker-8
  - zone A RHEL: r0-compute-0, r0-compute-1, r0-compute-2, r0-networker-0, ocp-master-0, ocp-worker-0, leaf-0, leaf-1
  - zone B RHEL: r1-compute-0, r1-compute-1, r1-compute-2, r1-networker-0, ocp-master-1, ocp-worker-1, leaf-2, leaf-3
  - zone C RHEL: r2-compute-0, r2-compute-1, r2-compute-2, r2-networker-0, ocp-master-2, ocp-worker-2, leaf-4, leaf-5
- [Toplogy CRDs](https://github.com/openstack-k8s-operators/infra-operator/pull/325) are
  used to either spread pods accross zones or keep them within a zone.
- Self Node Remdiation and Node Health Checks
- A Ceph cluster running in each zone on the compute nodes (HCI)

The CRs included within this DT should be applied on an environment
where EDPM and OCP nodes are connected through a spine/leaf
network. The BGP protocol should be enabled on those spine and leaf
routers. See [bgp-l3-xl](../bgp-l3-xl) for information about
the BGP Dynamic Routing configuration.

worker-9 is tained so that regular openstack workloads are not
scheduled on it. It is not included into any rack or zone. It
is not connected to any leaves, but to a router connected to
the spines. It exists for running tests from outside.

## Prerequisites

- Chapters 2 and 6 from
[Self Node Remdiation and Node Health Checks](https://docs.redhat.com/en/documentation/workload_availability_for_red_hat_openshift/24.4/html-single/remediation_fencing_and_maintenance)
have been completed so that when the Node Health Check (NHC) Operator
detects an unhealthy node, it creates a Self Node Remediation (SNR) CR
with the `Automatic` strategy (which will taint an unhealthy node so
that its pods are rescheduled).

- A storage class has been created. If [LVMS](https://docs.redhat.com/en/documentation/openshift_container_platform/4.16/html/storage/configuring-persistent-storage#persistent-storage-using-lvms)
is used, then if a node fails, the system does not allow the attached
volume to be mounted on a new node because it is already assigned to
the failed node. This prevents SNR from rescheduling pods with PVCs.

## Considerations

- See the "Considerations/Constraints" section of [bgp-l3-xl](../bgp-l3-xl)

- Between stages 8 and 9, _it is assumed that the user installs Ceph
  on each of the 3 OSP compute nodes per zone for a total of three
  separate Ceph clusters._  OpenStack K8S CRDs do not provide a way to
  install Ceph via any sort of combination of CRs.

- If an external Ceph cluster already exists in each zone, then the
  same stages can be followed though it is not necessary to include
  the `ceph-hci-pre` `OpenStackDataPlaneService`. An alternative set
  of CRs could also be created which merge the CRs from stages 6 and 9
  for the control plane and stages 8 and 9 for the data plane since it
  will be unnecessary to have separate stages in order to install Ceph.

## Stages

All stages must be executed in the order listed below. Everything is required unless otherwise indicated.

1. [Configure taints on the OCP worker](configure-taints.md)
2. [Disable RP filters on OCP nodes](disable-rp-filters.md)
3. [Install the OpenStack K8S operators and their dependencies](../../common/)
4. [Apply metallb customization required to run a speaker pod on the OCP tester node](metallb/)
5. [Define Zones and Toplogies](topology/)
6. [Configure networking and deploy the OpenStack control plane without a storage backend](control-plane.md)
7. [Create BGPConfiguration after control plane is deployed](bgp-configuration.md)
8. [Configure and deploy the initial data plane to prepare for Ceph installation](data-plane.md)
9. [Finish deploying the data plane after Ceph has been installed and update the control plane to use Ceph](post-ceph.md)
