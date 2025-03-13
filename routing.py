import json
import subprocess

routes = {
    "routes": {
        "RTU": {
            "ip": "172.168.14.102",
            "mask": "255.255.255.224",
            "gateway": "172.168.1.1"
        },
        "SERVER": {
            "ip": "192.168.1.5",
            "mask": "255.255.255.0",
            "gateway": "192.168.1.1"
        },
        "Default modem": {
            "ip": "192.168.1.1",
            "mask": "255.255.255.0",
            "gateway": "192.168.1.1"
        }
    }
}

def get_route_details(input):
    for route_name, details in routes["routes"].items():
        if route_name == input:
            return details
    return input + " not found"


def add_routes(routes):
    for route_name, details in routes["routes"].items():
        command = f"@echo route add {details['ip']} mask {details['mask']} {details['gateway']}"
        print(f"Executing: {command}")
        # Execute the command
        subprocess.run(command, shell=True)
        
def delete_routes(routes):
    for route_name, details in routes["routes"].items():
        command = f"@echo route delete {details['ip']} mask {details['mask']} {details['gateway']}"
        print(f"Executing: {command}")
        # Execute the command
        subprocess.run(command, shell=True)
        
def menu():
    print("1. Get route details")
    print("2. Add routes")
    print("3. Delete routes")
    print("4. Exit")
    return input("Enter your choice: ")

def main():

    while True:
        UserInput = input("Enter the route name: ") 
        print(get_route_details(UserInput))
        exit = input("Do you want to exit? (y/n): ")
        if exit == "y" or exit == "Y":
            break
        
    # Add routes
    add_routes(routes)

if __name__ == "__main__":
    main()