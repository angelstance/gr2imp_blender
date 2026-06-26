import math
import struct


VF_BYTE = 0
VF_FLOAT1 = 1
VF_FLOAT2 = 2
VF_FLOAT3 = 3
VF_NORMAL = 4

RAW_TREND_HEADER = struct.Struct("<3i")
LENTAB = (
    (1, 2, 3, 4, 5, 6, 7, 7),
    (1, 2, 3, 4, 5, 6, 7, 8),
    (1, 3, 4, 5, 6, 7, 8, 9),
    (1, 3, 5, 6, 7, 8, 9, 10),
    (1, 4, 5, 6, 7, 8, 9, 11),
    (1, 4, 5, 6, 7, 8, 10, 12),
    (1, 4, 5, 6, 7, 9, 11, 13),
    (1, 4, 5, 6, 8, 10, 12, 14),
    (1, 4, 5, 6, 8, 10, 13, 15),
    (1, 4, 5, 6, 8, 11, 14, 16),
)


class MeshCodecError(RuntimeError):
    pass


class BitStreamReader:
    def __init__(self, data, word_offset=0):
        if len(data) % 4:
            padding = 4 - (len(data) % 4)
            data = data + (b"\x00" * padding)
        self._data = data
        self._word_offset = word_offset
        self.count = 0
        self.word = 0
        self.bit = 0

    def _read_word(self, index):
        start = index * 4
        end = start + 4
        if end > len(self._data):
            return 0
        return struct.unpack_from("<I", self._data, start)[0]

    def read(self, bits):
        if bits == 0:
            return 0
        if bits >= 32:
            raise MeshCodecError("BitStreamReader only supports reads smaller than 32 bits")

        self.count += bits
        if bits <= self.bit:
            self.bit -= bits
            return (self.word >> self.bit) & ((1 << bits) - 1)

        nbits = bits - self.bit
        rword = (self.word & ((1 << self.bit) - 1)) << nbits if self.bit else 0
        self.word = self._read_word(self._word_offset)
        self._word_offset += 1
        self.bit = 32 - nbits
        return rword | (self.word >> self.bit)

    def peek(self, bits):
        saved = (self.count, self.word, self.bit, self._word_offset)
        value = self.read(bits)
        self.count, self.word, self.bit, self._word_offset = saved
        return value

    def flush(self):
        self.count = (self.count + 31) & ~31
        self.bit = 0
        self.word = 0


def _signed_extend(value, bits):
    sign = 1 << (bits - 1)
    return (value & (sign - 1)) - (value & sign)


def _decode_delta(reader, previous, lentab_row):
    if not reader.read(1):
        return previous

    size_index = reader.read(3)
    width = lentab_row[size_index]
    unsigned_value = reader.read(width)
    if size_index != 7:
        signed_value = _signed_extend(unsigned_value, width)
        if signed_value >= 0:
            signed_value += 1
        return previous + signed_value
    return unsigned_value


def _find_normal_triplets(vertex_format, bits):
    normal_indices = []
    sign_indices = []
    i = 0
    while i <= len(vertex_format) - 3:
        if vertex_format[i] == VF_NORMAL and vertex_format[i + 1] == VF_NORMAL and vertex_format[i + 2] == VF_NORMAL:
            sign_index = i + 2
            if bits[sign_index - 1] < bits[sign_index]:
                sign_index -= 1
                if bits[sign_index - 1] < bits[sign_index]:
                    sign_index -= 1
            elif bits[sign_index - 2] < bits[sign_index]:
                sign_index -= 2

            normal_indices.append(i)
            sign_indices.append(sign_index)
            i += 3
            continue
        i += 1
    return normal_indices, sign_indices


class CompressedMesh:
    def __init__(self):
        self.index_count = 0
        self.indices = []
        self.vertex_size = 0
        self.vertex_count = 0
        self.vertex_format = []
        self.vertices = []

    @classmethod
    def from_bytes(cls, blob):
        codec = cls()
        codec._decode(blob)
        return codec

    def _decode(self, blob):
        if len(blob) < 8:
            raise MeshCodecError("Compressed mesh blob is too small")

        reader = BitStreamReader(blob, word_offset=1)
        self.index_count = reader.read(31)
        self.indices = [0] * self.index_count

        current_index = 0
        mru = [0] * 14
        for i in range(self.index_count):
            idx = 0
            if i >= 3:
                idx = reader.read(1)
            if not idx:
                mru[:-1] = mru[1:]
                mru[-1] = current_index
                self.indices[i] = current_index
                current_index += 1
                continue

            t = reader.read(2)
            if not (t & 2):
                cache_index = 11 + t
            elif not (t & 1):
                cache_index = 13 + reader.read(1)
            elif reader.read(1):
                cache_index = 10
            elif reader.read(1):
                cache_index = 9
            elif reader.read(1):
                cache_index = 8
            else:
                cache_index = reader.read(3)

            if cache_index:
                cache_index -= 1
                value = mru[cache_index]
            else:
                bit_count = max(1, (current_index - 1).bit_length())
                value = reader.read(bit_count)

            tail = mru[cache_index + 1 :] if cache_index < len(mru) - 1 else []
            mru[cache_index : len(mru) - 1] = tail
            mru[-1] = value
            self.indices[i] = value

        self.vertex_count = current_index
        self.vertex_size = reader.read(6)
        self.vertex_format = [0] * self.vertex_size
        bits = [0] * self.vertex_size
        for i in range(self.vertex_size):
            fmt = reader.read(3)
            self.vertex_format[i] = fmt
            bits[i] = reader.read(4) + 4 if fmt != VF_BYTE else 0

        normal_indices, sign_indices = _find_normal_triplets(self.vertex_format, bits)
        min_values = [0.0] * self.vertex_size
        max_values = [0.0] * self.vertex_size
        byte_mins = [[0, 0, 0, 0] for _ in range(self.vertex_size)]
        byte_maxs = [[0, 0, 0, 0] for _ in range(self.vertex_size)]

        sign_set = set(sign_indices)
        for j in range(self.vertex_size):
            if self.vertex_format[j] != VF_BYTE:
                if j not in sign_set:
                    raw_min = reader.read(31) << 1
                    raw_max = reader.read(31) << 1
                    min_values[j] = struct.unpack("<f", struct.pack("<I", raw_min))[0]
                    max_values[j] = struct.unpack("<f", struct.pack("<I", raw_max))[0]
                else:
                    sign_mode = reader.read(2)
                    if sign_mode == 0:
                        min_values[j], max_values[j] = -1.0, 1.0
                    elif sign_mode == 1:
                        min_values[j] = max_values[j] = 1.0
                    else:
                        min_values[j] = max_values[j] = -1.0
            else:
                for k in range(4):
                    if reader.read(1):
                        byte_mins[j][k] = 0
                        byte_maxs[j][k] = 255
                    else:
                        value = reader.read(8)
                        byte_mins[j][k] = value
                        byte_maxs[j][k] = value

        pivals = [0] * self.vertex_size
        self.vertices = [[0] * self.vertex_size for _ in range(self.vertex_count)]
        for j in range(self.vertex_size):
            for i in range(self.vertex_count):
                if self.vertex_format[j] != VF_BYTE:
                    if max_values[j] == min_values[j]:
                        self.vertices[i][j] = max_values[j]
                    elif j in sign_set:
                        self.vertices[i][j] = -1.0 if reader.read(1) else 1.0
                    else:
                        pivals[j] = _decode_delta(reader, pivals[j], LENTAB[bits[j] - 7])
                        scale = float(pivals[j]) / float((1 << bits[j]) - 1)
                        self.vertices[i][j] = min_values[j] + ((max_values[j] - min_values[j]) * scale)
                else:
                    packed = 0
                    for k in range(4):
                        if byte_mins[j][k] != byte_maxs[j][k]:
                            component = reader.read(8)
                        else:
                            component = byte_maxs[j][k]
                        packed |= component << (k * 8)
                    self.vertices[i][j] = packed

        for normal_root, sign_index in zip(normal_indices, sign_indices):
            for vertex in self.vertices:
                summed = 0.0
                for k in range(normal_root, normal_root + 3):
                    if k != sign_index:
                        summed += vertex[k] * vertex[k]
                magnitude = math.sqrt(1.0 - summed) if summed < 1.0 else 0.0
                vertex[sign_index] *= magnitude

        reader.flush()


def find_triplet(vertex_format, value):
    for index in range(max(0, len(vertex_format) - 2)):
        if vertex_format[index] == value and vertex_format[index + 1] == value and vertex_format[index + 2] == value:
            return index
    return -1


def find_pair(vertex_format, value, start_index=0):
    for index in range(max(0, start_index), max(0, len(vertex_format) - 1)):
        if vertex_format[index] == value and vertex_format[index + 1] == value:
            return index
    return -1


def is_likely_raw_trend_buffer(blob):
    if len(blob) < RAW_TREND_HEADER.size:
        return False

    triangle_count, vertex_count, vertex_stride = RAW_TREND_HEADER.unpack_from(blob, 0)
    if triangle_count <= 0 or vertex_count <= 0 or vertex_stride < 28:
        return False
    if vertex_stride % 4:
        return False

    expected = RAW_TREND_HEADER.size + (triangle_count * 3 * 4) + (vertex_count * vertex_stride)
    return expected == len(blob)


def decode_raw_trend_buffer(blob):
    if len(blob) < RAW_TREND_HEADER.size:
        raise MeshCodecError("Raw .mesh blob is too small")

    triangle_count, vertex_count, vertex_stride = RAW_TREND_HEADER.unpack_from(blob, 0)
    if triangle_count <= 0 or vertex_count <= 0 or vertex_stride < 28:
        raise MeshCodecError("Raw .mesh header is invalid")

    index_offset = RAW_TREND_HEADER.size
    vertex_offset = index_offset + (triangle_count * 3 * 4)
    indices = struct.unpack_from(f"<{triangle_count * 3}i", blob, index_offset)

    positions = []
    uvs = []
    for vertex_index in range(vertex_count):
        base = vertex_offset + (vertex_index * vertex_stride)
        px, py, pz, u, v = struct.unpack_from("<5f", blob, base)
        positions.append((-px, py, pz))
        uvs.append((u, 1.0 - v))

    faces = []
    for tri_index in range(triangle_count):
        a = indices[tri_index]
        b = indices[triangle_count + (tri_index * 2) + 0]
        c = indices[triangle_count + (tri_index * 2) + 1]
        if a < 0 or b < 0 or c < 0 or a >= vertex_count or b >= vertex_count or c >= vertex_count:
            raise MeshCodecError("Raw .mesh contains out-of-range triangle indices")
        faces.append((a, c, b))

    return {
        "positions": positions,
        "uvs": uvs,
        "faces": faces,
    }


def decode_compressed_mesh(blob):
    codec = CompressedMesh.from_bytes(blob)
    if codec.vertex_count <= 0 or codec.index_count <= 0 or codec.vertex_size <= 0:
        raise MeshCodecError("Compressed .mesh decode failed")

    pos_start = find_triplet(codec.vertex_format, VF_FLOAT3)
    uv_start = find_pair(codec.vertex_format, VF_FLOAT2, 0)
    if pos_start < 0:
        raise MeshCodecError("Could not locate position data in decoded .mesh")

    positions = []
    uvs = []
    for vertex in codec.vertices:
        positions.append((-vertex[pos_start + 0], vertex[pos_start + 1], vertex[pos_start + 2]))
        if uv_start >= 0:
            u = vertex[uv_start + 0]
            v = 1.0 - vertex[uv_start + 1]
        else:
            u = 0.0
            v = 0.0
        uvs.append((u, v))

    triangle_count = codec.index_count // 3
    faces = []
    for tri_index in range(triangle_count):
        a = codec.indices[(tri_index * 3) + 0]
        b = codec.indices[(tri_index * 3) + 1]
        c = codec.indices[(tri_index * 3) + 2]
        if a < 0 or b < 0 or c < 0 or a >= codec.vertex_count or b >= codec.vertex_count or c >= codec.vertex_count:
            raise MeshCodecError("Decoded .mesh contains out-of-range triangle indices")
        faces.append((a, c, b))

    return {
        "positions": positions,
        "uvs": uvs,
        "faces": faces,
        "vertex_format": list(codec.vertex_format),
    }


def decode_mesh(blob):
    if is_likely_raw_trend_buffer(blob):
        result = decode_raw_trend_buffer(blob)
        result["encoding"] = "raw"
        return result

    result = decode_compressed_mesh(blob)
    result["encoding"] = "compressed"
    return result


def encode_raw_mesh(positions, uvs, faces, normals=None):
    triangle_count = len(faces)
    vertex_count = len(positions)
    vertex_stride = 32

    header = RAW_TREND_HEADER.pack(triangle_count, vertex_count, vertex_stride)
    first_indices = []
    paired_indices = []
    for face in faces:
        if len(face) != 3:
            raise MeshCodecError("Raw mesh export expects triangulated faces")
        v0, v1, v2 = face
        first_indices.append(v0)
        paired_indices.extend((v2, v1))

    index_blob = struct.pack(f"<{len(first_indices) + len(paired_indices)}i", *(first_indices + paired_indices))

    if normals is None:
        normals = [(0.0, 0.0, 1.0)] * vertex_count

    vertex_blob = bytearray(vertex_count * vertex_stride)
    for index, position in enumerate(positions):
        uv = uvs[index] if index < len(uvs) else (0.0, 0.0)
        normal = normals[index] if index < len(normals) else (0.0, 0.0, 1.0)
        offset = index * vertex_stride
        struct.pack_into(
            "<8f",
            vertex_blob,
            offset,
            -position[0],
            position[1],
            position[2],
            uv[0],
            1.0 - uv[1],
            -normal[0],
            normal[1],
            normal[2],
        )

    return header + index_blob + bytes(vertex_blob)
