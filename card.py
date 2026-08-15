import struct
from pathlib import Path


class Card:
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

            # Extension signature
            signature = file_bytes[0:4]
            if signature == b'CARD':
                raise Exception('This file was already Card-ed!')

            card_bytes = bytes()

            # Extension signature
            card_bytes += struct.pack('@4s', b'CARD')
            # Version
            card_bytes += struct.pack('>B', 0)
            # Additional length of initial extension
            card_bytes += struct.pack('>B', len(extension))
            # Initial extension
            card_bytes += extension.encode('ascii')
            # Length of metadata
            card_bytes += struct.pack('>I', len(name))
            # Metadata
            card_bytes += name.encode('ascii')
            print(card_bytes)
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

            print(' '.join(f'{b:02X}' for b in card_bytes[0:25]))

            # Extension signature
            signature = card_bytes[0:4]
            if signature != b'CARD':
                raise Exception('This file was not Card-ed!')

            # Version
            version_bytes = card_bytes[4:5]
            version = struct.unpack('>B', version_bytes)[0]
            print('Version of Card-ed:', version)

            # Additional length of initial extension
            INIT_FORMAT_END = 5
            INIT_EXT_START = INIT_FORMAT_END + 1

            ext_len_bytes = card_bytes[INIT_FORMAT_END:INIT_EXT_START]
            ext_len = struct.unpack('>B', ext_len_bytes)[0]

            # Initial extension
            INIT_EXT_END = INIT_EXT_START + ext_len

            init_ext_bytes = card_bytes[INIT_EXT_START:INIT_EXT_END]
            init_ext_len = init_ext_bytes.decode('ascii')
            print('Original file extension:', init_ext_len)

            # Length of metadata
            LEN_OF_METADATA = 4

            metadata_len_bytes = card_bytes[
                INIT_EXT_END:INIT_EXT_END+LEN_OF_METADATA
            ]
            metadata_len = struct.unpack('>I', metadata_len_bytes)[0]

            # Metadata
            METADATA_START = INIT_EXT_END+LEN_OF_METADATA

            metadata_bytes = card_bytes[
                METADATA_START:METADATA_START+metadata_len
            ]
            metadata = metadata_bytes.decode('ascii')
            print('Metadata:', metadata)

            # Files bytes
            FILE_BYTES_START = METADATA_START+metadata_len
            file_bytes = card_bytes[FILE_BYTES_START:]

        with open(parent / (name + init_ext_len), 'wb') as f:
            f.write(file_bytes)
