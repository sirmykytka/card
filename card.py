import struct
from pathlib import Path


class Card:
    """
    A custom binary container for images with metadata.

    The .card file bundles an image with its original extension and metadata
    (tags, source, description, etc.) into a single self-contained file.

    Structure (all integers are big-endian):

    Header (16 bytes):
      [0..3]   Signature   "CARD"
      [4]      Version     1 (for future extensions)
      [5]      Ext len     Length of original extension (e.g., 4 for ".png")
      [6..9]   Meta len    Length of metadata (e.g., 12 for "Hello world!")
      [10..15]  Reserved    Zero-filled (for future use)

    After header (variable):
      [16..]   Extension   Original extension (e.g., ".png")
      [...]    Metadata    Custom metadata (e.g., JSON or plain text)
      [...]    Image data  Original image bytes (remaining content)
    """

    SIGNATURE = b"CARD"
    VERSION = 1

    SIGNATURE_BYTES = 4
    VERSION_BYTES = 1
    EXTENSION_BYTES = 1
    METADATA_BYTES = 4
    RESERVED_BYTES = 6
    HEADER_BYTES = 16

    @staticmethod
    def pack(file_path: str) -> None:
        file = Path(file_path)
        parent = file.parent
        name = file.stem
        extension = file.suffix

        if extension == ".card":
            raise Exception('This file is already a Card!')

        with open(file_path, 'rb+') as f:
            file_bytes = f.read()

            # Check the signature
            signature = file_bytes[0:4]
            if signature == b'CARD':
                raise Exception('This file was already Card-ed!')

            card_bytes = bytes()

            # Struct of header
            card_bytes += struct.pack('@4s', Card.SIGNATURE)
            card_bytes += struct.pack('>B', Card.VERSION)
            card_bytes += struct.pack('>B', len(extension))
            card_bytes += struct.pack('>I', len(name))
            card_bytes += struct.pack(
                f'@{Card.RESERVED_BYTES}s',
                b'X' * Card.RESERVED_BYTES
            )

            # Data
            card_bytes += extension.encode('ascii')
            card_bytes += name.encode('ascii')

            # Files bytes
            card_bytes += file_bytes

        with open(parent / (name + '.card'), 'wb') as f:
            f.write(card_bytes)

    @staticmethod
    def unpack(file_path: str) -> None:
        file = Path(file_path)
        parent = file.parent
        name = file.stem
        extension = file.suffix

        if extension != ".card":
            raise Exception('This file is not a Card!')

        with open(file_path, 'rb+') as p:
            card_bytes = p.read()

            header_bytes = card_bytes[0:Card.HEADER_BYTES - 1]
            header = ' '.join(f'{b:02X}' for b in header_bytes)
            print(header)

            pointer = 0

            # Extension signature
            signature = header_bytes[pointer:Card.SIGNATURE_BYTES]
            if signature != b'CARD':
                raise Exception('This file was not Card-ed!')

            print('Signature:', signature)

            pointer += Card.SIGNATURE_BYTES

            # Version
            version_bytes = header_bytes[pointer:pointer+Card.VERSION_BYTES]
            version = struct.unpack('>B', version_bytes)[0]
            print('Version of Card-ed:', version)

            pointer += Card.VERSION_BYTES

            # Additional length of initial extension
            ext_len_bytes = header_bytes[pointer:pointer+Card.EXTENSION_BYTES]
            ext_len = struct.unpack('>B', ext_len_bytes)[0]
            print('Length of extension:', ext_len)

            pointer += Card.EXTENSION_BYTES

            # Length of metadata
            metadata_len_bytes = header_bytes[
                pointer:pointer+Card.METADATA_BYTES
            ]
            metadata_len = struct.unpack('>I', metadata_len_bytes)[0]
            print('Length of metadata:', metadata_len)

            pointer += Card.METADATA_BYTES

            # RESERVED
            pointer += Card.RESERVED_BYTES

            data_bytes = card_bytes[0:pointer+ext_len+metadata_len]

            print(pointer)
            print(data_bytes)

            # Initial extension
            init_ext_bytes = data_bytes[pointer:pointer+ext_len]
            init_ext_len = init_ext_bytes.decode('ascii')
            print('Original file extension:', init_ext_len)

            pointer += ext_len

            metadata_bytes = data_bytes[pointer:pointer+metadata_len]
            metadata = metadata_bytes.decode('ascii')
            print('Metadata:', metadata)

            pointer += metadata_len

            file_bytes = card_bytes[pointer:]

        with open(parent / (name + init_ext_len), 'wb') as f:
            f.write(file_bytes)
