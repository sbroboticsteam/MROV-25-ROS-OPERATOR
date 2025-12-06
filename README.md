# MROV-25-ROS-OPERATOR
MROV 2025 ROS port of the operator package
## Nodes
### ControllerPublisher
publishes direct controller inputs to the topic "controller_input".
Controller input is meant to be interpretted different in different contexts, so for processes like driving through teleop or autonomously, there should be a need for some intermediary node for computation/preprocessing.