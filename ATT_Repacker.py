import os, sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

Pak0_file = "Resource0.pak"
Pak1_file = "Resource1.pak"
Repack_0_file = "Resource0.ref"
Repack_1_file = "Resource1.ref"
Pak0_folder = "Pak0_Files"
Pak1_folder = "Pak1_Files"

signature_check = b'\x47\x52\x45\x53'

new_sizes = []  # Used for updating new sizes
new_offsets = []  # Used for updating new offsets to file data
files = []  # Used to store files to repack

def Reader(file: str, repack_file: str, folder: str):
    """Handles initial reading, writes first 12 bytes, then calls other functions."""
    print(f"Starting processing for {file}")
    files.clear()  # Clear files list at the start
    new_sizes.clear()  # Clear sizes list
    new_offsets.clear()  # Clear offsets list

    # If the new PAK file exists, remove it to start fresh
    if os.path.isfile(file):
        os.remove(file)

    try:
        with open(repack_file, "rb") as f2:
            initial_metadata = f2.read(8)  # Read 2 sets of 4-byte chunks
            file_count = f2.read(4)  # Read file count

            with open(file, "ab") as f1:
                f1.write(initial_metadata)  # Write initial metadata
                f1.write(file_count)  # Write file count

        # Read metadata from .ref file
        with open(repack_file, "rb") as f2:
            f2.seek(12)  # Skip initial 12 bytes
            for i in range(int.from_bytes(file_count, "little")):
                filename_len = f2.read(0x80)  # Read raw filename
                filename_decode = filename_len.decode().strip('\x00')  # Remove null bytes
                combined_path = os.path.join(folder, filename_decode)
                if not os.path.isfile(combined_path):
                    print(f"Warning: File {combined_path} does not exist!")
                    continue
                files.append(combined_path)
                file_offset = f2.read(4)  # Get old offset
                old_file_size = f2.read(4)  # Get old size
                Repack_metadata(file, filename_len, file_offset, old_file_size)

        # Repack file data
        for i, new_file in enumerate(files):
            print(f"Repacking data for: {new_file}")
            Repack_filedata(file, new_file)

        # Update metadata
        print(f"Updating metadata for {file}")
        Update_metadata(file, file_count)

    except Exception as e:
        print(f"Error processing {file}: {e}")
        raise

    print(f"Finished processing {file}")

def Repack_metadata(file: str, raw_filename: bytes, offset: bytes, size: bytes):
    """Handles adding metadata to the new PAK file."""
    try:
        with open(file, "ab") as f1:
            f1.write(raw_filename)  # Write filename
            f1.write(offset)  # Write original offset
            f1.write(size)  # Write original size
    except Exception as e:
        print(f"Error in Repack_metadata for {file}: {e}")
        raise

def Repack_filedata(file: str, new_file: str):
    """Handles repacking file data into new PAK files."""
    try:
        with open(file, "ab") as f1, open(new_file, "rb") as f2:
            current_offset = f1.tell()
            current_size = 0
            chunk_size = 64 * 1024  # 64KB chunks
            while chunk := f2.read(chunk_size):
                f1.write(chunk)
                current_size += len(chunk)
            new_sizes.append(current_size)
            new_offsets.append(current_offset)
    except Exception as e:
        print(f"Error in Repack_filedata for {new_file}: {e}")
        raise

def Update_metadata(file: str, filecount: bytes):
    """Updates offsets and sizes in metadata."""
    try:
        with open(file, "r+b") as f1:
            f1.seek(12)  # Skip to start of metadata
            for i in range(int.from_bytes(filecount, "little")):
                f1.read(0x80)  # Skip filename
                current_offset = new_offsets[i].to_bytes(4, "little")
                current_size = new_sizes[i].to_bytes(4, "little")
                f1.write(current_offset)
                f1.write(current_size)
    except Exception as e:
        print(f"Error in Update_metadata for {file}: {e}")
        raise

if __name__ == "__main__":
    try:
        Reader(Pak0_file, Repack_0_file, Pak0_folder)  # Process PAK0
        Reader(Pak1_file, Repack_1_file, Pak1_folder)  # Process PAK1
        print("Task finished successfully.")
    except Exception as e:
        input(f"Script failed: {e}")
        sys.exit(1)
    input("Press Enter to exit.")


