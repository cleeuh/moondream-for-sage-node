# moondream-for-sage-node
Moondream inferencing for arm based Sage Node using ONNX Runtime.

## Resource Allocation Chart

These are the recommended memory request for job submission

| Parameter      | Quantization | Recommended Memory |
|----------------|--------------|--------------------|
| 2B             | INT8         | 7Gi                |
| 2B             | INT4         | ---                |
| 0.5B           | INT8         | 3Gi                |
| 0.5B           | INT4         | ---                |


## Job Example

> [!NOTE]
> While this version will only use CPU based inferencing.  Disabling enforcement of resource.gpu: "true" may result in runtime errors.  Therefore it is recommened to run on an NX based compute unit instead of a RPI based unit.


```yaml
name: moondream-2-w0xx
plugins:
- name: moondream-2-w0xx
  pluginSpec:
    image: registry.sagecontinuum.org/chrislee/moondream-2:0.2.0
    args:
    - --dynamic-loading
    - --stream
    - bottom_camera
    - --caption
    - --point
    - smoke
    - --point
    - fire
    - --point
    - hazard
    - --query
    - Is there a fire?
    selector:
      resource.gpu: "true"
    resource:
      limit.cpu: "1"
      limit.memory: 3Gi
      request.cpu: "1"
      request.memory: 3Gi
    volume: {}
nodeTags: []
nodes:
  W097: null
scienceRules:
- 'schedule(moondream-2-w0xx): cronjob("moondream-2-w0xx", "*/30 * * * *")'
successCriteria: []
```
