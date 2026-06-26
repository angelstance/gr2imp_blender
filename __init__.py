bl_info = {
    "name": "Granny Runtime Importer/Exporter",
    "author": "angelstance",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "File > Import-Export",
    "description": "Import and export .gr2 (Granny 3D) files",
    "category": "Import-Export",
}

import os

import bpy
from bpy.props import BoolProperty
from bpy.props import CollectionProperty
from bpy.props import StringProperty
from bpy.types import AddonPreferences
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper
from mathutils import Matrix
from mathutils import Quaternion
from mathutils import Vector

from .granny import GrannyError
from .granny import GrannyLibrary


def _addon_root():
    return os.path.dirname(os.path.abspath(__file__))


def _iter_granny_candidates():
    root = _addon_root()
    candidates = [
        os.environ.get("GRANNY_DLL", ""),
        os.path.join(root, "granny2_x64.dll"),
    ]
    seen = set()
    for candidate in candidates:
        if candidate and candidate not in seen:
            seen.add(candidate)
            yield candidate


def _get_preferences():
    addon = bpy.context.preferences.addons.get(__package__)
    return addon.preferences if addon else None


def _resolve_granny_dll(explicit_path=""):
    if explicit_path and os.path.isfile(explicit_path):
        return explicit_path

    preferences = _get_preferences()
    if preferences and preferences.granny_dll_path and os.path.isfile(preferences.granny_dll_path):
        return preferences.granny_dll_path

    for candidate in _iter_granny_candidates():
        if os.path.isfile(candidate):
            return candidate
    return ""


class GR2AddonPreferences(AddonPreferences):
    bl_idname = __package__

    granny_dll_path: StringProperty(
        name="Granny DLL",
        subtype="FILE_PATH",
        description="Optional explicit path to granny2_x64.dll for GR2 import/export",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "granny_dll_path")
        path = _resolve_granny_dll(self.granny_dll_path)
        row = layout.row()
        row.label(text=f"Resolved DLL: {path or 'not found'}")


def _active_collection(context):
    return context.collection or context.scene.collection


def _safe_name(name, fallback):
    cleaned = (name or "").strip()
    return cleaned or fallback


def _build_mesh_object(name, mesh_data, collection):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(mesh_data["positions"], [], mesh_data["faces"])
    mesh.update()

    uvs = mesh_data.get("uvs") or []
    if uvs:
        uv_layer = mesh.uv_layers.new(name="UVMap")
        for polygon in mesh.polygons:
            for loop_index in polygon.loop_indices:
                vertex_index = mesh.loops[loop_index].vertex_index
                if vertex_index < len(uvs):
                    uv_layer.data[loop_index].uv = uvs[vertex_index]

    material_names = mesh_data.get("material_names") or []
    for material_name in material_names:
        material = bpy.data.materials.get(material_name)
        if material is None:
            material = bpy.data.materials.new(material_name)
        mesh.materials.append(material)

    for group in mesh_data.get("material_groups") or []:
        material_index = max(0, group.get("material_index", 0))
        tri_first = max(0, group.get("tri_first", 0))
        tri_count = max(0, group.get("tri_count", 0))
        for tri_offset in range(tri_count):
            polygon_index = tri_first + tri_offset
            if polygon_index < len(mesh.polygons):
                mesh.polygons[polygon_index].material_index = material_index

    normals = mesh_data.get("normals") or []
    if normals and len(normals) == len(mesh.vertices):
        mesh.normals_split_custom_set_from_vertices(normals)

    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def _quaternion_from_granny(orientation):
    return Quaternion((orientation[3], orientation[0], orientation[1], orientation[2]))


def _bone_local_matrix(bone):
    translation = Matrix.Translation(Vector(bone["position"]))
    rotation = _quaternion_from_granny(bone["orientation"]).to_matrix().to_4x4()
    return translation @ rotation


def _build_bone_world_matrices(skeleton):
    world_matrices = [Matrix.Identity(4) for _ in skeleton["bones"]]
    for bone_index, bone in enumerate(skeleton["bones"]):
        local = _bone_local_matrix(bone)
        parent_index = bone["parent_index"]
        if 0 <= parent_index < len(world_matrices):
            world_matrices[bone_index] = world_matrices[parent_index] @ local
        else:
            world_matrices[bone_index] = local
    return world_matrices


def _create_armature_for_skeleton(context, skeleton, collection):
    armature = bpy.data.armatures.new(_safe_name(skeleton["name"], "gr2_skeleton"))
    armature_object = bpy.data.objects.new(armature.name, armature)
    collection.objects.link(armature_object)

    previous_active = context.view_layer.objects.active
    previous_selection = list(context.selected_objects)
    for obj in previous_selection:
        obj.select_set(False)

    armature_object.select_set(True)
    context.view_layer.objects.active = armature_object
    bpy.ops.object.mode_set(mode="EDIT")

    edit_bones = armature.edit_bones
    bone_world_matrices = _build_bone_world_matrices(skeleton)
    children_by_parent = {}
    for index, bone in enumerate(skeleton["bones"]):
        children_by_parent.setdefault(bone["parent_index"], []).append(index)

    created = []
    for bone_index, bone in enumerate(skeleton["bones"]):
        edit_bone = edit_bones.new(_safe_name(bone["name"], f"bone_{bone_index}"))
        created.append(edit_bone)

    for bone_index, bone in enumerate(skeleton["bones"]):
        edit_bone = created[bone_index]
        world_matrix = bone_world_matrices[bone_index]
        head = world_matrix.translation

        child_indices = children_by_parent.get(bone_index, [])
        if child_indices:
            tail = sum((bone_world_matrices[index].translation for index in child_indices), Vector()) / float(len(child_indices))
        else:
            tail = head + (world_matrix.to_quaternion() @ Vector((0.0, 0.1, 0.0)))

        if (tail - head).length < 0.001:
            tail = head + Vector((0.0, 0.1, 0.0))

        edit_bone.head = head
        edit_bone.tail = tail
        parent_index = bone["parent_index"]
        if 0 <= parent_index < len(created):
            edit_bone.parent = created[parent_index]

    bpy.ops.object.mode_set(mode="OBJECT")

    for obj in previous_selection:
        obj.select_set(True)
    if previous_active:
        context.view_layer.objects.active = previous_active

    return armature_object


def _apply_skinning(mesh_object, armature_object, mesh_data, skeleton):
    bone_names = mesh_data.get("bone_bindings") or []
    weights = mesh_data.get("weights") or []
    if not armature_object or not bone_names or not weights:
        return

    vertex_groups = {}
    for bone_name in bone_names:
        group_name = bone_name or "Bone"
        vertex_groups[group_name] = mesh_object.vertex_groups.new(name=group_name)

    for vertex_index, influences in enumerate(weights):
        for bone_index, weight in influences:
            if 0 <= bone_index < len(bone_names) and weight > 0.0:
                vertex_groups[bone_names[bone_index]].add([vertex_index], weight, "REPLACE")

    modifier = mesh_object.modifiers.new(name="Armature", type="ARMATURE")
    modifier.object = armature_object
    mesh_object.parent = armature_object


def _import_gr2_scene(context, gr2_data):
    collection = _active_collection(context)
    armatures = {}

    for model in gr2_data["models"]:
        skeleton_index = model.get("skeleton_index")
        if skeleton_index is not None and skeleton_index not in armatures:
            armatures[skeleton_index] = _create_armature_for_skeleton(
                context,
                gr2_data["skeletons"][skeleton_index],
                collection,
            )

        for mesh_index in model.get("mesh_indices", []):
            mesh_data = gr2_data["meshes"][mesh_index]
            mesh_name = _safe_name(mesh_data["name"], model["name"] or f"gr2_mesh_{mesh_index}")
            mesh_object = _build_mesh_object(mesh_name, mesh_data, collection)
            if skeleton_index is not None:
                _apply_skinning(mesh_object, armatures[skeleton_index], mesh_data, gr2_data["skeletons"][skeleton_index])

    for mesh_index in gr2_data.get("orphan_mesh_indices", []):
        mesh_data = gr2_data["meshes"][mesh_index]
        _build_mesh_object(_safe_name(mesh_data["name"], f"gr2_mesh_{mesh_index}"), mesh_data, collection)


def _triangulated_mesh_data_from_object(obj, depsgraph, use_world_space=True):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        if hasattr(mesh, "calc_normals_split"):
            mesh.calc_normals_split()
        uv_layer = mesh.uv_layers.active.data if mesh.uv_layers.active else None
        world = obj.matrix_world if use_world_space else Matrix.Identity(4)
        normal_matrix = world.to_3x3()

        triangles = []
        raw_positions = []
        raw_uvs = []
        raw_normals = []
        raw_faces = []
        vertex_cursor = 0

        for tri in mesh.loop_triangles:
            tri_corners = []
            face_indices = []
            for i, (loop_index, vertex_index) in enumerate(zip(tri.loops, tri.vertices)):
                position = world @ mesh.vertices[vertex_index].co
                uv = uv_layer[loop_index].uv.copy() if uv_layer else Vector((0.0, 0.0))
                normal = (normal_matrix @ mesh.loops[loop_index].normal).normalized()
                tri_corners.append(
                    {
                        "position": (position.x, position.y, position.z),
                        "normal": (normal.x, normal.y, normal.z),
                        "uv": (uv.x, uv.y),
                    }
                )
                raw_positions.append((position.x, position.y, position.z))
                raw_uvs.append((uv.x, uv.y))
                raw_normals.append((normal.x, normal.y, normal.z))
                face_indices.append(vertex_cursor)
                vertex_cursor += 1
            triangles.append(tuple(tri_corners))
            raw_faces.append(tuple(face_indices))

        return {
            "name": _safe_name(obj.name, "mesh"),
            "triangles": triangles,
            "raw_positions": raw_positions,
            "raw_uvs": raw_uvs,
            "raw_normals": raw_normals,
            "raw_faces": raw_faces,
        }
    finally:
        evaluated.to_mesh_clear()


def _selected_mesh_objects(context):
    selected = [obj for obj in context.selected_objects if obj.type == "MESH"]
    if selected:
        return selected
    active = context.active_object
    if active and active.type == "MESH":
        return [active]
    return [obj for obj in context.scene.objects if obj.type == "MESH"]


class ImportGR2(Operator, ImportHelper):
    bl_idname = "import_scene.gr2"
    bl_label = "Import GR2"
    bl_options = {"PRESET", "UNDO"}

    filename_ext = ".gr2"
    filter_glob: StringProperty(default="*.gr2", options={"HIDDEN"})
    files: CollectionProperty(type=bpy.types.OperatorFileListElement)
    directory: StringProperty(subtype="DIR_PATH")
    granny_dll_path: StringProperty(
        name="Granny DLL",
        subtype="FILE_PATH",
        description="Optional explicit path to granny2_x64.dll",
    )

    def execute(self, context):
        dll_path = _resolve_granny_dll(self.granny_dll_path)
        if not dll_path:
            self.report({"ERROR"}, "Could not locate granny2_x64.dll")
            return {"CANCELLED"}

        paths = []
        if self.files:
            paths = [os.path.join(self.directory, entry.name) for entry in self.files]
        elif self.filepath:
            paths = [self.filepath]

        try:
            granny = GrannyLibrary(dll_path)
            if not granny.version_matches_header:
                major, minor, build, customization = granny.runtime_version
                self.report(
                    {"WARNING"},
                    f"Granny DLL version {major}.{minor}.{build}.{customization} differs from the checked-in SDK header; GR2 support is running in compatibility mode",
                )
            for path in paths:
                data = granny.load_file(path)
                _import_gr2_scene(context, data)
        except (OSError, GrannyError) as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

        return {"FINISHED"}


class ExportGR2(Operator, ExportHelper):
    bl_idname = "export_scene.gr2"
    bl_label = "Export GR2"
    bl_options = {"PRESET"}

    filename_ext = ".gr2"
    filter_glob: StringProperty(default="*.gr2", options={"HIDDEN"})

    use_selection: BoolProperty(
        name="Selected Objects Only",
        description="Export selected mesh objects if available",
        default=True,
    )
    granny_dll_path: StringProperty(
        name="Granny DLL",
        subtype="FILE_PATH",
        description="Optional explicit path to granny2_x64.dll",
    )

    def execute(self, context):
        dll_path = _resolve_granny_dll(self.granny_dll_path)
        if not dll_path:
            self.report({"ERROR"}, "Could not locate granny2_x64.dll")
            return {"CANCELLED"}

        depsgraph = context.evaluated_depsgraph_get()
        objects = _selected_mesh_objects(context) if self.use_selection else [obj for obj in context.scene.objects if obj.type == "MESH"]
        if not objects:
            self.report({"ERROR"}, "No mesh objects found to export")
            return {"CANCELLED"}

        payloads = []
        for obj in objects:
            payload = _triangulated_mesh_data_from_object(obj, depsgraph, use_world_space=True)
            if payload["triangles"]:
                payloads.append({"name": payload["name"], "triangles": payload["triangles"]})

        if not payloads:
            self.report({"ERROR"}, "The exporter could not build any triangulated mesh payloads")
            return {"CANCELLED"}

        try:
            granny = GrannyLibrary(dll_path)
            if not granny.version_matches_header:
                major, minor, build, customization = granny.runtime_version
                self.report(
                    {"ERROR"},
                    f"GR2 export requires the checked-in SDK match the DLL. Loaded DLL version is {major}.{minor}.{build}.{customization}, so export is blocked to avoid crashes.",
                )
                return {"CANCELLED"}
            granny.export_static_meshes(self.filepath, payloads, art_tool_name=b"Blender")
        except (OSError, GrannyError) as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

        return {"FINISHED"}


def _menu_import(self, context):
    self.layout.operator(ImportGR2.bl_idname, text="Granny 3D (.gr2)")


def _menu_export(self, context):
    self.layout.operator(ExportGR2.bl_idname, text="Granny 3D (.gr2)")


CLASSES = (
    GR2AddonPreferences,
    ImportGR2,
    ExportGR2,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(_menu_import)
    bpy.types.TOPBAR_MT_file_export.append(_menu_export)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(_menu_import)
    bpy.types.TOPBAR_MT_file_export.remove(_menu_export)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
