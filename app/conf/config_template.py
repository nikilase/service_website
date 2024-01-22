from app.schema.services import Service

services_list = [
    Service.new_service("This Tool", "this_tool.service", True),
    Service.new_service("Motion Deamon", "motion.service", True),
    Service.new_service("SSH Deamon", "sshd.service", False),
    Service.new_service("Non Existent", "none", True)
]

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8010
SERVER_RELOAD = True

ADMIN_USER = {"UUID": "4313186b-2795-4b63-afb9-edf9b5342b29",
              "email": "user@example.com",
              "hashed_pw": "$2b$12$O/h0NrQva4BsL3vG.sxSDeSjpZhL5kAl5KdU/1oau0c7qohX5Whw2",
              "is_active": True,
              "is_superuser": True,
              "is_verified": True
              }