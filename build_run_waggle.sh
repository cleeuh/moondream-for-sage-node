#!/bin/bash

BUILD_TAG=$(sudo pluginctl build .)
time sudo pluginctl run --name moondream-2-rapid-deploy --resource request.cpu=2,limit.cpu=2,request.memory=5Gi,limit.memory=5Gi "$BUILD_TAG" -- -stream bottom_camera

# time sudo pluginctl run --name moondream-2-rapid-deploy --resource request.cpu=2,limit.cpu=2,request.memory=5Gi,limit.memory=5Gi $(sudo pluginctl build .) -- -stream bottom_camera

# sudo pluginctl build . && time sudo pluginctl run --name moondream-2-rapid-deploy --resource request.cpu=2,limit.cpu=2,request.memory=5Gi,limit.memory=5Gi 10.31.81.1:5000/local/moondream-2-rapid-deploy -- -stream bottom_camera

# sudo pluginctl run --name moondream-05b-test registry.sagecontinuum.org/chrislee/moondream-0_5b:0.1.0 --resource request.cpu=1,limit.cpu=1,request.memory=3Gi,limit.memory=3Gi --selector resource.gpu=true -- --stream bottom_camera --caption --query "Is there a fire?"
