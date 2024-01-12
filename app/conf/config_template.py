from main import Service

services_list = [
    Service.new_service("This Tool", "this_tool.service", True),
    Service.new_service("Motion Deamon", "motion.service", True),
    Service.new_service("SSH Deamon", "sshd.service", False),
    Service.new_service("Non Existent", "none", True)
]
