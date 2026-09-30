#!/usr/bin/env python3
"""AES-based file encryption/decryption utility with key management."""

from __future__ import annotations

import argparse
import base64
import getpass
import os
import stat
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

MAGIC = b"FSEC"
VERSION = 1
FLAG_PBKDF2 = 0x01
NONCE_SIZE = 12
TAG_SIZE = 16
DEFAULT_ITERATIONS = 200_000
CHUNK_SIZE = 64 * 1024


@dataclass
class KeyMaterial:
    key: bytes
    flag: int
    salt: bytes
    iterations: int


class EncryptionError(Exception):
    """Raised when encryption or decryption fails."""


def derive_key(password: str, salt: bytes, iterations: int = DEFAULT_ITERATIONS) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    return kdf.derive(password.encode("utf-8"))


def load_key_file(path: Path) -> bytes:
    if not path.exists():
        raise FileNotFoundError(f"Key file not found: {path}")
    data = path.read_text(encoding="utf-8").strip()
    try:
        key = base64.b64decode(data)
    except Exception as exc:  # pylint: disable=broad-except
        raise EncryptionError("Key file is not valid base64.") from exc
    if len(key) != 32:
        raise EncryptionError("Key file must contain a 32-byte key in base64 format.")
    return key


def save_key_file(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"Key file already exists: {path}")
    key = os.urandom(32)
    encoded = base64.b64encode(key).decode("ascii")
    path.write_text(encoded + "\n", encoding="utf-8")
    try:
        current_mode = stat.S_IMODE(os.stat(path).st_mode)
        if current_mode != 0o600:
            os.chmod(path, 0o600)
    except PermissionError:
        pass
    print(f"Key saved to {path}. Keep this file secure.")


def prompt_password(confirm: bool) -> str:
    password = getpass.getpass("Enter password: ")
    if confirm:
        confirm_pw = getpass.getpass("Confirm password: ")
        if password != confirm_pw:
            raise EncryptionError("Passwords do not match.")
    if not password:
        raise EncryptionError("Password cannot be empty.")
    return password


def resolve_key_material(
    *,
    password: Optional[str],
    password_file: Optional[Path],
    key_file: Optional[Path],
    for_encryption: bool,
) -> KeyMaterial:
    provided_methods = sum(bool(x) for x in (password, password_file, key_file))
    if provided_methods > 1:
        raise EncryptionError("Specify only one of --password, --password-file, or --key-file.")

    if key_file:
        key = load_key_file(key_file)
        return KeyMaterial(key=key, flag=0, salt=b"", iterations=0)

    if password_file:
        password = password_file.read_text(encoding="utf-8").strip()
    elif password is None:
        password = prompt_password(confirm=for_encryption)

    if not password:
        raise EncryptionError("Password must not be empty.")

    salt = os.urandom(16)
    key = derive_key(password, salt)
    return KeyMaterial(key=key, flag=FLAG_PBKDF2, salt=salt, iterations=DEFAULT_ITERATIONS)


def derive_key_for_decryption(
    *,
    flag: int,
    salt: bytes,
    iterations: int,
    password: Optional[str],
    password_file: Optional[Path],
    key_file: Optional[Path],
) -> bytes:
    if flag & FLAG_PBKDF2:
        if key_file is not None:
            raise EncryptionError("Encrypted file requires a password, not a raw key.")
        if password_file:
            password = password_file.read_text(encoding="utf-8").strip()
        elif password is None:
            password = prompt_password(confirm=False)
        if not password:
            raise EncryptionError("Password must not be empty.")
        return derive_key(password, salt, iterations)

    if key_file is None:
        raise EncryptionError("A key file is required to decrypt this file.")
    return load_key_file(key_file)


def display_progress(processed: int, total: int, prefix: str) -> None:
    if total <= 0:
        return
    percent = (processed / total) * 100
    sys.stderr.write(f"\r{prefix}: {percent:6.2f}%")
    sys.stderr.flush()


def encrypt_file(input_path: Path, output_path: Path, key_material: KeyMaterial) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    total_size = input_path.stat().st_size
    nonce = os.urandom(NONCE_SIZE)

    cipher = Cipher(algorithms.AES(key_material.key), modes.GCM(nonce))
    encryptor = cipher.encryptor()

    salt_len = len(key_material.salt)
    header = bytearray()
    header.extend(MAGIC)
    header.append(VERSION)
    header.append(key_material.flag)
    header.append(salt_len)
    header.extend(struct.pack(">I", key_material.iterations))
    header.extend(nonce)
    header.extend(key_material.salt)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    processed = 0
    with input_path.open("rb") as fin, output_path.open("wb") as fout:
        fout.write(header)
        while True:
            chunk = fin.read(CHUNK_SIZE)
            if not chunk:
                break
            processed += len(chunk)
            encrypted = encryptor.update(chunk)
            fout.write(encrypted)
            display_progress(processed, total_size, "Encrypting")
        fout.write(encryptor.finalize())
        fout.write(encryptor.tag)
    sys.stderr.write("\rEncrypting: 100.00%\n")


def decrypt_file(
    input_path: Path,
    output_path: Path,
    *,
    password: Optional[str],
    password_file: Optional[Path],
    key_file: Optional[Path],
) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Encrypted file not found: {input_path}")

    with input_path.open("rb") as fin:
        magic = fin.read(4)
        if magic != MAGIC:
            raise EncryptionError("Invalid file format or not encrypted by this tool.")
        version = fin.read(1)
        if not version or version[0] != VERSION:
            raise EncryptionError("Unsupported file version.")
        flag = fin.read(1)[0]
        salt_len = fin.read(1)[0]
        iterations = struct.unpack(">I", fin.read(4))[0]
        nonce = fin.read(NONCE_SIZE)
        salt = fin.read(salt_len)
        data_start = fin.tell()

        total_size = input_path.stat().st_size
        ciphertext_length = total_size - data_start - TAG_SIZE
        if ciphertext_length < 0:
            raise EncryptionError("Encrypted file is truncated.")

        fin.seek(-TAG_SIZE, os.SEEK_END)
        tag = fin.read(TAG_SIZE)
        fin.seek(data_start)

        key = derive_key_for_decryption(
            flag=flag,
            salt=salt,
            iterations=iterations,
            password=password,
            password_file=password_file,
            key_file=key_file,
        )

        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
        decryptor = cipher.decryptor()

        processed = 0
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("wb") as fout:
            remaining = ciphertext_length
            while remaining > 0:
                read_size = min(CHUNK_SIZE, remaining)
                chunk = fin.read(read_size)
                if not chunk:
                    raise EncryptionError("Unexpected end of file during decryption.")
                remaining -= len(chunk)
                processed += len(chunk)
                fout.write(decryptor.update(chunk))
                display_progress(processed, ciphertext_length, "Decrypting")
            fout.write(decryptor.finalize())
    sys.stderr.write("\rDecrypting: 100.00%\n")


def handle_generate_key(args: argparse.Namespace) -> None:
    save_key_file(Path(args.key_file))


def handle_encrypt(args: argparse.Namespace) -> None:
    key_material = resolve_key_material(
        password=args.password,
        password_file=Path(args.password_file) if args.password_file else None,
        key_file=Path(args.key_file) if args.key_file else None,
        for_encryption=True,
    )
    encrypt_file(Path(args.input), Path(args.output), key_material)
    print(f"Encrypted {args.input} -> {args.output}")


def handle_decrypt(args: argparse.Namespace) -> None:
    decrypt_file(
        Path(args.input),
        Path(args.output),
        password=args.password,
        password_file=Path(args.password_file) if args.password_file else None,
        key_file=Path(args.key_file) if args.key_file else None,
    )
    print(f"Decrypted {args.input} -> {args.output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AES file encryption/decryption utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    key_parser = subparsers.add_parser("generate-key", help="Generate a random key file")
    key_parser.add_argument("--key-file", required=True, help="Path to store the generated key (base64)")
    key_parser.set_defaults(func=handle_generate_key)

    def add_common_arguments(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--input", required=True, help="Input file path")
        subparser.add_argument("--output", required=True, help="Output file path")
        subparser.add_argument("--password", help="Password for key derivation")
        subparser.add_argument("--password-file", help="File containing password")
        subparser.add_argument("--key-file", help="Base64 encoded key file (32 bytes)")

    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt a file")
    add_common_arguments(encrypt_parser)
    encrypt_parser.set_defaults(func=handle_encrypt)

    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt a file")
    add_common_arguments(decrypt_parser)
    decrypt_parser.set_defaults(func=handle_decrypt)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except EncryptionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
