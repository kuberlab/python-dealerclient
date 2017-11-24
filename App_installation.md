# How to install an Application using this CLI

**Note**: It is assumed you have been already configured CLI properly either using config file or environment variables.

* Search for needed chart in catalog (say, for **tensorflow**)

```
$ dealer catalog --type mlapp-v2 --search tensorflow
+------+--------------------+--------------------+----------+---------+----------------+
| ID   | Name               | Display name       | Type     | Version | Workspace      |
+------+--------------------+--------------------+----------+---------+----------------+
| 4611 | tensorflow         | tensorflow         | mlapp-v2 | 1.0.0   | kuberlab-demo  |
| 3172 | styles-transfer-v2 | styles-transfer-v2 | mlapp-v2 | 1.0.0   | kuberlab-demo  |
| 3175 | zappos             | zappos             | mlapp-v2 | 1.0.0   | kuberlab-demo  |
| 2722 | tensorflow-1       | ultrasound-v1      | mlapp-v2 | 1.0.0   | leonard-sheiba |
+------+--------------------+--------------------+----------+---------+----------------+
```
Exact name of needed chart is *tensorflow* which is located in workspace named *kuberlab-demo*.

* Download values.yaml of that chart:

```bash
$ dealer chart-values --workspace kuberlab-demo tensorflow > values.yaml
```

* See what we've got:

```bash
cat values.yaml
```

* Now, we have to adjust values.yaml to fit our requirements. First, need to choose cluster storage. See shared cluster list:

```
$ dealer shared-cluster-available-list
+-----+----------------+---------------+--------+
| ID  | Display name   | WorkspaceName | Active |
+-----+----------------+---------------+--------+
| 221 | testshare      | kuberlab-demo | True   |
| 381 | test-limits    | kuberlab-demo | True   |
| 401 | no-limits      | kuberlab-demo | True   |
+-----+----------------+---------------+--------+
```

* We will pick up the shared cluster without limits with ID *401*.

<mark>TODO: Add storage retrieving commands from cluster</mark>

* Adjust values.yaml so it uses chosen storage.
* See projects: 

```
$ dealer project-list --workspace kuberlab-demo
+------+----------+--------------+------------------------------------+-------------+
| ID   | Name     | Display name | Repository URL                     | Environment |
+------+----------+--------------+------------------------------------+-------------+
| 711  | demotest | demotest     | https://github.com/<redacted>      | master      |
+------+----------+--------------+------------------------------------+-------------+
```

* There is only project named *demotest*.
* Pass that together to command *app-install*:

```bash
dealer app-install --name tensorflow --chart-workspace kuberlab-demo --target-workspace kuberlab-demo \
   -app tensorflow-for-test --shared-cluster-id 401 --project demotest --values values.yaml
```

* Take a look what we've got:

```
dealer app-list --workspace kuberlab-demo
+-------------------------+-------------------------+---------+----------+---------------+----------+
| Name                    | Display name            | Enabled | Cluster  | Workspace     | Project  |
+-------------------------+-------------------------+---------+----------+---------------+----------+
| tensorflow-for-test     | tensorflow-for-test     | True    | minikube | kuberlab-demo | kuberlab |
+-------------------------+-------------------------+---------+----------+---------------+----------+

# See detailed info

$ dealer app-get --workspace kuberlab-demo tensorflow-for-test
+------------------------+---------------------+
| Field                  | Value               |
+------------------------+---------------------+
| Name                   | tensorflow-for-test |
| Display name           | tensorflow-for-test |
| Enabled                | True                |
| Cluster                | minikube            |
| Workspace              | kuberlab-demo       |
| Project                | kuberlab            |
| Description            | Tensoflow           |
| Environment            | shared              |
| Disable Reason         | <none>              |
| Global Cluster ID      | <none>              |
| Global Cluster Name    | <none>              |
| Project Display Name   | kuberlab            |
| Workspace Display Name | KuberLab Demo       |
| Shared Cluster ID      | 401                 |
| Shared Cluster Name    | no-limits           |
+------------------------+---------------------+

# See application status

$ dealer app-status-list --workspace kuberlab-demo tensorflow-for-test
+---------------------------------+---------+------+
| Name                            | Status  | Type |
+---------------------------------+---------+------+
| tensorflow-for-test-jupyter     | Running | UIX  |
| tensorflow-for-test-tensorboard | Running | UIX  |
+---------------------------------+---------+------+
```

* See available tasks in application config:

```
$ dealer app-config-task-list --workspace kuberlab-demo tensorflow-for-test
+--------------+
| Name         |
+--------------+
| prepare-data |
| standalone   |
| parallel     |
| export       |
| workflow     |
+--------------+
```

* Let's run the first task, wait and watch for completion: 

```
$ dealer app-task-run --workspace kuberlab-demo tensorflow-for-test prepare-data --wait --watch
<Task name=prepare-data build=1 status=Starting>
<Task name=prepare-data build=1 status=Pending>
+------------+-----------------------------+
| Field      | Value                       |
+------------+-----------------------------+
| App        | tensorflow-for-test         |
| Name       | prepare-data                |
| Build      | 1                           |
| Status     | Succeeded                   |
| Completed  | True                        |
| Exit error | 2017-11-24T14:15:00.094421Z |
| Start      | 2017-11-24T14:15:05.515258Z |
| Stop       | None                        |
+------------+-----------------------------+
```

* See the logs:

```
# Retrieve task list
$ dealer app-task-list --workspace kuberlab-demo tensorflow-for-test
+------------------------+---------------------------------------+-------+-----------+-----------+
| App                    | Name                                  | Build | Status    | Completed |
+------------------------+---------------------------------------+-------+-----------+-----------+
| 21-tensorflow-for-test | 21-tensorflow-for-test-prepare-data-1 | 1     | Succeeded | True      |
+------------------------+---------------------------------------+-------+-----------+-----------+

# Retrieve pod list
$ dealer app-task-pods --workspace kuberlab-demo tensorflow-for-test prepare-data 1
+---------------------------------------------+--------+
| Name                                        | Status |
+---------------------------------------------+--------+
| master                                      | N/A    |
| tensorflow-for-test-prepare-data-upload-1-0 | N/A    |
+---------------------------------------------+--------+

# Retrieve logs
$ dealer app-task-logs --workspace kuberlab-demo tensorflow-for-test prepare-data 1 tensorflow-for-test-prepare-data-upload-1-0
Uploading Data
Done!!!

```