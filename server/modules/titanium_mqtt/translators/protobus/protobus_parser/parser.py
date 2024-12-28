import os

def write_proto_file(filepath: str, content: str) -> None:
    """
    Write content to a file.

    This function attempts to open the specified file in write mode and 
    writes the provided content to it. If the file cannot be opened or 
    written to, it raises an IOError.

    Args:
        filepath (str): The path to the file where content will be written.
        content (str): The content to write to the file.

    Raises:
        IOError: If the file cannot be opened or written to.
    """
    try:
        with open(filepath, 'w') as file:
            file.write(content)
    except IOError as e:
        raise IOError(f"Error writing to file '{filepath}': {e}")


def read_proto_file(filepath: str = None) -> str:
    """
    Read the contents of a Proto file.

    This function attempts to open and read the contents of the specified file.
    If the file cannot be found or opened, it raises an IOError.

    Args:
        filepath (str): The path to the file to read. Defaults to the 
                        nanopb.proto file.

    Returns:
        str: The contents of the file as a string.

    Raises:
        IOError: If the file cannot be opened or read.
    """
    try:
        if not filepath:
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(current_file_dir, "resources", "nanopb.proto")
        with open(filepath, 'r') as file:
            return file.read()
    except IOError as e:
        raise IOError(f"Error reading file '{filepath}': {e}")

def create_python_module(filepath: str, outputpath: str):
    """
    Create a Python module directory based on the given file path.

    This function creates a directory named after the file (without extension)
    in the output folder and copies resource files into it.

    Args:
        filepath (str): The path to the Python file being processed.

    Returns:
        str: The name of the created module (directory) without the extension.
    """
    filename = os.path.basename(filepath)
    filename_without_extension = os.path.splitext(filename)[0]
    
    source_dir = "/app/resources/"
    destination_dir = f"/app/output/{filename_without_extension}/"
    os.system("ls -lah && cd resources && ls -lah")
    if os.path.exists(source_dir) and os.listdir(source_dir):
        os.system(f"cp {source_dir}* {destination_dir}")
    else:
        print(f"No files to copy from {source_dir} or directory does not exist.")

    return filename_without_extension

def process_python_file(filepath: str, outputpath: str):
    """
    Process a Python file.

    This function reads the contents of the specified Python Proto file,
    modifies it, writes the modified content to a temporary file, and 
    generates a Python module based on the Proto definitions.

    Args:
        filepath (str): The path to the Python Proto file to process.

    Raises:
        IOError: If there are errors reading from or writing to files.
    """
    nanopb_file = read_proto_file()
    proto_file = read_proto_file(filepath).replace('syntax = "proto2";', '')
    
    temp_file = proto_file.replace('import "nanopb.proto";', nanopb_file)
    write_proto_file(os.path.join(outputpath, "titanium_tmp.proto"), temp_file)

    module_name = os.path.splitext(os.path.basename(filepath))[0]
    os.system(f"cd /app/tmp/ && protoc --python_out={outputpath}/{module_name} {outputpath}/titanium_tmp.proto")
    
def parse(filepath, outputpath):
    """
    Main function to execute the script.

    This function parses command-line arguments and directs processing
    to the appropriate function based on the specified file extension.
    """
    
    process_python_file(filepath, outputpath)
