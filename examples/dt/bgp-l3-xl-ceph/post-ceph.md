# Update the control plane to use Ceph and complete the data plane deployment

## Assumptions

- The pre-Ceph [dataplane](data-plane.md) was already deployed and
  Ceph was manually installed on each nodeset in each zone afterwords

## Initialize

Switch to the "openstack" namespace
```
oc project openstack
```

## Update Control Plane

Update the control plane to use the three Ceph clusters.
```
cd architecture/examples/dt/bgp-l3-xl-ceph
```
Edit the [service-values.yaml](service-values.yaml) files to suit your
environment.
```
vi service-values.yaml
```
The edit should include changing the following services to use the
three Ceph clusters.

- Cinder
- Glance
- Manila

Also, add `extraMounts` so that the above services can access
the Ceph configuration. The following command will provide insight
into how this file differs from the deployed version of the
control-plane.
```
diff service-values.yaml control-plane/service-values.yaml
```
Generate and apply the post-Ceph control plane CR.
```
kustomize build > control-plane-post-ceph.yaml
oc apply -f control-plane-post-ceph.yaml
```
Wait for control plane to be available after updating
```
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```

### todo

The `oc wait osctlplane` will time out unless the `ceph-conf-files`
Secret is updated with real values for a real ceph cluster.

## Update Data Plane

Complete the deployment of the Compute and Networker nodes now that
Ceph has been deployed.

Change to the bgp-l3-xl-ceph post-ceph deployment directory
```
cd architecture/examples/dt/bgp-l3-xl-ceph/edpm-post-ceph/deployment/
```
Generate a dataplane deployment CRs
```
kustomize build computes > edpm-post-ceph-compute-deployment.yaml
kustomize build networkers > edpm-post-ceph-networkers-deployment.yaml
```

## Apply the deployment

Start the deployment
```
oc apply -f edpm-post-ceph-compute-deployment.yaml
oc apply -f edpm-post-ceph-networkers-deployment.yaml
```
Wait for data plane deployments to finish
```
oc wait osdpd edpm-post-ceph-computes-deployment --for condition=Ready --timeout=2400s
oc wait osdpd edpm-post-ceph-networkers-deployment --for condition=Ready --timeout=2400s
```

### todo

The following will be needed.

```yaml
apiVersion: v1
data:
  03-ceph-nova.conf: CHANGEME_NOVA_CEPH_CONF
kind: ConfigMap
metadata:
  name: ceph-nova
  namespace: openstack
---
```

## Finalize Nova computes

Ask Nova to discover all compute hosts
```bash
oc rsh nova-cell0-conductor-0 nova-manage cell_v2 discover_hosts --verbose
```
(will the above discover nodes for all three cells?)

## Final OpenStackDataPlaneNodeSet services list

The `OpenStackDataPlaneNodeSet` must contain the full `services` list
so that during updates all required services are updated. Thus, the
pre-ceph and post-ceph deployments used a `servicesOverride` so that
only a subset of the services would be configured either before or
after Ceph was deployed. Any subsequent deployments should not pass a
`servicesOverride` unless necessary.
