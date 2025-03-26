# Distributed Zones OpenStack Architecture with HCI and Ceph

The Distributed Zones architecture has the following properties.

- Three zones:
  - zone A: ocp-master-0
  - zone B: ocp-master-1
  - zone C: ocp-master-2
- Each ocp-master is schedulable as a worker
- [Toplogy CRDs](https://github.com/openstack-k8s-operators/infra-operator/pull/325) are
  used to either spread pods accross zones or keep them within a zone.
- Self Node Remdiation and Node Health Checks
- Three 3-node HCI data plane nodes hosting Ceph and Nova compute
- OVN networking
- Network isolation over a single NIC

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

0. Production deployments should use three OCP nodes per zone for high
   availability, not one as in this example.

1. These CRs are validated for the overall functionality of the OSP cloud deployed, but they nonetheless require customization for the particular environment in which they are utilized.  In this sense they are _templates_ meant to be consumed and tweaked to fit the specific constraints of the hardware available.

2. The CRs are applied against an OpenShift cluster in _stages_.  That is, there is an ordering in which each grouping of CRs is fed to the cluster.  It is _not_ a case of simply taking all CRs from all stages and applying them all at once.

3. In stages 1 and 2 [kustomize](https://kustomize.io/) is used to genereate the control plane CRs dynamically. The `control-plane/nncp/values.yaml` file(s) must be updated to fit your environment. kustomize version 5 or newer required.

4. In stages 3 and 4 [kustomize](https://kustomize.io/) is used to generate the dataplane CRs dynamically. The `edpm-pre-ceph/values.yaml`, `values.yaml` and `service-values.yaml` files must be updated to fit your environment. kustomize version 5 or newer required.

5. Between stages 3 and 4, _it is assumed that the user installs Ceph on the 3 OSP compute nodes._  OpenStack K8S CRDs do not provide a way to install Ceph via any sort of combination of CRs.

Note: Steps 3 and 4, as well as the Ceph installation, must be completed for each site.

Additionally, the values yaml files can be reset and modified for each site as needed.

## Stages

All stages must be executed in the order listed below. Everything is required unless otherwise indicated.

1. [Install the OpenStack K8S operators and their dependencies](../../common/)
2. [Define Zones and Toplogies](topology/)
3. [Configure networking and deploy the OpenStack control plane](control-plane.md)
4. [Configure and deploy the initial data plane to prepare for Ceph installation](dataplane-pre-ceph.md)
5. [Update the control plane and finish deploying the data plane after Ceph has been installed](dataplane-post-ceph.md)
