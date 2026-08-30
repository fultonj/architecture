# Complete the deployment after Ceph

Run these commands from the root of the `architecture` repository:

```shell
oc project openstack
```

## Review the generated Ceph values

Confirm that `examples/dt/dz-ceph/control-plane/ceph-conf-files.yaml`
contains Ceph client configuration for `az0`, `az1`, and `az2`, and
that no `CHANGE_TO_CEPH_FSID_*` placeholder remains in these files:

- `examples/dt/dz-ceph/control-plane/ceph-storage.yaml`
- `examples/dt/dz-ceph/edpm-post-ceph/nova-ceph/r0/values.yaml`
- `examples/dt/dz-ceph/edpm-post-ceph/nova-ceph/r1/values.yaml`
- `examples/dt/dz-ceph/edpm-post-ceph/nova-ceph/r2/values.yaml`

The Nova values select the local Ceph configuration and Glance endpoint for
each rack. Edit them only if the generated cluster identity or endpoint differs
from the environment.

The post-Ceph deployment values select the NodeSet and service list for each
rack:

- `examples/dt/dz-ceph/edpm-post-ceph/deployment/r0/values.yaml`
- `examples/dt/dz-ceph/edpm-post-ceph/deployment/r1/values.yaml`
- `examples/dt/dz-ceph/edpm-post-ceph/deployment/r2/values.yaml`

The defaults deploy Nova on both the `compute-0` and `compute-1` hosts in each
rack. The `compute-1` nodes receive Nova after their Ceph configuration is
available. Adjust these files only if the NodeSet names or service lists have
been customized.

## Update the control plane to use Ceph

Build and apply the post-Ceph control-plane overlay. It enables the Ceph-backed
Cinder and Glance services and mounts the generated client configuration.

### Enable Cells per Zone (Optional)

The [post ceph control plane kustomization](control-plane/kustomization.yaml) includes
the [nova-single-cell.yaml](control-plane/pre-ceph/nova-single-cell.yaml) patch file in
the patches list. This results in all compute nodes being deployed in a single cell.
To deploy a separate Compute cell per availability zone, update the kustomization to
remove the nova-single-cell patch.

```shell
kustomize build examples/dt/dz-ceph/control-plane > control-plane-post-ceph.yaml
oc apply -f control-plane-post-ceph.yaml
oc -n openstack wait openstackcontrolplane controlplane \
  --for condition=Ready \
  --timeout=180m
```

## Complete the Nova deployment in each rack

Each deployment kustomization includes its rack's `nova-ceph` ConfigMap and
custom data-plane service. It targets the rack's compute NodeSet, which
contains both compute VMs. Build and apply the three deployments separately so
that each Nova compute uses the Ceph cluster in its own availability zone.

```shell
kustomize build examples/dt/dz-ceph/edpm-post-ceph/deployment/r0 > edpm-post-ceph-r0.yaml
kustomize build examples/dt/dz-ceph/edpm-post-ceph/deployment/r1 > edpm-post-ceph-r1.yaml
kustomize build examples/dt/dz-ceph/edpm-post-ceph/deployment/r2 > edpm-post-ceph-r2.yaml

oc apply -f edpm-post-ceph-r0.yaml
oc apply -f edpm-post-ceph-r1.yaml
oc apply -f edpm-post-ceph-r2.yaml

oc -n openstack wait openstackdataplanedeployment edpm-post-ceph-r0 \
  --for condition=Ready --timeout=180m
oc -n openstack wait openstackdataplanedeployment edpm-post-ceph-r1 \
  --for condition=Ready --timeout=180m
oc -n openstack wait openstackdataplanedeployment edpm-post-ceph-r2 \
  --for condition=Ready --timeout=180m
```
