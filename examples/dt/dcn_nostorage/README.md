# Distributed Compute Node (DCN) OpenStack Architecture (No Local Storage)

This is a collection of CR templates that represent a Red Hat OpenStack Services on OpenShift deployment that has the following characteristics:

- 3 master/worker combo-node OpenShift cluster
- 3-replica Galera database
- RabbitMQ
- Spine and leaf network architecture
- Network isolation
- OVN networking
- 9 compute nodes distributed across multiple DCN sites
- No local storage backend (ephemeral disks only)

## Considerations

1. These CRs are validated for the overall functionality of the OSP cloud deployed, but they nonetheless require customization for the particular environment in which they are utilized.  In this sense they are _templates_ meant to be consumed and tweaked to fit the specific constraints of the hardware available.

2. The CRs are applied against an OpenShift cluster in _stages_.  That is, there is an ordering in which each grouping of CRs is fed to the cluster.  It is _not_ a case of simply taking all CRs from all stages and applying them all at once.

3. [kustomize](https://kustomize.io/) is used to generate the control plane and dataplane CRs dynamically. The `control-plane/nncp/values.yaml` and `service-values.yaml` files must be updated to fit your environment. kustomize version 5 or newer required.

Additionally, the values yaml files can be reset and modified for each DCN site as needed.

## Stages

All stages must be executed in the order listed below. Everything is required unless otherwise indicated.

1. [Install the OpenStack K8S operators and their dependencies](../../common/)
2. [Configuring networking and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy the data plane](dataplane-pre-ceph.md)
