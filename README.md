# forms-online
A online forms program, designed to be deployed on SnapDeploy.
This runs in a docker container, exposing port 80.
SnapDeploy automatically handles the ports as long as they are configured in docker.
The Dockerfile **MUST** be updated to expose all new ports.
The / and /health routes must return 200 OK **OR** a html page.
