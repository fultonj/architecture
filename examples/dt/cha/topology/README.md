# Define Zones and Toplogies

## Define Topologies

The `Topology` objects in this directory do not use kustomize and can
be created directly.

Switch to the "openstack" namespace
```
oc project openstack
```
Change to the topology directory
```
cd architecture/examples/dt/cha/topology
```
Create a toplogy for each zone.
```
oc create -f azone-node-affinity.yaml
oc create -f bzone-node-affinity.yaml
oc create -f czone-node-affinity.yaml
```
Create a toplogy which spreads pods across the zones.
```
oc create -f default-spread-pods.yaml
```

## Define Zones

The toplogies from the previous section assume that the OCP nodes have
been labeled with zones. An example command to create three zones for
seven nodes is below.

```
oc label nodes master-0 topology.kubernetes.io/zone=zoneA --overwrite
oc label nodes worker-0 topology.kubernetes.io/zone=zoneA --overwrite
oc label nodes worker-3 topology.kubernetes.io/zone=zoneA --overwrite

oc label nodes master-1 topology.kubernetes.io/zone=zoneB --overwrite
oc label nodes worker-1 topology.kubernetes.io/zone=zoneB --overwrite

oc label nodes master-2 topology.kubernetes.io/zone=zoneC --overwrite
oc label nodes worker-2 topology.kubernetes.io/zone=zoneC --overwrite
```

The
[Node labels section](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/#node-labels)
of the upstream Pod Topology Spread Constraints documentation
has more details. See also
[kubernetes/api/core/v1/well_known_labels.go](https://github.com/kubernetes/api/blob/master/core/v1/well_known_labels.go#L26).
