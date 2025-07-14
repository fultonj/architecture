# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `local-storage` should already exist.
- An infrastructure of spine/leaf routers exists, is properly connected to the
  OCP nodes and the routers are configured to support BGP.

## Initialize

Switch to the "openstack" namespace
```shell
oc project openstack
```
Change to the dz-storage/control-plane directory
```
cd architecture/examples/dt/dz-storage/control-plane
```
Edit the [networking/nncp/values.yaml](control-plane/networking/nncp/values.yaml) and
[service-values.yaml](control-plane/service-values.yaml) files to suit
your environment.
```shell
vi networking/nncp/values.yaml
vi service-values.yaml
```

## Apply node network configuration

Generate the node network configuration
```shell
kustomize build networking/nncp > nncp.yaml
```
Apply the NNCP CRs
```shell
oc apply -f nncp.yaml
```
Wait for NNCPs to be available
```shell
oc wait nncp -l osp/nncm-config-type=standard --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=300s
```

## Apply the remaining networking configuration

Generate the networking CRs.
```shell
kustomize build networking > networking.yaml
```
Apply the CRs
```shell
oc apply -f networking.yaml
```

## Create Storage Secrets

### Cinder

Edit the secrets in the `control-plane/` directory to store the credentials for Cinder to connect to the storage array in each zone.

```shell
vi cinder-volume-ontap-secrets-az0.yaml
vi cinder-volume-ontap-secrets-az1.yaml
vi cinder-volume-ontap-secrets-az2.yaml
```
The example below is for NetApp iSCSI.

```yaml
apiVersion: v1
kind: Secret
metadata:
  labels:
    component: cinder-volume
    service: cinder
  name: cinder-volume-ontap-secrets-az1
  namespace: openstack
stringData:
  cinder-volume-ontap-secrets-az1: |
    [ontap]
    netapp_login = <login>
    netapp_password = <password>
    netapp_vserver = <vserver>
    netapp_pool_name_search_pattern = (my_pool)
```

When the control-plane configuration is applied it will create the secrets with the provided values.

### Manila

Edit the secrets in the `control-plane/` directory to store the credentials for Manila to connect to the storage array in each zone.

```shell
vi manila-share-ontap-secrets-az0.yaml
vi manila-share-ontap-secrets-az1.yaml
vi manila-share-ontap-secrets-az2.yaml
```
The example below is for NetApp NFS.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: osp-secret-manila-az0
  namespace: openstack
stringData:
  netapp-secrets.conf: |
    [nfs_az0]
    netapp_server_hostname = 10.1.0.5
    netapp_login = <redacted>
    netapp_password = <redacted>
    netapp_vserver = vserver-rhos-0
```

When the control-plane configuration is applied it will create the secrets with the provided values.

## Apply control-plane configuration

Generate the control-plane CRs and their secrets:
```shell
kustomize build > control-plane.yaml
```
Apply the CRs
```shell
oc apply -f control-plane.yaml
```

Wait for control plane to be available
```shell
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```

