# test-repo-pc4
# Proyecto 7: Observabilidad de clúster Kubernetes local (mini-monitoring)

## Setup

1. Construir la imagen Docker local:
   ```sh
   docker build -t timeserver:latest app
   ```
2. Verificar que Kubernetes esta activado:
   ```sh
   kubectl cluster-info
   ```
    Debe decir:
    ```sh
    Kubernetes control plane is running at https://kubernetes.docker.internal:6443
    CoreDNS is running at https://kubernetes.docker.internal:6443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

    To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
    ```

3. Desplegar pods:
   ```sh
   kubectl apply -f k8s/
   ```
4. Comprobar que Pods estan corriendo:
   ```sh
   kubectl get pods
   ```
5. Ir a un navegador y abrir:
    ```sh
    http://localhost:80
   ```
Se obtendra el tiempo actual en timezone UTC y Lima.


## Limpieza

Para borrar todo lo creado y liberar recursos:

1. Eliminar recursos en Kubernetes:
   ```sh
   kubectl delete -f k8s/
   ```

2. Eliminar la imagen (esperar unos segundos):
   ```sh
   docker image rm timeserver
   ```