import logging
import yaml, os
from typing import List, Dict

class FolderScanner:
    def __init__(self, 
                 input_yaml_path: str, 
                 base_directory: str, 
                 output_text_path: str = 'file_list.txt'):
        """
        Initialize the folder scanner
        
        :param input_yaml_path: Path to YAML file with list of folders to scan
        :param base_directory: Base directory where folders are located
        :param output_text_path: Path to output text file with scanned files
        """
        # Setup logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.input_yaml_path = input_yaml_path
        self.base_directory = base_directory
        self.output_text_path = output_text_path
    
    def load_folders_from_yaml(self) -> List[str]:
        """
        Load list of folders to scan from input YAML
        
        :return: List of folder names
        """
        try:
            with open(self.input_yaml_path, 'r') as file:
                folders = yaml.safe_load(file)
                
            # Validate input is a list
            if not isinstance(folders, list):
                self.logger.error("YAML file must contain a list of folders")
                return []
            
            return folders
        
        except FileNotFoundError:
            self.logger.error(f"Input YAML file not found: {self.input_yaml_path}")
            return []
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML file: {e}")
            return []
    
    def scan_folder(self, folder_path: str) -> Dict[str, List[str]]:
        """
        Recursively scan a folder and collect file paths
        
        :param folder_path: Path to the folder to scan
        :return: Dictionary with folder name and file paths
        """
        file_list = []
        
        # Check if folder exists
        if not os.path.exists(folder_path):
            self.logger.warning(f"Folder does not exist: {folder_path}")
            return {}
        
        # Walk through directory
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Get full file path
                full_path = os.path.join(root, file)
                
                # Get relative path from base folder
                relative_path = os.path.relpath(full_path, folder_path)
                if not relative_path.startswith("."):
                    file_list.append(relative_path)
        
        return {
            'folder': os.path.basename(folder_path),
            'files': sorted(file_list)
        }
    
    def scan_all_folders(self) -> List[Dict[str, List[str]]]:
        """
        Scan all folders specified in the input YAML
        
        :return: List of scanned folder details
        """
        # Load folders from YAML
        folders = self.load_folders_from_yaml()
        
        # Store scanned results
        scanned_results = []
        
        # Scan each folder
        for folder in folders:
            # Construct full path
            full_folder_path = os.path.join(self.base_directory, folder)
            
            # Scan folder
            folder_scan_result = self.scan_folder(full_folder_path)
            
            if folder_scan_result:
                scanned_results.append(folder_scan_result)
                self.logger.info(f"Scanned folder: {folder}")
        
        return scanned_results
    
    def save_results_to_text(self, results: List[Dict[str, List[str]]]):
        """
        Save scan results to a text file
        
        :param results: Scanned folder results
        """
        try:
            with open(self.output_text_path, 'w') as file:
                for folder_result in results:
                    # Write folder name
                    file.write(f"{folder_result['folder']}:\n")
                    # file.write("-" * 40 + "\n")
                    
                    # Write files
                    for file_path in folder_result['files']:
                        file.write(f"- ../{folder_result['folder']}/{file_path}\n")
                    
                    # Add a blank line between folders
                    file.write("\n")
            
            self.logger.info(f"Scan results saved to: {self.output_text_path}")
        
        except IOError as e:
            self.logger.error(f"Error saving results to text file: {e}")
    
    def run_scan(self):
        """
        Main method to run folder scanning process
        """
        # Scan all folders
        scan_results = self.scan_all_folders()
        
        # Save results
        if scan_results:
            self.save_results_to_text(scan_results)
        else:
            self.logger.warning("No folders were scanned")

def main():
    # Example usage
    input_yaml = 'scan.yaml'
    base_directory = ''
    output_text = 'file_list.txt'
    
    # Create scanner
    scanner = FolderScanner(
        input_yaml_path=input_yaml, 
        base_directory=base_directory, 
        output_text_path=output_text
    )
    
    # Run scan
    scanner.run_scan()

if __name__ == "__main__":
    main()
