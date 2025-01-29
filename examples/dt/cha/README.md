# DT for Campus HA Storage

- 3 zones:
  - zone A: ocp-master-0, ocp-worker-0, ocp-worker-3
  - zone B: ocp-master-1, ocp-worker-1
  - zone C: ocp-master-2, ocp-worker-2
- Each ocp-master is schedulable as a worker
- [Toplogy CRDs](https://github.com/openstack-k8s-operators/infra-operator/pull/325) are
  used to either spread pods accross zones or keep them within a zone.
- Self Node Remdiation and Node Health Checks
- 3 HCI data plane nodes hosting Ceph and Nova compute
- OVN networking
- Network isolation over a single NIC

## Prerequisites

- Chapters 2 and 6 from
[Self Node Remdiation and Node Health Checks](https://docs.redhat.com/en/documentation/workload_availability_for_red_hat_openshift/24.4/html-single/remediation_fencing_and_maintenance)
have been completed so that when the Node Health Check (NHC) Operator
detects an unhealthy node, it creates a Self Node Remediation (SNR) CR
with the `Automatic` strategy (which will taint an unhealthy node so
that its pods are rescheduled).

- A storage class has been created. As per the CSI [access modes](https://docs.openshift.com/container-platform/4.17/storage/understanding-persistent-storage.html#pv-access-modes_understanding-persistent-storage),
[LVMS](https://docs.redhat.com/en/documentation/openshift_container_platform/4.16/html/storage/configuring-persistent-storage#persistent-storage-using-lvms)
can only provide RWO volumes so "if a node fails, the system does not
allow the attached RWO volume to be mounted on a new node because it
is already assigned to the failed node." This prevents SNR from
rescheduling pods with PVCs.
[ODF](https://docs.openshift.com/container-platform/4.17/storage/persistent_storage/persistent-storage-ocs.html)
supports RWX so when a pod fails on a node it can be automatically
brought back on another node with the same persistent volume.

## Stages

- [Install the OpenStack K8S operators and their dependencies](../../common/)
- [Define Zones and Toplogies](topology/)
- [Configuring networking and deploy the OpenStack control plane](control-plane.md)
- [Configure and deploy the initial data plane to prepare for Ceph installation](dataplane-pre-ceph.md)
- [Update the control plane and finish deploying the data plane after Ceph has been installed](dataplane-post-ceph.md)
