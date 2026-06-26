import ctypes
import os


GRANNY_MAJOR = 2
GRANNY_MINOR = 11
GRANNY_BUILD = 8
GRANNY_CUSTOMIZATION = 0
GR2_EXPORTER_TAG = 0x47523201
GRANNY_EXCLUDE_TYPE_TREE = 0x1
GRANNY_CURRENT_GRN_STANDARD_TAG = 0x80000000 + 57
GRANNY_STANDARD_DISCARDABLE_SECTION = 6
GRANNY_STANDARD_SECTION_COUNT = 7


class GrannyError(RuntimeError):
    pass


class GrannyStructure(ctypes.Structure):
    _pack_ = 4


class GrannyDataTypeDefinition(GrannyStructure):
    pass


GrannyDataTypeDefinition._fields_ = [
    ("Type", ctypes.c_int32),
    ("Name", ctypes.c_char_p),
    ("ReferenceType", ctypes.POINTER(GrannyDataTypeDefinition)),
    ("ArrayWidth", ctypes.c_int32),
    ("Extra", ctypes.c_int32 * 3),
    ("Ignored_Ignored", ctypes.c_size_t),
]


class GrannyVariant(GrannyStructure):
    _fields_ = [
        ("Type", ctypes.POINTER(GrannyDataTypeDefinition)),
        ("Object", ctypes.c_void_p),
    ]


class GrannyTransform(GrannyStructure):
    _fields_ = [
        ("Flags", ctypes.c_uint32),
        ("Position", ctypes.c_float * 3),
        ("Orientation", ctypes.c_float * 4),
        ("ScaleShear", (ctypes.c_float * 3) * 3),
    ]


class GrannyModelMeshBinding(GrannyStructure):
    pass


class GrannyModel(GrannyStructure):
    pass


class GrannyTexture(GrannyStructure):
    pass


class GrannyMaterialMap(GrannyStructure):
    pass


class GrannyMaterial(GrannyStructure):
    _fields_ = [
        ("Name", ctypes.c_char_p),
        ("MapCount", ctypes.c_int32),
        ("Maps", ctypes.POINTER(GrannyMaterialMap)),
        ("Texture", ctypes.POINTER(GrannyTexture)),
        ("ExtendedData", GrannyVariant),
    ]


class GrannyTrackGroup(GrannyStructure):
    pass


class GrannyAnimation(GrannyStructure):
    _fields_ = [
        ("Name", ctypes.c_char_p),
        ("Duration", ctypes.c_float),
        ("TimeStep", ctypes.c_float),
        ("Oversampling", ctypes.c_float),
        ("TrackGroupCount", ctypes.c_int32),
        ("TrackGroups", ctypes.POINTER(ctypes.POINTER(GrannyTrackGroup))),
    ]


class GrannyArtToolInfo(GrannyStructure):
    _fields_ = [
        ("FromArtToolName", ctypes.c_char_p),
        ("ArtToolMajorRevision", ctypes.c_int32),
        ("ArtToolMinorRevision", ctypes.c_int32),
        ("ArtToolPointerSize", ctypes.c_int32),
        ("UnitsPerMeter", ctypes.c_float),
        ("Origin", ctypes.c_float * 3),
        ("RightVector", ctypes.c_float * 3),
        ("UpVector", ctypes.c_float * 3),
        ("BackVector", ctypes.c_float * 3),
        ("ExtendedData", GrannyVariant),
    ]


class GrannyExporterInfo(GrannyStructure):
    _fields_ = [
        ("ExporterName", ctypes.c_char_p),
        ("ExporterMajorRevision", ctypes.c_int32),
        ("ExporterMinorRevision", ctypes.c_int32),
        ("ExporterCustomization", ctypes.c_int32),
        ("ExporterBuildNumber", ctypes.c_int32),
        ("ExtendedData", GrannyVariant),
    ]


class GrannySkeleton(GrannyStructure):
    pass


class GrannyVertexAnnotationSet(GrannyStructure):
    pass


class GrannyVertexData(GrannyStructure):
    _fields_ = [
        ("VertexType", ctypes.POINTER(GrannyDataTypeDefinition)),
        ("VertexCount", ctypes.c_int32),
        ("Vertices", ctypes.POINTER(ctypes.c_uint8)),
        ("VertexComponentNameCount", ctypes.c_int32),
        ("VertexComponentNames", ctypes.POINTER(ctypes.c_char_p)),
        ("VertexAnnotationSetCount", ctypes.c_int32),
        ("VertexAnnotationSets", ctypes.POINTER(GrannyVertexAnnotationSet)),
    ]


class GrannyMorphTarget(GrannyStructure):
    _fields_ = [
        ("ScalarName", ctypes.c_char_p),
        ("VertexData", ctypes.POINTER(GrannyVertexData)),
        ("DataIsDeltas", ctypes.c_int32),
    ]


class GrannyTriMaterialGroup(GrannyStructure):
    _fields_ = [
        ("MaterialIndex", ctypes.c_int32),
        ("TriFirst", ctypes.c_int32),
        ("TriCount", ctypes.c_int32),
    ]


class GrannyTriAnnotationSet(GrannyStructure):
    pass


class GrannyTriTopology(GrannyStructure):
    _fields_ = [
        ("GroupCount", ctypes.c_int32),
        ("Groups", ctypes.POINTER(GrannyTriMaterialGroup)),
        ("IndexCount", ctypes.c_int32),
        ("Indices", ctypes.POINTER(ctypes.c_int32)),
        ("Index16Count", ctypes.c_int32),
        ("Indices16", ctypes.POINTER(ctypes.c_uint16)),
        ("VertexToVertexCount", ctypes.c_int32),
        ("VertexToVertexMap", ctypes.POINTER(ctypes.c_int32)),
        ("VertexToTriangleCount", ctypes.c_int32),
        ("VertexToTriangleMap", ctypes.POINTER(ctypes.c_int32)),
        ("SideToNeighborCount", ctypes.c_int32),
        ("SideToNeighborMap", ctypes.POINTER(ctypes.c_uint32)),
        ("PolygonIndexStartCount", ctypes.c_int32),
        ("PolygonIndexStarts", ctypes.POINTER(ctypes.c_int32)),
        ("PolygonIndexCount", ctypes.c_int32),
        ("PolygonIndices", ctypes.POINTER(ctypes.c_int32)),
        ("BonesForTriangleCount", ctypes.c_int32),
        ("BonesForTriangle", ctypes.POINTER(ctypes.c_int32)),
        ("TriangleToBoneCount", ctypes.c_int32),
        ("TriangleToBoneIndices", ctypes.POINTER(ctypes.c_int32)),
        ("TriAnnotationSetCount", ctypes.c_int32),
        ("TriAnnotationSets", ctypes.POINTER(GrannyTriAnnotationSet)),
    ]


class GrannyBoneBinding(GrannyStructure):
    _fields_ = [
        ("BoneName", ctypes.c_char_p),
        ("OBBMin", ctypes.c_float * 3),
        ("OBBMax", ctypes.c_float * 3),
        ("TriangleCount", ctypes.c_int32),
        ("TriangleIndices", ctypes.POINTER(ctypes.c_int32)),
    ]


class GrannyMaterialBinding(GrannyStructure):
    _fields_ = [("Material", ctypes.POINTER(GrannyMaterial))]


class GrannyMesh(GrannyStructure):
    _fields_ = [
        ("Name", ctypes.c_char_p),
        ("PrimaryVertexData", ctypes.POINTER(GrannyVertexData)),
        ("MorphTargetCount", ctypes.c_int32),
        ("MorphTargets", ctypes.POINTER(GrannyMorphTarget)),
        ("PrimaryTopology", ctypes.POINTER(GrannyTriTopology)),
        ("MaterialBindingCount", ctypes.c_int32),
        ("MaterialBindings", ctypes.POINTER(GrannyMaterialBinding)),
        ("BoneBindingCount", ctypes.c_int32),
        ("BoneBindings", ctypes.POINTER(GrannyBoneBinding)),
        ("ExtendedData", GrannyVariant),
    ]


GrannyModelMeshBinding._fields_ = [("Mesh", ctypes.POINTER(GrannyMesh))]

GrannyModel._fields_ = [
    ("Name", ctypes.c_char_p),
    ("Skeleton", ctypes.POINTER(GrannySkeleton)),
    ("InitialPlacement", GrannyTransform),
    ("MeshBindingCount", ctypes.c_int32),
    ("MeshBindings", ctypes.POINTER(GrannyModelMeshBinding)),
    ("ExtendedData", GrannyVariant),
]


class GrannyBone(GrannyStructure):
    _fields_ = [
        ("Name", ctypes.c_char_p),
        ("ParentIndex", ctypes.c_int32),
        ("LocalTransform", GrannyTransform),
        ("InverseWorld4x4", (ctypes.c_float * 4) * 4),
        ("LODError", ctypes.c_float),
        ("ExtendedData", GrannyVariant),
    ]


GrannySkeleton._fields_ = [
    ("Name", ctypes.c_char_p),
    ("BoneCount", ctypes.c_int32),
    ("Bones", ctypes.POINTER(GrannyBone)),
    ("LODType", ctypes.c_int32),
    ("ExtendedData", GrannyVariant),
]


class GrannyFileInfo(GrannyStructure):
    _fields_ = [
        ("ArtToolInfo", ctypes.POINTER(GrannyArtToolInfo)),
        ("ExporterInfo", ctypes.POINTER(GrannyExporterInfo)),
        ("FromFileName", ctypes.c_char_p),
        ("TextureCount", ctypes.c_int32),
        ("Textures", ctypes.POINTER(ctypes.POINTER(GrannyTexture))),
        ("MaterialCount", ctypes.c_int32),
        ("Materials", ctypes.POINTER(ctypes.POINTER(GrannyMaterial))),
        ("SkeletonCount", ctypes.c_int32),
        ("Skeletons", ctypes.POINTER(ctypes.POINTER(GrannySkeleton))),
        ("VertexDataCount", ctypes.c_int32),
        ("VertexDatas", ctypes.POINTER(ctypes.POINTER(GrannyVertexData))),
        ("TriTopologyCount", ctypes.c_int32),
        ("TriTopologies", ctypes.POINTER(ctypes.POINTER(GrannyTriTopology))),
        ("MeshCount", ctypes.c_int32),
        ("Meshes", ctypes.POINTER(ctypes.POINTER(GrannyMesh))),
        ("ModelCount", ctypes.c_int32),
        ("Models", ctypes.POINTER(ctypes.POINTER(GrannyModel))),
        ("TrackGroupCount", ctypes.c_int32),
        ("TrackGroups", ctypes.POINTER(ctypes.POINTER(GrannyTrackGroup))),
        ("AnimationCount", ctypes.c_int32),
        ("Animations", ctypes.POINTER(ctypes.POINTER(GrannyAnimation))),
        ("ExtendedData", GrannyVariant),
    ]


class GrannyPNT332Vertex(GrannyStructure):
    _fields_ = [
        ("Position", ctypes.c_float * 3),
        ("Normal", ctypes.c_float * 3),
        ("UV", ctypes.c_float * 2),
    ]


def _ptr_value(pointer):
    return ctypes.cast(pointer, ctypes.c_void_p).value or 0


def _decode_string(value):
    return value.decode("cp1252", errors="replace") if value else ""


def _pointer_array(pointer, count):
    if not pointer or count <= 0:
        return []
    return [pointer[index] for index in range(count)]


def _zero_variant():
    return GrannyVariant()


def _identity_matrix4x4():
    matrix = ((ctypes.c_float * 4) * 4)()
    for index in range(4):
        matrix[index][index] = 1.0
    return matrix


class GrannyLibrary:
    def __init__(self, dll_path):
        if not dll_path:
            raise GrannyError("No granny2_x64.dll path was provided")
        if not os.path.isfile(dll_path):
            raise GrannyError(f"Granny DLL not found: {dll_path}")

        self.dll_path = dll_path
        self.dll = ctypes.WinDLL(dll_path)
        self._bind_functions()
        self._bind_data_symbols()
        self._validate_runtime()

    def _bind_functions(self):
        dll = self.dll

        self.GrannyVersionsMatch_ = dll.GrannyVersionsMatch_
        self.GrannyVersionsMatch_.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.GrannyVersionsMatch_.restype = ctypes.c_bool

        self.GrannyGetVersion = dll.GrannyGetVersion
        self.GrannyGetVersion.argtypes = [
            ctypes.POINTER(ctypes.c_int32),
            ctypes.POINTER(ctypes.c_int32),
            ctypes.POINTER(ctypes.c_int32),
            ctypes.POINTER(ctypes.c_int32),
        ]
        self.GrannyGetVersion.restype = None

        self.GrannyReadEntireFile = dll.GrannyReadEntireFile
        self.GrannyReadEntireFile.argtypes = [ctypes.c_char_p]
        self.GrannyReadEntireFile.restype = ctypes.c_void_p

        self.GrannyFreeFile = dll.GrannyFreeFile
        self.GrannyFreeFile.argtypes = [ctypes.c_void_p]
        self.GrannyFreeFile.restype = None

        self.GrannyGetFileInfo = dll.GrannyGetFileInfo
        self.GrannyGetFileInfo.argtypes = [ctypes.c_void_p]
        self.GrannyGetFileInfo.restype = ctypes.POINTER(GrannyFileInfo)

        self.GrannyGetMeshVertexCount = dll.GrannyGetMeshVertexCount
        self.GrannyGetMeshVertexCount.argtypes = [ctypes.POINTER(GrannyMesh)]
        self.GrannyGetMeshVertexCount.restype = ctypes.c_int32

        self.GrannyCopyMeshVertices = dll.GrannyCopyMeshVertices
        self.GrannyCopyMeshVertices.argtypes = [
            ctypes.POINTER(GrannyMesh),
            ctypes.POINTER(GrannyDataTypeDefinition),
            ctypes.c_void_p,
        ]
        self.GrannyCopyMeshVertices.restype = None

        self.GrannyGetMeshTriangleCount = dll.GrannyGetMeshTriangleCount
        self.GrannyGetMeshTriangleCount.argtypes = [ctypes.POINTER(GrannyMesh)]
        self.GrannyGetMeshTriangleCount.restype = ctypes.c_int32

        self.GrannyCopyMeshIndices = dll.GrannyCopyMeshIndices
        self.GrannyCopyMeshIndices.argtypes = [ctypes.POINTER(GrannyMesh), ctypes.c_int32, ctypes.c_void_p]
        self.GrannyCopyMeshIndices.restype = None

        self.GrannyGetMeshTriangleGroupCount = dll.GrannyGetMeshTriangleGroupCount
        self.GrannyGetMeshTriangleGroupCount.argtypes = [ctypes.POINTER(GrannyMesh)]
        self.GrannyGetMeshTriangleGroupCount.restype = ctypes.c_int32

        self.GrannyGetMeshTriangleGroups = dll.GrannyGetMeshTriangleGroups
        self.GrannyGetMeshTriangleGroups.argtypes = [ctypes.POINTER(GrannyMesh)]
        self.GrannyGetMeshTriangleGroups.restype = ctypes.POINTER(GrannyTriMaterialGroup)

        self.GrannyFindMatchingMember = dll.GrannyFindMatchingMember
        self.GrannyFindMatchingMember.argtypes = [
            ctypes.POINTER(GrannyDataTypeDefinition),
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.POINTER(GrannyVariant),
        ]
        self.GrannyFindMatchingMember.restype = ctypes.c_bool

        self.GrannyGetTotalObjectSize = dll.GrannyGetTotalObjectSize
        self.GrannyGetTotalObjectSize.argtypes = [ctypes.POINTER(GrannyDataTypeDefinition)]
        self.GrannyGetTotalObjectSize.restype = ctypes.c_int32

        self.GrannyGetTemporaryDirectory = dll.GrannyGetTemporaryDirectory
        self.GrannyGetTemporaryDirectory.argtypes = []
        self.GrannyGetTemporaryDirectory.restype = ctypes.c_char_p

        self.GrannyBeginFile = dll.GrannyBeginFile
        self.GrannyBeginFile.argtypes = [
            ctypes.c_int32,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        self.GrannyBeginFile.restype = ctypes.c_void_p

        self.GrannyAbortFile = dll.GrannyAbortFile
        self.GrannyAbortFile.argtypes = [ctypes.c_void_p]
        self.GrannyAbortFile.restype = None

        self.GrannyBeginFileDataTreeWriting = dll.GrannyBeginFileDataTreeWriting
        self.GrannyBeginFileDataTreeWriting.argtypes = [
            ctypes.POINTER(GrannyDataTypeDefinition),
            ctypes.c_void_p,
            ctypes.c_int32,
            ctypes.c_int32,
        ]
        self.GrannyBeginFileDataTreeWriting.restype = ctypes.c_void_p

        self.GrannyEndFileDataTreeWriting = dll.GrannyEndFileDataTreeWriting
        self.GrannyEndFileDataTreeWriting.argtypes = [ctypes.c_void_p]
        self.GrannyEndFileDataTreeWriting.restype = None

        self.GrannyWriteDataTreeToFileBuilder = dll.GrannyWriteDataTreeToFileBuilder
        self.GrannyWriteDataTreeToFileBuilder.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.GrannyWriteDataTreeToFileBuilder.restype = ctypes.c_bool

        self.GrannyWriteDataTreeToFile = dll.GrannyWriteDataTreeToFile
        self.GrannyWriteDataTreeToFile.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_int32,
        ]
        self.GrannyWriteDataTreeToFile.restype = ctypes.c_bool

        self.GrannySetFileDataTreeFlags = dll.GrannySetFileDataTreeFlags
        self.GrannySetFileDataTreeFlags.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.GrannySetFileDataTreeFlags.restype = None

        self.GrannyEndFile = dll.GrannyEndFile
        self.GrannyEndFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.GrannyEndFile.restype = ctypes.c_bool

        self.GrannyEndFileRaw = dll.GrannyEndFileRaw
        self.GrannyEndFileRaw.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.GrannyEndFileRaw.restype = ctypes.c_bool

        self.GrannyMakeIdentity = dll.GrannyMakeIdentity
        self.GrannyMakeIdentity.argtypes = [ctypes.POINTER(GrannyTransform)]
        self.GrannyMakeIdentity.restype = None

        self.GrannyBeginMesh = dll.GrannyBeginMesh
        self.GrannyBeginMesh.argtypes = [
            ctypes.c_int32,
            ctypes.c_int32,
            ctypes.c_int32,
            ctypes.c_int32,
            ctypes.POINTER(GrannyDataTypeDefinition),
        ]
        self.GrannyBeginMesh.restype = ctypes.c_void_p

        self.GrannyGetResultingVertexDataSize = dll.GrannyGetResultingVertexDataSize
        self.GrannyGetResultingVertexDataSize.argtypes = [ctypes.c_void_p]
        self.GrannyGetResultingVertexDataSize.restype = ctypes.c_int32

        self.GrannyGetResultingTopologySize = dll.GrannyGetResultingTopologySize
        self.GrannyGetResultingTopologySize.argtypes = [ctypes.c_void_p]
        self.GrannyGetResultingTopologySize.restype = ctypes.c_int32

        self.GrannyEndMeshInPlace = dll.GrannyEndMeshInPlace
        self.GrannyEndMeshInPlace.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.POINTER(GrannyVertexData)),
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.POINTER(GrannyTriTopology)),
        ]
        self.GrannyEndMeshInPlace.restype = None

        self.GrannySetPosition = dll.GrannySetPosition
        self.GrannySetPosition.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float, ctypes.c_float]
        self.GrannySetPosition.restype = None

        self.GrannyPushVertex = dll.GrannyPushVertex
        self.GrannyPushVertex.argtypes = [ctypes.c_void_p]
        self.GrannyPushVertex.restype = None

        self.GrannySetVertexIndex = dll.GrannySetVertexIndex
        self.GrannySetVertexIndex.argtypes = [ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32]
        self.GrannySetVertexIndex.restype = None

        self.GrannySetNormal = dll.GrannySetNormal
        self.GrannySetNormal.argtypes = [ctypes.c_void_p, ctypes.c_int32, ctypes.c_float, ctypes.c_float, ctypes.c_float]
        self.GrannySetNormal.restype = None

        self.GrannySetChannel = dll.GrannySetChannel
        self.GrannySetChannel.argtypes = [ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_float), ctypes.c_int32]
        self.GrannySetChannel.restype = None

        self.GrannySetMaterial = dll.GrannySetMaterial
        self.GrannySetMaterial.argtypes = [ctypes.c_void_p, ctypes.c_int32]
        self.GrannySetMaterial.restype = None

        self.GrannyPushTriangle = dll.GrannyPushTriangle
        self.GrannyPushTriangle.argtypes = [ctypes.c_void_p]
        self.GrannyPushTriangle.restype = None

    def _bind_data_symbols(self):
        self._pnt332_vertex_type_raw = ctypes.c_void_p.in_dll(self.dll, "GrannyPNT332VertexType")
        self._file_info_type_raw = ctypes.c_void_p.in_dll(self.dll, "GrannyFileInfoType")
        self._this_platform_magic_raw = ctypes.c_void_p.in_dll(self.dll, "GrannyGRNFileMV_ThisPlatform")

        self.pnt332_vertex_type = ctypes.cast(self._pnt332_vertex_type_raw.value, ctypes.POINTER(GrannyDataTypeDefinition))
        self.file_info_type = ctypes.cast(self._file_info_type_raw.value, ctypes.POINTER(GrannyDataTypeDefinition))
        self.this_platform_magic = self._this_platform_magic_raw.value

    def _validate_runtime(self):
        major = ctypes.c_int32()
        minor = ctypes.c_int32()
        build = ctypes.c_int32()
        customization = ctypes.c_int32()
        self.GrannyGetVersion(
            ctypes.byref(major),
            ctypes.byref(minor),
            ctypes.byref(build),
            ctypes.byref(customization),
        )
        self.runtime_version = (major.value, minor.value, build.value, customization.value)
        self.version_matches_header = bool(
            self.GrannyVersionsMatch_(GRANNY_MAJOR, GRANNY_MINOR, GRANNY_BUILD, GRANNY_CUSTOMIZATION)
        )
        if not self.pnt332_vertex_type:
            raise GrannyError("Could not resolve GrannyPNT332VertexType from the DLL")
        if not self.file_info_type:
            raise GrannyError("Could not resolve GrannyFileInfoType from the DLL")
        if not self.this_platform_magic:
            raise GrannyError("Could not resolve GrannyGRNFileMV_ThisPlatform from the DLL")

    def load_file(self, file_path):
        encoded = os.fsdecode(file_path).encode("cp1252", errors="replace")
        handle = self.GrannyReadEntireFile(encoded)
        if not handle:
            raise GrannyError(f"Unable to load GR2 file through the Granny runtime: {file_path}")
        try:
            info = self.GrannyGetFileInfo(handle)
            if not info:
                raise GrannyError("Unable to read Granny file info")
            return self._extract_file_info(info.contents)
        finally:
            self.GrannyFreeFile(handle)

    def _extract_file_info(self, info):
        skeleton_map = {}
        skeletons = []
        for index, skeleton_ptr in enumerate(_pointer_array(info.Skeletons, info.SkeletonCount)):
            skeleton_map[_ptr_value(skeleton_ptr)] = index
            skeletons.append(self._extract_skeleton(skeleton_ptr.contents))

        mesh_map = {}
        meshes = []
        for index, mesh_ptr in enumerate(_pointer_array(info.Meshes, info.MeshCount)):
            mesh_map[_ptr_value(mesh_ptr)] = index
            meshes.append(self._extract_mesh(mesh_ptr))

        models = []
        referenced_meshes = set()
        for model_ptr in _pointer_array(info.Models, info.ModelCount):
            model = model_ptr.contents
            mesh_indices = []
            for binding_index in range(model.MeshBindingCount):
                mesh_ptr = model.MeshBindings[binding_index].Mesh
                if mesh_ptr:
                    mesh_index = mesh_map.get(_ptr_value(mesh_ptr))
                    if mesh_index is not None:
                        mesh_indices.append(mesh_index)
                        referenced_meshes.add(mesh_index)
            skeleton_index = None
            if model.Skeleton:
                skeleton_index = skeleton_map.get(_ptr_value(model.Skeleton))
            models.append(
                {
                    "name": _decode_string(model.Name),
                    "skeleton_index": skeleton_index,
                    "mesh_indices": mesh_indices,
                }
            )

        orphan_mesh_indices = [index for index in range(len(meshes)) if index not in referenced_meshes]
        return {
            "skeletons": skeletons,
            "meshes": meshes,
            "models": models,
            "orphan_mesh_indices": orphan_mesh_indices,
        }

    def _extract_skeleton(self, skeleton):
        bones = []
        for bone_index in range(skeleton.BoneCount):
            bone = skeleton.Bones[bone_index]
            inverse_world = [[bone.InverseWorld4x4[row][column] for column in range(4)] for row in range(4)]
            scale_shear = [[bone.LocalTransform.ScaleShear[row][column] for column in range(3)] for row in range(3)]
            bones.append(
                {
                    "name": _decode_string(bone.Name) or f"bone_{bone_index}",
                    "parent_index": bone.ParentIndex,
                    "position": tuple(bone.LocalTransform.Position),
                    "orientation": tuple(bone.LocalTransform.Orientation),
                    "scale_shear": scale_shear,
                    "inverse_world_4x4": inverse_world,
                }
            )
        return {
            "name": _decode_string(skeleton.Name),
            "bones": bones,
        }

    def _extract_mesh(self, mesh_ptr):
        mesh = mesh_ptr.contents
        vertex_count = self.GrannyGetMeshVertexCount(mesh_ptr)
        triangle_count = self.GrannyGetMeshTriangleCount(mesh_ptr)
        if vertex_count <= 0 or triangle_count <= 0:
            return {
                "name": _decode_string(mesh.Name),
                "positions": [],
                "normals": [],
                "uvs": [],
                "faces": [],
                "material_names": [],
                "material_groups": [],
                "bone_bindings": [],
                "weights": [],
            }

        vertex_buffer = (GrannyPNT332Vertex * vertex_count)()
        self.GrannyCopyMeshVertices(mesh_ptr, self.pnt332_vertex_type, ctypes.byref(vertex_buffer))

        index_buffer = (ctypes.c_int32 * (triangle_count * 3))()
        self.GrannyCopyMeshIndices(mesh_ptr, ctypes.sizeof(ctypes.c_int32), ctypes.byref(index_buffer))

        positions = []
        normals = []
        uvs = []
        for vertex in vertex_buffer:
            positions.append(tuple(vertex.Position))
            normals.append(tuple(vertex.Normal))
            uvs.append((vertex.UV[0], 1.0 - vertex.UV[1]))

        faces = []
        for triangle_index in range(triangle_count):
            base = triangle_index * 3
            faces.append((index_buffer[base + 0], index_buffer[base + 1], index_buffer[base + 2]))

        material_groups = []
        group_count = self.GrannyGetMeshTriangleGroupCount(mesh_ptr)
        group_ptr = self.GrannyGetMeshTriangleGroups(mesh_ptr)
        if group_ptr and group_count > 0:
            for group_index in range(group_count):
                group = group_ptr[group_index]
                material_groups.append(
                    {
                        "material_index": group.MaterialIndex,
                        "tri_first": group.TriFirst,
                        "tri_count": group.TriCount,
                    }
                )

        material_names = []
        for binding_index in range(mesh.MaterialBindingCount):
            binding = mesh.MaterialBindings[binding_index]
            material_name = ""
            if binding.Material:
                material_name = _decode_string(binding.Material.contents.Name)
            material_names.append(material_name or f"{_decode_string(mesh.Name)}_material_{binding_index}")

        bone_bindings = [_decode_string(mesh.BoneBindings[index].BoneName) for index in range(mesh.BoneBindingCount)]
        weights = self._extract_weights(mesh_ptr, vertex_count)

        return {
            "name": _decode_string(mesh.Name),
            "positions": positions,
            "normals": normals,
            "uvs": uvs,
            "faces": faces,
            "material_names": material_names,
            "material_groups": material_groups,
            "bone_bindings": bone_bindings,
            "weights": weights,
        }

    def _extract_weights(self, mesh_ptr, vertex_count):
        mesh = mesh_ptr.contents
        if mesh.BoneBindingCount <= 0 or not mesh.PrimaryVertexData or not mesh.PrimaryVertexData.contents.VertexType:
            return [[] for _ in range(vertex_count)]

        vertices_pointer = mesh.PrimaryVertexData.contents.Vertices
        if not vertices_pointer:
            return [[] for _ in range(vertex_count)]

        stride = self.GrannyGetTotalObjectSize(mesh.PrimaryVertexData.contents.VertexType)
        if stride <= 0:
            return [[] for _ in range(vertex_count)]

        index_variant = GrannyVariant()
        weight_variant = GrannyVariant()
        rigid_variant = GrannyVariant()

        base_object = ctypes.cast(vertices_pointer, ctypes.c_void_p)
        has_indices = self.GrannyFindMatchingMember(
            mesh.PrimaryVertexData.contents.VertexType,
            base_object,
            b"BoneIndices",
            ctypes.byref(index_variant),
        )
        has_weights = self.GrannyFindMatchingMember(
            mesh.PrimaryVertexData.contents.VertexType,
            base_object,
            b"BoneWeights",
            ctypes.byref(weight_variant),
        )
        has_rigid = self.GrannyFindMatchingMember(
            mesh.PrimaryVertexData.contents.VertexType,
            base_object,
            b"BoneIndex",
            ctypes.byref(rigid_variant),
        )

        index_count = index_variant.Type.contents.ArrayWidth if has_indices and index_variant.Type else 0
        weight_count = weight_variant.Type.contents.ArrayWidth if has_weights and weight_variant.Type else 0
        if index_count <= 0 and has_indices:
            index_count = 1
        if weight_count <= 0 and has_weights:
            weight_count = 1

        index_base = index_variant.Object if has_indices else 0
        weight_base = weight_variant.Object if has_weights else 0
        rigid_base = rigid_variant.Object if has_rigid else 0

        results = []
        for vertex_index in range(vertex_count):
            accum = {}
            if index_base:
                vertex_indices_ptr = index_base + (vertex_index * stride)
                vertex_weights_ptr = weight_base + (vertex_index * stride) if weight_base else 0
                influence_count = index_count
                for influence_index in range(influence_count):
                    binding_index = ctypes.c_ubyte.from_address(vertex_indices_ptr + influence_index).value
                    if binding_index < 0 or binding_index >= mesh.BoneBindingCount:
                        continue
                    if vertex_weights_ptr:
                        weight = ctypes.c_ubyte.from_address(vertex_weights_ptr + influence_index).value / 255.0
                    else:
                        weight = 1.0 if influence_index == 0 else 0.0
                    if weight <= 0.0:
                        continue
                    accum[binding_index] = accum.get(binding_index, 0.0) + weight
            elif rigid_base:
                binding_index = ctypes.c_uint32.from_address(rigid_base + (vertex_index * stride)).value
                if 0 <= binding_index < mesh.BoneBindingCount:
                    accum[int(binding_index)] = 1.0

            if not accum and mesh.BoneBindingCount == 1:
                accum[0] = 1.0

            total = sum(accum.values())
            if total > 0.0:
                entries = sorted((bone_index, weight / total) for bone_index, weight in accum.items() if weight > 0.0)
            else:
                entries = []
            results.append(entries)
        return results

    def export_static_meshes(self, output_path, mesh_payloads, art_tool_name=b"Blender", art_tool_major=4, art_tool_minor=0):
        if not mesh_payloads:
            raise GrannyError("No mesh payloads were provided for GR2 export")

        file_info = GrannyFileInfo()
        owned_strings = []
        art_tool_info = GrannyArtToolInfo()
        exporter_info = GrannyExporterInfo()
        materials = []
        meshes = []
        models = []
        vertex_datas = []
        topologies = []
        vertex_data_ptrs = []
        topology_ptrs = []
        vertex_data_memory = []
        topology_memory = []
        material_bindings = []
        mesh_bindings = []
        material_pointer_array = None
        vertex_data_pointer_array = None
        topology_pointer_array = None
        mesh_pointer_array = None
        model_pointer_array = None

        def intern(text):
            if isinstance(text, bytes):
                raw = text
            else:
                raw = os.fsdecode(text).encode("cp1252", errors="replace")
            buffer = ctypes.create_string_buffer(raw + b"\x00")
            owned_strings.append(buffer)
            return ctypes.cast(buffer, ctypes.c_char_p)

        art_tool_info.FromArtToolName = intern(art_tool_name)
        art_tool_info.ArtToolMajorRevision = art_tool_major
        art_tool_info.ArtToolMinorRevision = art_tool_minor
        art_tool_info.ArtToolPointerSize = ctypes.sizeof(ctypes.c_void_p)
        art_tool_info.UnitsPerMeter = 1.0
        art_tool_info.Origin[:] = (0.0, 0.0, 0.0)
        art_tool_info.RightVector[:] = (1.0, 0.0, 0.0)
        art_tool_info.UpVector[:] = (0.0, 0.0, 1.0)
        art_tool_info.BackVector[:] = (0.0, -1.0, 0.0)
        art_tool_info.ExtendedData = _zero_variant()

        exporter_info.ExporterName = intern("Blender GR2 Exporter")
        exporter_info.ExporterMajorRevision = 1
        exporter_info.ExporterMinorRevision = 0
        exporter_info.ExporterCustomization = 0
        exporter_info.ExporterBuildNumber = 1
        exporter_info.ExtendedData = _zero_variant()

        for mesh_index, payload in enumerate(mesh_payloads):
            triangles = payload.get("triangles") or []
            if not triangles:
                continue

            exported_vertex_count = len(triangles) * 3
            builder = self.GrannyBeginMesh(exported_vertex_count, len(triangles), 1, 0, self.pnt332_vertex_type)
            if not builder:
                raise GrannyError("GrannyBeginMesh failed")

            for triangle in triangles:
                if len(triangle) != 3:
                    raise GrannyError("GR2 export expects triangulated mesh payloads")
                for corner in triangle:
                    position = corner.get("position", (0.0, 0.0, 0.0))
                    self.GrannySetPosition(builder, position[0], position[1], position[2])
                    self.GrannyPushVertex(builder)

            for triangle_index, triangle in enumerate(triangles):
                for edge_index, corner in enumerate(triangle):
                    normal = corner.get("normal", (0.0, 0.0, 1.0))
                    uv = corner.get("uv", (0.0, 0.0))
                    vertex_index = (triangle_index * 3) + edge_index
                    uv_value = (ctypes.c_float * 2)(uv[0], 1.0 - uv[1])
                    self.GrannySetVertexIndex(builder, edge_index, vertex_index)
                    self.GrannySetNormal(builder, edge_index, normal[0], normal[1], normal[2])
                    self.GrannySetChannel(builder, edge_index, 0, uv_value, 2)
                self.GrannySetMaterial(builder, 0)
                self.GrannyPushTriangle(builder)

            vertex_size = self.GrannyGetResultingVertexDataSize(builder)
            topology_size = self.GrannyGetResultingTopologySize(builder)
            if vertex_size <= 0 or topology_size <= 0:
                raise GrannyError("Granny mesh builder did not produce valid mesh buffers")

            vertex_memory = (ctypes.c_uint8 * vertex_size)()
            topology_memory_block = (ctypes.c_uint8 * topology_size)()
            vertex_data_ptr = ctypes.POINTER(GrannyVertexData)()
            topology_ptr = ctypes.POINTER(GrannyTriTopology)()
            self.GrannyEndMeshInPlace(
                builder,
                vertex_memory,
                ctypes.byref(vertex_data_ptr),
                topology_memory_block,
                ctypes.byref(topology_ptr),
            )
            if not vertex_data_ptr or not topology_ptr:
                raise GrannyError("GrannyEndMeshInPlace failed to build a mesh")

            material = GrannyMaterial()
            material.Name = intern(f"{payload.get('name') or f'gr2_mesh_{mesh_index}'}_material")
            material.MapCount = 0
            material.Maps = None
            material.Texture = None
            material.ExtendedData = _zero_variant()
            material_ptr = ctypes.pointer(material)

            mesh_material_bindings = (GrannyMaterialBinding * 1)()
            mesh_material_bindings[0].Material = material_ptr

            mesh_name = intern(payload.get("name") or f"gr2_mesh_{mesh_index}")

            mesh = GrannyMesh()
            mesh.Name = mesh_name
            mesh.PrimaryVertexData = vertex_data_ptr
            mesh.MorphTargetCount = 0
            mesh.MorphTargets = None
            mesh.PrimaryTopology = topology_ptr
            mesh.MaterialBindingCount = 1
            mesh.MaterialBindings = mesh_material_bindings
            mesh.BoneBindingCount = 0
            mesh.BoneBindings = None
            mesh.ExtendedData = _zero_variant()
            mesh_ptr = ctypes.pointer(mesh)

            model_mesh_bindings = (GrannyModelMeshBinding * 1)()
            model_mesh_bindings[0].Mesh = mesh_ptr

            model = GrannyModel()
            model.Name = mesh_name
            model.Skeleton = None
            self.GrannyMakeIdentity(ctypes.byref(model.InitialPlacement))
            model.MeshBindingCount = 1
            model.MeshBindings = model_mesh_bindings
            model.ExtendedData = _zero_variant()

            materials.append(material)
            meshes.append(mesh)
            models.append(model)
            vertex_datas.append(vertex_data_ptr)
            topologies.append(topology_ptr)
            vertex_data_ptrs.append(vertex_data_ptr)
            topology_ptrs.append(topology_ptr)
            vertex_data_memory.append(vertex_memory)
            topology_memory.append(topology_memory_block)
            material_bindings.append(mesh_material_bindings)
            mesh_bindings.append(model_mesh_bindings)

        if not meshes:
            raise GrannyError("The GR2 exporter could not build any mesh payloads")

        material_pointer_array = (ctypes.POINTER(GrannyMaterial) * len(materials))(
            *[ctypes.pointer(material) for material in materials]
        )
        vertex_data_pointer_array = (ctypes.POINTER(GrannyVertexData) * len(vertex_datas))(*vertex_datas)
        topology_pointer_array = (ctypes.POINTER(GrannyTriTopology) * len(topologies))(*topologies)
        mesh_pointer_array = (ctypes.POINTER(GrannyMesh) * len(meshes))(
            *[ctypes.pointer(mesh) for mesh in meshes]
        )
        model_pointer_array = (ctypes.POINTER(GrannyModel) * len(models))(
            *[ctypes.pointer(model) for model in models]
        )

        file_info.ArtToolInfo = ctypes.pointer(art_tool_info)
        file_info.ExporterInfo = ctypes.pointer(exporter_info)
        file_info.FromFileName = intern(output_path)
        file_info.SkeletonCount = 0
        file_info.Skeletons = None
        file_info.MaterialCount = len(materials)
        file_info.Materials = material_pointer_array
        file_info.VertexDataCount = len(vertex_datas)
        file_info.VertexDatas = vertex_data_pointer_array
        file_info.TriTopologyCount = len(topologies)
        file_info.TriTopologies = topology_pointer_array
        file_info.MeshCount = len(meshes)
        file_info.Meshes = mesh_pointer_array
        file_info.ModelCount = len(models)
        file_info.Models = model_pointer_array
        file_info.ExtendedData = _zero_variant()

        builder = self.GrannyBeginFile(
            GRANNY_STANDARD_SECTION_COUNT,
            GRANNY_CURRENT_GRN_STANDARD_TAG,
            self.this_platform_magic,
            self.GrannyGetTemporaryDirectory(),
            b"blender_gr2exp",
        )
        if not builder:
            raise GrannyError("GrannyBeginFile failed")

        writer = self.GrannyBeginFileDataTreeWriting(
            self.file_info_type,
            ctypes.byref(file_info),
            GRANNY_STANDARD_DISCARDABLE_SECTION,
            0,
        )
        if not writer:
            self.GrannyAbortFile(builder)
            raise GrannyError("GrannyBeginFileDataTreeWriting failed")

        try:
            if not self.GrannyWriteDataTreeToFileBuilder(writer, builder):
                self.GrannyAbortFile(builder)
                raise GrannyError("GrannyWriteDataTreeToFileBuilder failed")
        finally:
            self.GrannyEndFileDataTreeWriting(writer)

        output_bytes = os.fsdecode(output_path).encode("cp1252", errors="replace")
        if not self.GrannyEndFile(builder, output_bytes):
            raise GrannyError("GrannyEndFile failed")
