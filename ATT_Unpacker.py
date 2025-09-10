import os

Pak0_file = "Resource0.pak"
Pak1_file = "Resource1.pak"
Repack_0_file = "Resource0.ref"
Repack_1_file = "Resource1.ref"
Pak0_folder = "Pak0_Files"
Pak1_folder = "Pak1_Files"

signature_check = b'\x47\x52\x45\x53'

def Reader(file: str, repack_file: str, folder: str, sig_check: bytes):
    """This function handles file reading for pak files"""
    print(f"Starting unpack for {file}")
    try:
        if os.path.isfile(repack_file):
            os.remove(repack_file)
        # Open pak file and a ref file for storing metadata for repacking
        with open(file, "rb") as f1, open(repack_file, "ab") as f2:
            sig_read = f1.read(4) # Check if initial 4 bytes match signature

            # compares the 4 bytes read with signature
            if sig_read != sig_check:
                raise ValueError(f"Invalid signature in {file}: expected {sig_check}, got {sig_read}")
            
            unknown1 = f1.read(4)
            file_count = f1.read(4)

            # Adds initial metadata to the repack file
            f2.write(signature_check)
            f2.write(unknown1)
            f2.write(file_count)
            f2.close() # close since the repack file will be opened again in a separate function
            for i in range(0, int.from_bytes(file_count, "little")):
                filename_len = f1.read(0x80) # read raw filename
                filename_decode = filename_len.decode().strip('\x00') # remove null values from filename
                print(f"File: {i+1} unpacked") # print filename, good for showing user the progress
                combined_path = os.path.join(folder, filename_decode) # create a combined path for unpacking
                file_offset = int.from_bytes(f1.read(4), "little") # get the integer value for file offset
                file_size = int.from_bytes(f1.read(4), "little") # get integer file size for file data
                return_here = f1.tell() # used to return here for unpacking
                f1.seek(file_offset) # go to file data of the current file entry
                file_data = f1.read(file_size) # read file data equal to the file size
                Unpacker(combined_path, file_data) # call unpacker function
                Repacker(repack_file, filename_len, file_offset, file_size) # call repacker function
                f1.seek(return_here) # return to metadata section at next file metadata entry
        print(f"Finished unpacking {file}")
    except Exception as e:
        print(f"Error unpacking {file}: {e}")
        raise
            
def Unpacker(file: str, data: bytes):
    """This function handles file creation from unpacking the pak files"""
    try:
        with open(file, "wb") as f1:
            f1.write(data) # create the unpacked file in the unpacked folder
    except Exception as e:
        print(f"Error writing {file}: {e}")
        raise
        
def Repacker(file: str, raw_filename: bytes, offset: bytes, size: bytes):
    """This function handles creating metadata files for rebuilding the PAK files"""
    try:
        with open(file, "ab") as f1:
            f1.write(raw_filename) # add the current metadata entry's raw filename
            f1.write(offset.to_bytes(4, "little")) # add the original offset
            f1.write(size.to_bytes(4, "little")) # add the original size
    except Exception as e:
        print(f"Error writing metadata to {file}: {e}")
        raise
        
if __name__ == "__main__":
    try:
        os.makedirs(Pak0_folder, exist_ok = True) # create PAK0 unpack folder
        os.makedirs(Pak1_folder, exist_ok = True) # create PAK1 unpack folder

        Reader(Pak0_file, Repack_0_file, Pak0_folder, signature_check) # call Reader function for PAK0
        Reader(Pak1_file, Repack_1_file, Pak1_folder, signature_check) # call Reader function for PAK1
    except Exception as e:
        input(f"Script failed: {e}")
        sys.exit(1)
    input("Task finished, you may exit now.")
