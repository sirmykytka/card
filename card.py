import struct
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CardManifest:
    """
    A data class that represents the card manifest, i.e. what was put into it.
    """
    version: int
    extension: str
    metadata: str


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

    EXTENSION = ".card"
    SIGNATURE = b"CARD"
    VERSION = 1

    SIGNATURE_BYTES = 4
    VERSION_BYTES = 1
    EXTENSION_BYTES = 1
    METADATA_BYTES = 4
    RESERVED_BYTES = 6
    HEADER_BYTES = 16

    @staticmethod
    def pack(file_path: str | Path, metadata: str) -> None:
        """
        A method that creates binary container with a file and metadata.
        :param file_path: path to file
        :param metadata: metadata that will be added to the file
        :return:
        """

        path = Path(file_path) if isinstance(file_path, str) else file_path

        if not path.exists():
            raise FileNotFoundError(f'File {path} does not exist')

        if not path.is_file():
            raise Exception(f"{path} is not a file")

        parent = path.parent
        name = path.stem
        extension = path.suffix
        card_file = parent / (name + '.card')

        if extension == Card.EXTENSION:
            raise Exception('This file is already the card')

        with open(path, 'rb') as f:
            file_bytes = f.read()

            # Check the signature
            signature = file_bytes[0:Card.SIGNATURE_BYTES]
            if signature == Card.SIGNATURE:
                raise Exception('This file was already turn into the card')

            card_bytes = bytes()

            # Struct of header
            card_bytes += struct.pack('@4s', Card.SIGNATURE)
            card_bytes += struct.pack('>B', Card.VERSION)
            card_bytes += struct.pack('>B', len(extension))
            card_bytes += struct.pack('>I', len(metadata))
            card_bytes += struct.pack(
                f'@{Card.RESERVED_BYTES}s',
                b'X' * Card.RESERVED_BYTES
            )

            # Metadata with the file itself
            card_bytes += extension.encode('ascii')
            card_bytes += metadata.encode('ascii')

            card_bytes += file_bytes

        with open(card_file, 'wb') as f:
            f.write(card_bytes)

    @staticmethod
    def unpack(card_path: str | Path) -> CardManifest:
        """
        A method that unpacks a binary container as a file and a card manifest.
        :param card_path: path to file
        :return:
        """

        path = Path(card_path) if isinstance(card_path, str) else card_path

        if not path.exists():
            raise FileNotFoundError(f'File {path} does not exist')

        if not path.is_file():
            raise Exception(f"{path} is not a file")

        parent = path.parent
        name = path.stem
        extension = path.suffix

        if extension != Card.EXTENSION:
            raise Exception('This file is not a card!')

        with open(path, 'rb') as p:
            card_bytes = p.read()

            header_bytes = card_bytes[0:Card.HEADER_BYTES - 1]
            # header = ' '.join(f'{b:02X}' for b in header_bytes)

            pointer = 0

            # Signature
            signature = header_bytes[pointer:Card.SIGNATURE_BYTES]
            if signature != Card.SIGNATURE:
                raise Exception('This file was not packed into card!')

            pointer += Card.SIGNATURE_BYTES

            # Version
            version_bytes = header_bytes[pointer:pointer+Card.VERSION_BYTES]
            version = struct.unpack('>B', version_bytes)[0]

            pointer += Card.VERSION_BYTES

            # Additional length of initial extension
            ext_len_bytes = header_bytes[pointer:pointer+Card.EXTENSION_BYTES]
            ext_len = struct.unpack('>B', ext_len_bytes)[0]

            pointer += Card.EXTENSION_BYTES

            # Length of metadata
            metadata_len_bytes = header_bytes[
                pointer:pointer+Card.METADATA_BYTES
            ]
            metadata_len = struct.unpack('>I', metadata_len_bytes)[0]

            pointer += Card.METADATA_BYTES

            # RESERVED
            pointer += Card.RESERVED_BYTES

            data_bytes = card_bytes[0:pointer+ext_len+metadata_len]

            # Initial extension
            init_ext_bytes = data_bytes[pointer:pointer+ext_len]
            init_ext_len = init_ext_bytes.decode('ascii')

            pointer += ext_len

            metadata_bytes = data_bytes[pointer:pointer+metadata_len]
            metadata = metadata_bytes.decode('ascii')

            pointer += metadata_len

            file_bytes = card_bytes[pointer:]

        file_path = parent / (name + init_ext_len)

        with open(file_path, 'wb') as f:
            f.write(file_bytes)

        return CardManifest(version, extension, metadata)
