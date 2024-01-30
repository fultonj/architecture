# Configure networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `local-storage` should already exist.
- The [nncp](nncp) CRs should already be created

## Initialize

Switch to the "openstack" namespace.
```
oc project openstack
```
Change to the `hci` directory.
```
cd architecture/examples/va/hci
```
Edit the [values.yaml](values.yaml) file to suit your environment.
```
vi values.yaml
```
Generate the control-plane and networking CRs.
```
kustomize build > control-plane.yaml
```

## Create CRs
```
oc apply -f control-plane.yaml
```

Wait for control plane to be available
```
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```
