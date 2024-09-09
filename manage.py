import subprocess
import argparse


ftdi_mapping = {
    'A': '1:5,1,1',
    'B': '1:5,1,2',
    'C': '1:5,1,3',
    'D': '1:5,2',
    'E': '1:5,3',
    'F': '1:5,4'
}


# Create a subparser with command "flash"
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='command')
flash_parser = subparsers.add_parser('flash')
restart_parser = subparsers.add_parser('restart')

# Add a required argument "-d" to the "flash" command
flash_parser.add_argument('--directory', '-d', type=str, required=True, help="firmware directory")
flash_parser.add_argument('--system', '-s', type=str, required=True, help="which system to flash (A or B or .. F or 'all' for all)")

restart_parser.add_argument('--system', '-s', type=str, required=True, help="which system to restart (A or B or .. F or 'all' for all)")

# Parse the command line arguments
args = parser.parse_args()

# Check if the "flash" command was given
if args.command == 'flash':
    # Access the value of the "-d" argument
    device = args.directory
    
    systems = []
    if args.system == 'all':
        systems = ftdi_mapping.keys()
    else:
        systems = [args.target]

    for system in systems:
        print("\n==> Flashing system ", system, f" with ftdi location {ftdi_mapping[system]}\n")
        ftdi_path = ftdi_mapping[system]
        subprocess.run([
            'artiq_flash', '-t', 'kasli', 
            '-I', f'ftdi_location {ftdi_path}', 
            '-d', args.directory, '--srcbuild', 
            'erase', 'gateware', 'bootloader', 'firmware', 'start'
        ])

elif args.command == 'restart':
    systems = []
    if args.system == 'all':
        systems = ftdi_mapping.keys()
    else:
        systems = [args.target]

    for system in systems:
        print("\n==> Restarting system ", system, f" with ftdi location {ftdi_mapping[system]}\n")
        ftdi_path = ftdi_mapping[system]
        subprocess.run([
            'artiq_flash', '-t', 'kasli', 
            '-I', f'ftdi_location {ftdi_path}', 
            'start'
        ])
