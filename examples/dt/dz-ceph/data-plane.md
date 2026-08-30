# Prepare the data plane for Ceph

This stage creates one compute NodeSet per rack from the shared `dz-storage`
compute definitions. Each NodeSet contains both `compute-0` and `compute-1`,
with the same pre-Ceph services on both. The Ceph playbook targets only
`compute-1`; the post-Ceph stage configures Nova on both. The networker
NodeSets are used without modification.

During the pre-Ceph deployment, the combined compute NodeSet runs the same
services on both VMs, including `ceph-hci-pre`. `libvirt` and Nova are
configured for both nodes in the post-Ceph deployment.

Run the commands from the root of the `architecture` repository after the
[pre-Ceph control plane](control-plane.md) is ready.

```shell
oc project openstack
```

## Customize the shared NodeSet values

Edit the following shared compute values for the host names, addresses,
network configuration, and other environment-specific settings in each rack:

- `examples/dt/dz-storage/edpm/computes/r0/values.yaml`
- `examples/dt/dz-storage/edpm/computes/r1/values.yaml`
- `examples/dt/dz-storage/edpm/computes/r2/values.yaml`

Each file supplies values to the corresponding `dz-ceph` compute overlay. Keep
both `compute-0` and `compute-1` in these files; the Ceph playbook targets
`compute-1` by host name.

Edit the shared networker values as well:

- `examples/dt/dz-storage/edpm/networkers/r0/values.yaml`
- `examples/dt/dz-storage/edpm/networkers/r1/values.yaml`
- `examples/dt/dz-storage/edpm/networkers/r2/values.yaml`

The initial deployment membership is defined in
`examples/dt/dz-ceph/edpm/deployment/values.yaml`. Its default list includes
all three compute and networker NodeSets.

## Build and apply the compute NodeSets

### Disable the config drive

At this time it is only possible to migrate guests between distributed zones
if the guest does not have a config drive.

Each compute overlay sets `[DEFAULT] force_config_drive = false` in the
`nova-extra-config-azN` ConfigMap (`/etc/nova/nova.conf.d/25-nova-extra.conf`):
```
[DEFAULT]
force_config_drive = false
```
A config drive is an image that is stored in the availability zone that spawned
the instance, and a live migration does not move it to the destination zone. Thus,
an instance that has a config drive cannot be fully live migrated between zones.
Guests which need to migrate between zones should get their user-data and SSH keys
from a metadata service.

See [force_config_drive](https://docs.openstack.org/nova/latest/configuration/config.html#DEFAULT.force_config_drive)
and https://redhat.atlassian.net/browse/OSPRH-41009 for more information.

### Enable Cells per Zone (Optional)

By default, the `dz-ceph` compute overlays use one Nova cell across all three
availability zones. Each regional `neutron-ovn-azN` service is patched to
reference the global `nova-metadata-neutron-config` secret. The regional
`nova-custom-azN` service uses the cell-specific `nova-cell1-compute-config`
secret. Both are created by the single-cell control-plane overlay.

To deploy a separate Nova cell per availability zone, also remove the
`OpenStackDataPlaneService` patches for `neutron-ovn-azN` and
`nova-custom-azN` from each regional compute kustomization (e.g.
[edpm/computes/r0/kustomization.yaml](edpm/computes/r0/kustomization.yaml)
for `r0`, but also for `r1` and `r2`). The inherited `dz-storage` services then
reference the matching secrets: AZ0 uses cell1, AZ1 uses cell2, and AZ2 uses
cell3. Do this together with removing the `nova-single-cell.yaml` patch from
the pre-Ceph control-plane kustomization, as described in the [control-plane
guide](control-plane.md#enable-cells-per-zone-optional).

```shell
kustomize build examples/dt/dz-ceph/edpm/computes/r0 > edpm-r0-compute-nodeset.yaml
kustomize build examples/dt/dz-ceph/edpm/computes/r1 > edpm-r1-compute-nodeset.yaml
kustomize build examples/dt/dz-ceph/edpm/computes/r2 > edpm-r2-compute-nodeset.yaml

oc apply -f edpm-r0-compute-nodeset.yaml
oc apply -f edpm-r1-compute-nodeset.yaml
oc apply -f edpm-r2-compute-nodeset.yaml

oc -n openstack wait openstackdataplanenodeset r0-compute-nodes \
  --for condition=SetupReady --timeout=600s
oc -n openstack wait openstackdataplanenodeset r1-compute-nodes \
  --for condition=SetupReady --timeout=600s
oc -n openstack wait openstackdataplanenodeset r2-compute-nodes \
  --for condition=SetupReady --timeout=600s
```

## Build and apply the networker NodeSets

Because these NodeSets are shared unchanged, build them from `dz-storage`:

```shell
kustomize build examples/dt/dz-storage/edpm/networkers/r0 > edpm-r0-networker-nodeset.yaml
kustomize build examples/dt/dz-storage/edpm/networkers/r1 > edpm-r1-networker-nodeset.yaml
kustomize build examples/dt/dz-storage/edpm/networkers/r2 > edpm-r2-networker-nodeset.yaml

oc apply -f edpm-r0-networker-nodeset.yaml
oc apply -f edpm-r1-networker-nodeset.yaml
oc apply -f edpm-r2-networker-nodeset.yaml

oc -n openstack wait openstackdataplanenodeset r0-networker-nodes \
  --for condition=SetupReady --timeout=600s
oc -n openstack wait openstackdataplanenodeset r1-networker-nodes \
  --for condition=SetupReady --timeout=600s
oc -n openstack wait openstackdataplanenodeset r2-networker-nodes \
  --for condition=SetupReady --timeout=600s
```

## Run the initial EDPM deployment

```shell
kustomize build examples/dt/dz-ceph/edpm/deployment > edpm-deployment.yaml
oc apply -f edpm-deployment.yaml
oc -n openstack wait openstackdataplanedeployment edpm-deployment \
  --for condition=Ready \
  --timeout=180m
```

## Deploy the Ceph clusters

This is the boundary between the initial and post-Ceph stages.

A separate Ceph cluster needs to be deployed in each availability zone.

In a test environment, after the initial EDPM deployment, the ci-framework playbook
[ceph-multiple.yml](https://github.com/openstack-k8s-operators/ci-framework/blob/main/hooks/playbooks/ceph-multiple.yml)
could be used to deploy ceph on each `compute-1` host for three single-node
Ceph clusters.

The following files then need to be upated with the CephX identity and other
Ceph client configuration.

- `examples/dt/dz-ceph/control-plane/ceph-conf-files.yaml`
- `examples/dt/dz-ceph/control-plane/ceph-storage.yaml`
- `examples/dt/dz-ceph/edpm-post-ceph/nova-ceph/r0/values.yaml`
- `examples/dt/dz-ceph/edpm-post-ceph/nova-ceph/r1/values.yaml`
- `examples/dt/dz-ceph/edpm-post-ceph/nova-ceph/r2/values.yaml`

Do not proceed to the post-Ceph stage while these files still contain empty
client data or `CHANGE_TO_CEPH_FSID_*` placeholders.
