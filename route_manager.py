import json
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, font
import os

class RouteManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Routing Table Manager")
        self.root.geometry("750x550")
        self.root.resizable(True, True)
        
        # Custom font
        self.title_font = font.Font(family="Arial", size=16, weight="bold")
        self.label_font = font.Font(family="Arial", size=11)
        self.button_font = font.Font(family="Arial", size=10)
        
        # Set background color and theme
        self.root.configure(bg="#f0f0f0")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=self.label_font)
        self.style.configure('TButton', font=self.button_font)
        self.style.configure('TCombobox', font=self.label_font)
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        self.title_label = tk.Label(self.main_frame, text="Routing Table Manager", font=self.title_font, bg="#f0f0f0", fg="#2c3e50")
        self.title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="w")
        
        # Left side - Route selection and details display
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 20))
        
        # Route selection
        ttk.Label(self.left_frame, text="Select Route:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.route_var = tk.StringVar()
        self.route_dropdown = ttk.Combobox(self.left_frame, textvariable=self.route_var, state="readonly", width=25)
        self.route_dropdown.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.route_dropdown.bind("<<ComboboxSelected>>", self.display_route_details)
        
        # Route details frame
        self.details_frame = ttk.LabelFrame(self.left_frame, text="Route Details", padding=10)
        self.details_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        
        # Route name
        ttk.Label(self.details_frame, text="Route Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(self.details_frame, textvariable=self.name_var, width=25)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        
        # IP address
        ttk.Label(self.details_frame, text="IP Address:").grid(row=1, column=0, sticky="w", pady=5)
        self.ip_var = tk.StringVar()
        self.ip_entry = ttk.Entry(self.details_frame, textvariable=self.ip_var, width=25)
        self.ip_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Subnet mask
        ttk.Label(self.details_frame, text="Subnet Mask:").grid(row=2, column=0, sticky="w", pady=5)
        self.mask_var = tk.StringVar()
        self.mask_entry = ttk.Entry(self.details_frame, textvariable=self.mask_var, width=25)
        self.mask_entry.grid(row=2, column=1, sticky="ew", pady=5)
        
        # Gateway
        ttk.Label(self.details_frame, text="Gateway:").grid(row=3, column=0, sticky="w", pady=5)
        self.gateway_var = tk.StringVar()
        self.gateway_entry = ttk.Entry(self.details_frame, textvariable=self.gateway_var, width=25)
        self.gateway_entry.grid(row=3, column=1, sticky="ew", pady=5)
        
        # Right side - Action buttons
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.grid(row=1, column=1, sticky="nsew")
        
        # Action buttons frame
        self.action_frame = ttk.LabelFrame(self.right_frame, text="Actions", padding=10)
        self.action_frame.pack(fill=tk.BOTH, expand=True)
        
        # Route management buttons
        self.save_button = ttk.Button(self.action_frame, text="Save Route", command=self.save_route)
        self.save_button.pack(fill=tk.X, pady=5)
        
        self.new_button = ttk.Button(self.action_frame, text="Add New Route", command=self.clear_form)
        self.new_button.pack(fill=tk.X, pady=5)
        
        self.delete_button = ttk.Button(self.action_frame, text="Delete Route", command=self.delete_route)
        self.delete_button.pack(fill=tk.X, pady=5)
        
        # Separator
        ttk.Separator(self.action_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Windows route actions
        self.add_windows_button = ttk.Button(self.action_frame, text="Add to Windows Routes", command=lambda: self.windows_route_action("add"))
        self.add_windows_button.pack(fill=tk.X, pady=5)
        
        self.delete_windows_button = ttk.Button(self.action_frame, text="Delete from Windows Routes", command=lambda: self.windows_route_action("delete"))
        self.delete_windows_button.pack(fill=tk.X, pady=5)
        
        # Console output frame
        self.console_frame = ttk.LabelFrame(self.main_frame, text="Console Output", padding=10)
        self.console_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        
        # Console output text widget
        self.console = tk.Text(self.console_frame, height=8, width=80, bg="#282c34", fg="#abb2bf", font=("Consolas", 10))
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=3)
        self.main_frame.columnconfigure(1, weight=2)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Load routes and initialize UI
        self.routes = self.load_routes_from_file("routes.json")
        self.update_route_dropdown()
    
    def log(self, message):
        """Log a message to the console widget with timestamp"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.console.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console.see(tk.END)
    
    def load_routes_from_file(self, file_path):
        """Load routes from JSON file"""
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            # If file doesn't exist, create a new routes structure
            self.log(f"File {file_path} not found. Creating new routes file.")
            routes = {"routes": {}}
            with open(file_path, "w") as file:
                json.dump(routes, file, indent=4)
            return routes
        except json.JSONDecodeError:
            self.log(f"Error reading {file_path}. Creating new routes file.")
            routes = {"routes": {}}
            with open(file_path, "w") as file:
                json.dump(routes, file, indent=4)
            return routes
    
    def save_routes_to_file(self, routes, file_path):
        """Save routes to JSON file"""
        with open(file_path, "w") as file:
            json.dump(routes, file, indent=4)
        self.log(f"Routes saved to {file_path}")
    
    def update_route_dropdown(self):
        """Update the route dropdown with current routes"""
        route_names = list(self.routes["routes"].keys())
        self.route_dropdown['values'] = route_names
        if route_names:
            self.route_dropdown.current(0)
            self.display_route_details(None)
    
    def display_route_details(self, event):
        """Display details of the selected route"""
        route_name = self.route_var.get()
        if not route_name:
            return
        
        details = self.routes["routes"].get(route_name, {})
        self.name_var.set(route_name)
        self.ip_var.set(details.get("ip", ""))
        self.mask_var.set(details.get("mask", ""))
        self.gateway_var.set(details.get("gateway", ""))
        
        self.log(f"Displaying details for route: {route_name}")
    
    def clear_form(self):
        """Clear the form for a new route"""
        self.name_var.set("")
        self.ip_var.set("")
        self.mask_var.set("")
        self.gateway_var.set("")
        self.log("Form cleared for new route entry")
    
    def save_route(self):
        """Save the current route details"""
        route_name = self.name_var.get().strip()
        ip = self.ip_var.get().strip()
        mask = self.mask_var.get().strip()
        gateway = self.gateway_var.get().strip()
        
        # Validate inputs
        if not all([route_name, ip, mask, gateway]):
            messagebox.showerror("Error", "All fields must be filled")
            return
        
        # Save the route
        self.routes["routes"][route_name] = {"ip": ip, "mask": mask, "gateway": gateway}
        self.save_routes_to_file(self.routes, "routes.json")
        
        # Update UI
        self.update_route_dropdown()
        self.route_var.set(route_name)
        
        self.log(f"Route {route_name} saved successfully")
        self.status_var.set(f"Route {route_name} saved")
    
    def delete_route(self):
        """Delete the current route"""
        route_name = self.route_var.get()
        if not route_name:
            messagebox.showerror("Error", "No route selected")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete route '{route_name}'?")
        if not confirm:
            return
        
        # Delete the route
        if route_name in self.routes["routes"]:
            del self.routes["routes"][route_name]
            self.save_routes_to_file(self.routes, "routes.json")
            
            # Update UI
            self.update_route_dropdown()
            self.clear_form()
            
            self.log(f"Route {route_name} deleted")
            self.status_var.set(f"Route {route_name} deleted")
        else:
            messagebox.showerror("Error", f"Route {route_name} not found")
    
    def windows_route_action(self, action):
        """Add or delete the current route from Windows routing table"""
        route_name = self.route_var.get()
        if not route_name:
            messagebox.showerror("Error", "No route selected")
            return
        
        details = self.routes["routes"].get(route_name, {})
        if not details:
            messagebox.showerror("Error", f"Route {route_name} details not found")
            return
        
        # Create the command
        if action == "add":
            command = f"route add {details['ip']} mask {details['mask']} {details['gateway']}"
            action_text = "Adding"
        else:  # delete
            command = f"route delete {details['ip']} mask {details['mask']} {details['gateway']}"
            action_text = "Deleting"
        
        # Check if we're running as admin
        admin_rights = self.check_admin()
        if not admin_rights:
            res = messagebox.askyesno("Admin Rights Required", 
                                     "This operation requires administrator privileges.\n\n"
                                     "Do you want to run the command using 'runas' to elevate permissions?")
            if res:
                # Create a batch file to run with elevated permissions
                self.create_and_run_batch(command)
            return
        
        # Execute the command
        self.log(f"{action_text} route in Windows: {command}")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"Command executed successfully: {command}")
                self.status_var.set(f"Route {action}ed in Windows")
            else:
                self.log(f"Error executing command: {result.stderr}")
                messagebox.showerror("Error", f"Failed to {action} route: {result.stderr}")
        except Exception as e:
            self.log(f"Exception executing command: {str(e)}")
            messagebox.showerror("Error", f"Exception: {str(e)}")
    
    def check_admin(self):
        """Check if the application is running with admin rights"""
        try:
            # This will fail if we don't have admin rights
            with open(os.path.join(os.environ["WINDIR"], "temp", "admin_check"), "w") as file:
                file.write("admin check")
            os.remove(os.path.join(os.environ["WINDIR"], "temp", "admin_check"))
            return True
        except:
            return False
    
    def create_and_run_batch(self, command):
        """Create and run a batch file with the given command using elevated privileges"""
        # Create a temporary batch file
        batch_path = os.path.join(os.environ["TEMP"], "route_command.bat")
        with open(batch_path, "w") as batch_file:
            batch_file.write(f"@echo off\n")
            batch_file.write(f"echo Executing: {command}\n")
            batch_file.write(f"{command}\n")
            batch_file.write("pause\n")
        
        # Run the batch file with elevated privileges
        try:
            subprocess.Popen(["runas", "/user:Administrator", batch_path])
            self.log(f"Created batch file and launched with elevated privileges")
        except Exception as e:
            self.log(f"Error launching elevated batch file: {str(e)}")
            messagebox.showerror("Error", f"Failed to execute with admin rights: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RouteManagerApp(root)
    root.mainloop()