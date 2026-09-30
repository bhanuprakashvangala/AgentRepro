import os
import sys
from cryptography.fernet import Fernet
from tqdm import tqdm


def generate_key(key_file="encryption.key"):
    """
    Generates a new encryption key and saves it to a file.

    Args:
        key_file (str): The name of the key file.
    """
    key = Fernet.generate_key()
    with open(key_file, "wb") as f:
        f.write(key)
    print(f"Encryption key generated and saved to {key_file}")
    return key


def load_key(key_file="encryption.key"):
    """
    Loads the encryption key from a file.

    Args:
        key_file (str): The name of the key file.

    Returns:
        bytes: The encryption key.
    """
    try:
        with open(key_file, "rb") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Key file '{key_file}' not found.")
        sys.exit(1)


def encrypt_file(input_file, output_file, key_file="encryption.key"):
    """
    Encrypts a file using AES encryption.

    Args:
        input_file (str): Path to the file to encrypt.
        output_file (str): Path to save the encrypted file.
        key_file (str): Path to the encryption key file.
    """
    # Generate or load key
    if not os.path.exists(key_file):
        key = generate_key(key_file)
    else:
        key = load_key(key_file)
        print(f"Using existing key from {key_file}")

    fernet = Fernet(key)

    # Get file size for progress bar
    file_size = os.path.getsize(input_file)
    chunk_size = 1024 * 1024  # 1MB chunks

    print(f"Encrypting {input_file}...")

    with open(input_file, "rb") as f_in:
        with open(output_file, "wb") as f_out:
            with tqdm(total=file_size, unit='B', unit_scale=True) as pbar:
                while True:
                    chunk = f_in.read(chunk_size)
                    if not chunk:
                        break
                    encrypted_chunk = fernet.encrypt(chunk)
                    f_out.write(encrypted_chunk)
                    pbar.update(len(chunk))

    print(f"File encrypted successfully: {output_file}")


def decrypt_file(input_file, output_file, key_file="encryption.key"):
    """
    Decrypts a file using AES encryption.

    Args:
        input_file (str): Path to the encrypted file.
        output_file (str): Path to save the decrypted file.
        key_file (str): Path to the encryption key file.
    """
    key = load_key(key_file)
    fernet = Fernet(key)

    # Get file size for progress bar
    file_size = os.path.getsize(input_file)
    chunk_size = 1024 * 1024 + 57  # Encrypted chunk size (1MB + Fernet overhead)

    print(f"Decrypting {input_file}...")

    try:
        with open(input_file, "rb") as f_in:
            with open(output_file, "wb") as f_out:
                with tqdm(total=file_size, unit='B', unit_scale=True) as pbar:
                    while True:
                        encrypted_chunk = f_in.read(chunk_size)
                        if not encrypted_chunk:
                            break
                        try:
                            decrypted_chunk = fernet.decrypt(encrypted_chunk)
                            f_out.write(decrypted_chunk)
                        except Exception as e:
                            print(f"\nError: Failed to decrypt. Invalid key or corrupted file.")
                            os.remove(output_file)
                            sys.exit(1)
                        pbar.update(len(encrypted_chunk))

        print(f"File decrypted successfully: {output_file}")
    except Exception as e:
        print(f"Error during decryption: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 4:
        print("Usage:")
        print("  Encrypt: python file_encryptor.py encrypt <input_file> <output_file>")
        print("  Decrypt: python file_encryptor.py decrypt <encrypted_file> <output_file>")
        sys.exit(1)

    mode = sys.argv[1].lower()
    input_file = sys.argv[2]
    output_file = sys.argv[3]

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)

    if mode == "encrypt":
        encrypt_file(input_file, output_file)
    elif mode == "decrypt":
        decrypt_file(input_file, output_file)
    else:
        print(f"Error: Invalid mode '{mode}'. Use 'encrypt' or 'decrypt'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
