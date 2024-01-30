# Node Network Configuration

Create `NodeNetworkConfigurationPolicy` CRs for Node Network Configuration

## Assumptions

- The [commmon](../../../common/) CRs have been created

## Initialize

Switch to the "openstack" namespace.
```
oc project openstack
```
Change to the `nncp` directory within the `hci` directory.
```
cd architecture/examples/va/hci/nncp
```
Edit the [values.yaml](values.yaml) file to suit your environment.
```
vi values.yaml
```
Generate the control-plane and networking CRs.
```
kustomize build > nncp.yaml
```

## Create CRs
```
oc apply -f nncp.yaml
```

Wait for NNCPs to be available
```
oc wait nncp -l osp/nncm-config-type=standard --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=300s
```
