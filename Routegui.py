import json
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, font, filedialog, scrolledtext
import os
import uuid
import ipaddress
import socket
import threading
import datetime

class RouteManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Routing Table Manager")
        
        # Set minimum size 
        self.root.minsize(1000, 700)
        
        # Set initial window size and center it
        self.center_window(1200, 900)
        self.root.resizable(True, True)
        
        # Custom font
        self.title_font = font.Font(family="Segoe UI", size=18, weight="bold")
        self.label_font = font.Font(family="Segoe UI", size=11)
        self.button_font = font.Font(family="Segoe UI", size=10)
        self.console_font = font.Font(family="Consolas", size=10)
        self.info_font = font.Font(family="Segoe UI", size=10)
        
        # Set background color and theme
        bg_color = "#d9d9d9"
        self.root.configure(bg=bg_color)
        self.style = ttk.Style()
        if 'clam' in self.style.theme_names():
            self.style.theme_use('clam')
        
        # Configure theme styles
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', font=self.label_font, background=bg_color)
        self.style.configure('TLabelframe', background=bg_color)
        self.style.configure('TLabelframe.Label', font=self.label_font, background=bg_color)
        
        # Create menu bar
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)
        
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New Routes File", command=self.new_routes_file)
        self.file_menu.add_command(label="Open...", command=self.load_routes_dialog)
        self.file_menu.add_command(label="Save", command=lambda: self.save_routes_to_file(self.routes, self.routes_file))
        self.file_menu.add_command(label="Save As...", command=self.save_routes_dialog)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Add New Route", command=self.clear_form)
        self.edit_menu.add_command(label="Save Current Route", command=self.save_route)
        self.edit_menu.add_command(label="Delete Current Route", command=self.delete_route)
        
        # Route menu
        self.route_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Route", menu=self.route_menu)
        self.route_menu.add_command(label="Add to Windows Routes", command=lambda: self.windows_route_action("add"))
        self.route_menu.add_command(label="Delete from Windows Routes", command=lambda: self.windows_route_action("delete"))
        self.route_menu.add_command(label="Show Windows Routing Table", command=self.show_routing_table_options)
        self.route_menu.add_separator()
        self.route_menu.add_command(label="Validate Current Route", command=self.validate_route)
        self.route_menu.add_command(label="Calculate Subnet Information", command=self.recalculate_subnet_info)
        
        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)
        self.help_menu.add_command(label="Usage Guide", command=self.show_usage_guide)
        
        # Current file path display at the top
        self.file_frame = ttk.Frame(self.root)
        self.file_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.file_frame, text="Current File:").pack(side=tk.LEFT, padx=(0, 5))
        self.file_path_label = ttk.Label(self.file_frame, text="", foreground="#0000AA")
        self.file_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        self.title_label = tk.Label(self.main_frame, text="Routing Table Manager", 
                                  font=self.title_font, bg=bg_color)
        self.title_label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 10))
        
        # Upper section (form and network info)
        self.upper_frame = ttk.Frame(self.main_frame)
        self.upper_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left side - Route selection and details
        self.form_frame = ttk.Frame(self.upper_frame)
        self.form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Route selection
        self.selection_frame = ttk.Frame(self.form_frame)
        self.selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.selection_frame, text="Select Route:").pack(side=tk.LEFT)
        self.route_var = tk.StringVar()
        self.route_dropdown = ttk.Combobox(self.selection_frame, textvariable=self.route_var, 
                                         state="readonly", width=30)
        self.route_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.route_dropdown.bind("<<ComboboxSelected>>", self.display_route_details)
        
        # Route details frame
        self.details_frame = ttk.LabelFrame(self.form_frame, text="Route Details", padding=10)
        self.details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form grid for input fields
        self.form_grid = ttk.Frame(self.details_frame)
        self.form_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Route name
        ttk.Label(self.form_grid, text="Route Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(self.form_grid, textvariable=self.name_var)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=(5, 0))
        
        # IP address
        ttk.Label(self.form_grid, text="IP Address:").grid(row=1, column=0, sticky="w", pady=5)
        self.ip_var = tk.StringVar()
        self.ip_entry = ttk.Entry(self.form_grid, textvariable=self.ip_var)
        self.ip_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=(5, 0))
        self.ip_var.trace_add("write", lambda name, index, mode: self.validate_and_update_subnet_info())
        
        # Subnet mask
        ttk.Label(self.form_grid, text="Subnet Mask:").grid(row=2, column=0, sticky="w", pady=5)
        self.mask_var = tk.StringVar()
        self.mask_entry = ttk.Entry(self.form_grid, textvariable=self.mask_var)
        self.mask_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=(5, 0))
        self.mask_var.trace_add("write", lambda name, index, mode: self.validate_and_update_subnet_info())
        
        # Switch address (formerly Gateway)
        ttk.Label(self.form_grid, text="Switch Address:").grid(row=3, column=0, sticky="w", pady=5)
        self.gateway_var = tk.StringVar()
        self.gateway_entry = ttk.Entry(self.form_grid, textvariable=self.gateway_var)
        self.gateway_entry.grid(row=3, column=1, sticky="ew", pady=5, padx=(5, 0))
        self.gateway_var.trace_add("write", lambda name, index, mode: self.validate_gateway())
        
        # Configure form grid columns to expand
        self.form_grid.columnconfigure(1, weight=1)
        
        # Right side - Network Information
        self.network_frame = ttk.LabelFrame(self.upper_frame, text="Network Information", padding=10)
        self.network_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Network info display
        self.network_info = tk.Text(self.network_frame, height=7, width=45, 
                                  font=self.info_font, bg="#f0f0f0", bd=1, relief=tk.SOLID)
        self.network_info.pack(fill=tk.BOTH, expand=True)
        self.network_info.config(state=tk.DISABLED)
        
        # Console output frame (takes rest of the screen)
        self.console_frame = ttk.LabelFrame(self.main_frame, text="Console Output", padding=10)
        self.console_frame.pack(fill=tk.BOTH, expand=True)
        
        # Console output text widget with built-in scrollbar
        self.console = scrolledtext.ScrolledText(self.console_frame, height=20, 
                                              bg="#282c34", fg="#abb2bf", font=self.console_font)
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Load initial routes
        self.routes_file = "routes.json"
        self.routes = self.load_routes_from_file(self.routes_file)
        self.update_route_dropdown()
        
        # Update file path display
        self.update_file_path_display()
        
        # Update status bar with file information
        self.status_var.set(f"Routes loaded from {os.path.abspath(self.routes_file)}")
        
        # Initial log message
        self.log("Routing Table Manager started")
        
        # For tracking validation errors
        self.ip_error = False
        self.mask_error = False
        self.gateway_error = False
        self.route_ip_error = False
    
    def new_routes_file(self):
        """Create a new routes file"""
        # Ask user if they want to save current changes
        if len(self.routes.get("routes", {})) > 0:
            save = messagebox.askyesnocancel("Save Changes", 
                                          "Do you want to save the current routes before creating a new file?")
            if save is None:  # Cancel was clicked
                return
            if save:
                self.save_routes_to_file(self.routes, self.routes_file)
        
        # Create new routes structure
        self.routes = {"routes": {}}
        self.routes_file = "routes.json"  # Reset to default filename
        
        # Update UI
        self.update_route_dropdown()
        self.clear_form()
        self.update_file_path_display()
        
        self.log("Created new routes file")
        self.status_var.set("New routes file created")
    
    def validate_route(self):
        """Manually validate the current route"""
        route_name = self.name_var.get().strip()
        ip = self.ip_var.get().strip()
        mask = self.mask_var.get().strip()
        switch_addr = self.gateway_var.get().strip()
        
        if not all([route_name, ip, mask, switch_addr]):
            messagebox.showinfo("Validation", "Please fill all fields to validate the route.")
            return
        
        # Perform validation
        self.validate_and_update_subnet_info()
        self.validate_gateway()
        
        # Check results
        errors = []
        if self.ip_error:
            errors.append("- Invalid IP address format")
        if self.mask_error:
            errors.append("- Invalid subnet mask format")
        if self.gateway_error:
            errors.append("- Invalid Switch address format")
        
        warnings = []
        if self.route_ip_error:
            warnings.append("- The route IP is not set to the network address")
        
        # Show validation result
        if errors or warnings:
            message = "Validation Results:\n\n"
            if errors:
                message += "Errors:\n" + "\n".join(errors) + "\n\n"
            if warnings:
                message += "Warnings:\n" + "\n".join(warnings)
            messagebox.showwarning("Validation Results", message)
        else:
            messagebox.showinfo("Validation Results", "All fields are valid.")
    
    def recalculate_subnet_info(self):
        """Manually recalculate and display subnet information"""
        ip = self.ip_var.get().strip()
        mask = self.mask_var.get().strip()
        
        if not ip or not mask:
            messagebox.showinfo("Subnet Information", "Please enter IP address and subnet mask.")
            return
        
        self.validate_and_update_subnet_info()
        if self.ip_error or self.mask_error:
            messagebox.showerror("Error", "Invalid IP address or subnet mask format.")
            return
        
        self.log("Subnet information recalculated")
    
    def show_about(self):
        """Show the about dialog"""
        messagebox.showinfo("About Routing Table Manager", 
                         "Routing Table Manager\n\n"
                         "A tool for managing network routes.\n\n"
                         "This application allows you to create, save, and manage \n"
                         "network routes, and add them to the Windows routing table.")
    
    def show_usage_guide(self):
        """Show usage guide in the console"""
        usage_text = """
=== ROUTING TABLE MANAGER USAGE GUIDE ===

1. ROUTES
   - Select routes from the dropdown at the top left
   - View and edit route details in the form fields
   - Network information is displayed in the right panel

2. FILE MENU
   - New Routes File: Create a new empty routes file
   - Open: Load routes from a JSON file
   - Save: Save routes to the current file
   - Save As: Save routes to a new file

3. EDIT MENU
   - Add New Route: Clear the form to add a new route
   - Save Current Route: Save the current form data as a route
   - Delete Current Route: Remove the selected route

4. ROUTE MENU
   - Add to Windows Routes: Add the current route to the Windows routing table
   - Delete from Windows Routes: Remove the route from the Windows routing table
   - Show Windows Routing Table: Display the current system routing table
   - Validate Current Route: Check if the route details are valid
   - Calculate Subnet Information: Update the network information display

5. CONSOLE
   - View log messages and command outputs
   - See the full Windows routing table when requested
        """
        
        self.console.delete(1.0, tk.END)
        self.console.insert(tk.END, usage_text)
        self.log("Usage guide displayed in console")
    
    def update_file_path_display(self):
        """Update the file path display with the current file's absolute path"""
        file_path = os.path.abspath(self.routes_file)
        self.file_path_label.config(text=file_path)
    
    def center_window(self, width, height):
        """Center the window on the screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def log(self, message):
        """Log a message to the console widget with timestamp"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.console.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console.see(tk.END)
    
    def load_routes_from_file(self, file_path):
        """Load routes from JSON file"""
        try:
            with open(file_path, "r") as file:
                routes = json.load(file)
                self.log(f"Routes loaded from {file_path}")
                return routes
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
        except Exception as e:
            self.log(f"Unexpected error loading file: {str(e)}")
            messagebox.showerror("Error", f"Failed to load routes: {str(e)}")
            return {"routes": {}}
    
    def save_routes_to_file(self, routes, file_path):
        """Save routes to JSON file"""
        try:
            with open(file_path, "w") as file:
                json.dump(routes, file, indent=4)
            self.log(f"Routes saved to {file_path}")
            self.update_file_path_display()
            self.status_var.set(f"Routes saved to {os.path.abspath(file_path)}")
        except Exception as e:
            self.log(f"Error saving routes to {file_path}: {str(e)}")
            messagebox.showerror("Error", f"Failed to save routes: {str(e)}")
            
    def load_routes_dialog(self):
        """Open file dialog to load routes from user-selected file"""
        file_path = filedialog.askopenfilename(
            title="Load Routes",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.dirname(os.path.abspath(self.routes_file))
        )
        
        if file_path:
            try:
                self.routes = self.load_routes_from_file(file_path)
                self.routes_file = file_path
                self.update_route_dropdown()
                self.update_file_path_display()
                self.status_var.set(f"Routes loaded from {os.path.abspath(file_path)}")
            except Exception as e:
                self.log(f"Error loading routes from {file_path}: {str(e)}")
                messagebox.showerror("Error", f"Failed to load routes: {str(e)}")
    
    def save_routes_dialog(self):
        """Open file dialog to save routes to user-selected file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Routes",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.dirname(os.path.abspath(self.routes_file)),
            initialfile=os.path.basename(self.routes_file)
        )
        
        if file_path:
            try:
                self.save_routes_to_file(self.routes, file_path)
                self.routes_file = file_path
                self.update_file_path_display()
            except Exception as e:
                self.log(f"Error saving routes to {file_path}: {str(e)}")
                messagebox.showerror("Error", f"Failed to save routes: {str(e)}")
    
    def update_route_dropdown(self):
        """Update the route dropdown with current routes"""
        route_names = list(self.routes["routes"].keys())
        self.route_dropdown['values'] = route_names
        if route_names:
            self.route_dropdown.current(0)
            self.display_route_details(None)
        else:
            self.clear_form()
    
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
        
        # Validate and update subnet information
        self.validate_and_update_subnet_info()
        self.validate_gateway()
    
    def clear_form(self):
        """Clear the form for a new route"""
        self.name_var.set("")
        self.ip_var.set("")
        self.mask_var.set("")
        self.gateway_var.set("")
        self.log("Form cleared for new route entry")
        
        # Clear network info
        self.network_info.config(state=tk.NORMAL)
        self.network_info.delete(1.0, tk.END)
        self.network_info.config(state=tk.DISABLED)
        
        # Reset validation errors
        self.ip_error = False
        self.mask_error = False
        self.gateway_error = False
        self.route_ip_error = False
    
    def is_valid_ip(self, ip_str):
        """Check if the IP address is valid"""
        try:
            ipaddress.IPv4Address(ip_str)
            return True
        except ValueError:
            return False
    
    def is_valid_mask(self, mask_str):
        """Check if the subnet mask is valid"""
        try:
            # Check if it's a valid IP address first
            ip = ipaddress.IPv4Address(mask_str)
            
            # Convert to integer, then binary string, removing '0b' prefix
            binary = bin(int(ip))[2:].zfill(32)
            
            # Check if it's a contiguous sequence of 1's followed by 0's
            if '01' in binary:
                return False
            
            return True
        except ValueError:
            return False
    
    def get_network_info(self, ip_str, mask_str):
        """Calculate network information based on IP and mask"""
        try:
            # Create network objects
            ip = ipaddress.IPv4Address(ip_str)
            mask = ipaddress.IPv4Address(mask_str)
            
            # Calculate prefix length from subnet mask
            mask_binary = bin(int(mask))[2:].zfill(32)
            prefix_length = mask_binary.count('1')
            
            # Create network with prefix
            network = ipaddress.IPv4Network(f"{ip}/{prefix_length}", strict=False)
            
            # Calculate values
            network_address = network.network_address
            broadcast_address = network.broadcast_address
            first_host = network.network_address + 1
            last_host = network.broadcast_address - 1
            num_hosts = network.num_addresses - 2  # Subtract network and broadcast addresses
            
            # Check if the route IP is at the beginning of subnet range
            route_ip_correct = (ip == network_address)
            self.route_ip_error = not route_ip_correct
            
            return {
                "network_address": str(network_address),
                "broadcast": str(broadcast_address),
                "first_host": str(first_host),
                "last_host": str(last_host),
                "num_hosts": num_hosts,
                "prefix_length": prefix_length,
                "cidr": f"{network_address}/{prefix_length}",
                "route_ip_correct": route_ip_correct
            }
        except Exception as e:
            return None
    
    def validate_and_update_subnet_info(self):
        """Validate IP and mask, then update subnet information"""
        ip = self.ip_var.get().strip()
        mask = self.mask_var.get().strip()
        
        # Enable updating the text widget
        self.network_info.config(state=tk.NORMAL)
        self.network_info.delete(1.0, tk.END)
        
        # Check if both IP and mask are provided
        if not ip or not mask:
            self.network_info.insert(tk.END, "Enter IP address and subnet mask to see network information.")
            self.network_info.config(state=tk.DISABLED)
            return
        
        # Validate IP address
        if not self.is_valid_ip(ip):
            self.network_info.insert(tk.END, "ERROR: Invalid IP address format.\n")
            self.network_info.insert(tk.END, "IP address must be in format: xxx.xxx.xxx.xxx\n")
            self.network_info.insert(tk.END, "with each value between 0-255.")
            self.ip_error = True
            self.network_info.config(state=tk.DISABLED)
            return
        self.ip_error = False
        
        # Validate subnet mask
        if not self.is_valid_ip(mask):
            self.network_info.insert(tk.END, "ERROR: Invalid subnet mask format.\n")
            self.network_info.insert(tk.END, "Subnet mask must be in format: xxx.xxx.xxx.xxx\n")
            self.network_info.insert(tk.END, "with each value between 0-255.")
            self.mask_error = True
            self.network_info.config(state=tk.DISABLED)
            return
        elif not self.is_valid_mask(mask):
            self.network_info.insert(tk.END, "ERROR: Invalid subnet mask pattern.\n")
            self.network_info.insert(tk.END, "Subnet mask must be a valid mask like:\n")
            self.network_info.insert(tk.END, "255.255.255.0, 255.255.0.0, etc.")
            self.mask_error = True
            self.network_info.config(state=tk.DISABLED)
            return
        self.mask_error = False
        
        # Calculate network information
        info = self.get_network_info(ip, mask)
        if info:
            # Use a more compact display format
            self.network_info.insert(tk.END, f"Network Address: {info['network_address']}\n")
            self.network_info.insert(tk.END, f"Subnet Mask: {mask}\n")
            self.network_info.insert(tk.END, f"CIDR: {info['cidr']}\n")
            self.network_info.insert(tk.END, f"Broadcast: {info['broadcast']}\n")
            self.network_info.insert(tk.END, f"First Host: {info['first_host']}\n")
            self.network_info.insert(tk.END, f"Last Host: {info['last_host']}\n")
            self.network_info.insert(tk.END, f"Usable Hosts: {info['num_hosts']}\n\n")
            
            # Check if routing IP is at beginning of subnet range
            if not info['route_ip_correct']:
                self.network_info.insert(tk.END, "WARNING: Routing IP is not the network address!\n")
                self.network_info.insert(tk.END, f"For proper routing, IP should be: {info['network_address']}")
                self.route_ip_error = True
            else:
                self.network_info.insert(tk.END, "✓ Routing IP is correctly set to network address")
                self.route_ip_error = False
        else:
            self.network_info.insert(tk.END, "Error calculating network information.")
            
        # Disable editing the text widget
        self.network_info.config(state=tk.DISABLED)
    
    def validate_gateway(self):
        """Validate the switch address (formerly gateway)"""
        switch_addr = self.gateway_var.get().strip()
        
        # Skip validation if field is empty
        if not switch_addr:
            self.gateway_error = False
            return
        
        # Check if switch address is valid IP
        if not self.is_valid_ip(switch_addr):
            self.gateway_error = True
            self.log("ERROR: Invalid switch address IP format")
            return
        
        # Switch address is valid and doesn't need to be in the same subnet
        self.gateway_error = False
        
        # Remove any previous warnings about switch address
        self.network_info.config(state=tk.NORMAL)
        content = self.network_info.get("1.0", tk.END)
        
        # Remove any warning lines about switch addresses
        lines = content.split('\n')
        filtered_lines = [line for line in lines if "WARNING: Switch address" not in line]
        
        # Clear and rewrite content
        self.network_info.delete("1.0", tk.END)
        self.network_info.insert(tk.END, '\n'.join(filtered_lines))
        self.network_info.config(state=tk.DISABLED)
    
    def save_route(self):
        """Save the current route details with validation"""
        route_name = self.name_var.get().strip()
        ip = self.ip_var.get().strip()
        mask = self.mask_var.get().strip()
        switch_addr = self.gateway_var.get().strip()
        
        # Validate inputs
        if not all([route_name, ip, mask, switch_addr]):
            messagebox.showerror("Error", "All fields must be filled")
            return
        
        # Check for validation errors
        errors = []
        if self.ip_error:
            errors.append("- Invalid IP address format")
        if self.mask_error:
            errors.append("- Invalid subnet mask format")
        if self.gateway_error:
            errors.append("- Invalid Switch address format")
        
        # Warnings (can proceed but with warning)
        warnings = []
        if self.route_ip_error:
            warnings.append("The route IP is not set to the network address, which may cause routing issues.")
        
        # Show errors if any
        if errors:
            messagebox.showerror("Validation Errors", 
                              "Please correct the following errors before saving:\n\n" + 
                              "\n".join(errors))
            return
        
        # Show warnings if any, but allow saving
        if warnings:
            proceed = messagebox.askyesno("Warning", 
                                       "\n".join(warnings) + 
                                       "\n\nDo you want to save anyway?")
            if not proceed:
                return
        
        # Save the route
        self.routes["routes"][route_name] = {"ip": ip, "mask": mask, "gateway": switch_addr}
        self.save_routes_to_file(self.routes, self.routes_file)
        
        # Update UI
        self.update_route_dropdown()
        self.route_var.set(route_name)
        
        self.log(f"Route {route_name} saved successfully")
        self.status_var.set(f"Route {route_name} saved to {os.path.abspath(self.routes_file)}")
    
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
            self.save_routes_to_file(self.routes, self.routes_file)
            
            # Update UI
            self.update_route_dropdown()
            self.clear_form()
            
            self.log(f"Route {route_name} deleted")
            self.status_var.set(f"Route {route_name} deleted from {os.path.abspath(self.routes_file)}")
        else:
            messagebox.showerror("Error", f"Route {route_name} not found")
    
    def show_routing_table_options(self):
        """Show options for displaying the routing table"""
        # Create a custom dialog instead of using messagebox.askquestion with buttons
        result = messagebox.askyesno("Display Options", 
                                    "Would you like to view the routing table in the console?\n\n"
                                    "Yes - View in application console\n"
                                    "No - Open in a separate command window")
        
        if result:  # Yes was clicked - show in console
            self.print_windows_routing_table_to_console()
        else:  # No was clicked - show in separate window
            self.print_windows_routing_table_to_window()
    
    def print_windows_routing_table_to_console(self):
        """Show the current Windows routing table in the console widget"""
        self.log("Retrieving Windows routing table...")
        
        try:
            # Run the route print command and capture output
            process = subprocess.Popen(["route", "print"], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     universal_newlines=True,
                                     shell=True)
            
            # Use a separate thread to read output without blocking the UI
            def read_output():
                stdout, stderr = process.communicate()
                
                if stderr:
                    self.log(f"Error retrieving routing table: {stderr}")
                    return
                
                # Clear and update console with routing table
                self.console.delete(1.0, tk.END)
                self.console.insert(tk.END, "=== WINDOWS ROUTING TABLE ===\n\n")
                self.console.insert(tk.END, stdout)
                self.console.see(tk.END)
                
                self.log("Routing table displayed in console")
            
            # Start the thread
            threading.Thread(target=read_output, daemon=True).start()
            
        except Exception as e:
            self.log(f"Error showing routing table: {str(e)}")
            messagebox.showerror("Error", f"Failed to show routing table: {str(e)}")
    
    def print_windows_routing_table_to_window(self):
        """Show the current Windows routing table in a separate window"""
        # Create batch file to run route print
        batch_id = str(uuid.uuid4())[:8]
        batch_path = os.path.join(os.environ["TEMP"], f"route_print_{batch_id}.bat")
        
        with open(batch_path, "w") as batch_file:
            batch_file.write(f"@echo off\n")
            batch_file.write(f"echo =======================================\n")
            batch_file.write(f"echo Windows Routing Table\n")
            batch_file.write(f"echo =======================================\n")
            batch_file.write(f"echo.\n")
            batch_file.write(f"route print\n")
            batch_file.write(f"echo.\n")
            batch_file.write(f"echo Press any key to close this window...\n")
            batch_file.write("pause > nul\n")
            batch_file.write(f"del \"%~f0\"\n")  # Self-delete the batch file
        
        # Run the batch file
        try:
            subprocess.Popen(batch_path, shell=True)
            self.log(f"Showing Windows routing table in a separate window")
        except Exception as e:
            self.log(f"Error showing routing table: {str(e)}")
            messagebox.showerror("Error", f"Failed to show routing table: {str(e)}")
    
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
        
        # Check for validation errors before adding to Windows
        if action == "add" and (self.ip_error or self.mask_error or self.gateway_error):
            messagebox.showerror("Validation Error", 
                              "Cannot add route to Windows due to validation errors.\n"
                              "Please fix the errors first.")
            return
        
        # Warn if the route IP is not the network address
        if action == "add" and self.route_ip_error:
            proceed = messagebox.askyesno("Warning", 
                                       "The route IP is not set to the network address, which may cause routing issues.\n\n"
                                       "Do you want to continue anyway?")
            if not proceed:
                return
        
        # Create the command
        if action == "add":
            command = f"route add {details['ip']} mask {details['mask']} {details['gateway']}"
            action_text = "Adding"
        else:  # delete
            command = f"route delete {details['ip']} mask {details['mask']}"
            action_text = "Deleting"
        
        # Always use elevated command for route operations
        self.log(f"{action_text} route in Windows: {command}")
        self.create_and_run_batch(command)
        
        # Update status
        self.status_var.set(f"Command sent to {action.lower()} route - check console for results")
    
    def create_and_run_batch(self, command):
        """Create and run a batch file with the given command using elevated privileges"""
        # Create a temporary batch file with a unique name
        batch_id = str(uuid.uuid4())[:8]
        batch_path = os.path.join(os.environ["TEMP"], f"route_command_{batch_id}.bat")
        
        with open(batch_path, "w") as batch_file:
            batch_file.write(f"@echo off\n")
            batch_file.write(f"echo =======================================\n")
            batch_file.write(f"echo Routing Table Manager - Admin Command\n")
            batch_file.write(f"echo =======================================\n")
            batch_file.write(f"echo.\n")
            batch_file.write(f"echo Executing: {command}\n")
            batch_file.write(f"echo.\n")
            batch_file.write(f"{command}\n")
            batch_file.write(f"echo.\n")
            batch_file.write(f"echo Current Routing Table:\n")
            batch_file.write(f"route print\n")
            batch_file.write(f"echo.\n")
            batch_file.write(f"echo Press any key to close this window...\n")
            batch_file.write("pause > nul\n")
            batch_file.write(f"del \"%~f0\"\n")  # Self-delete the batch file
        
        # Run the batch file with elevated privileges using PowerShell
        powershell_command = f'powershell -Command "Start-Process -FilePath \'{batch_path}\' -Verb RunAs"'
        
        try:
            subprocess.Popen(powershell_command, shell=True)
            self.log(f"Created batch file and launched with elevated privileges")
            self.log(f"Check the admin command window for results")
        except Exception as e:
            self.log(f"Error launching elevated batch file: {str(e)}")
            messagebox.showerror("Error", f"Failed to execute with admin rights: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RouteManagerApp(root)
    root.mainloop()