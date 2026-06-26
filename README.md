# Granny Runtime Importer/Exporter for Blender

A Blender 4.0+ addon for importing and exporting `.gr2` (Granny 3D) files.

Made by **angelstance**.

> **Note:** Animation export is not supported. Mesh geometry only.

---

## Installation

1. Download the latest release from the [Releases](../../releases) page.
2. Extract `gr2_imp_exp.zip` into your Blender addons folder, for example:
   ```
   X:\Steam\steamapps\common\Blender\5.1\scripts\addons_core
   ```
   The path varies depending on your Blender version and installation path.
3. Enable **Import-Export: Granny Runtime Importer/Exporter** in **Edit > Preferences > Add-ons**.

---

## Usage

### Import

**File > Import > Granny 3D (.gr2)**

Select one or more `.gr2` files. Meshes, UVs, materials, normals, and skeletons are imported automatically.

### Export

**File > Export > Granny 3D (.gr2)**

Exports selected mesh objects (or all scene meshes if nothing is selected) to a single `.gr2` file.

---

## Granny DLL

The addon requires `granny2_x64.dll` to function. It is not included in this repository.

The DLL is resolved in this order:

1. The path set in **Edit > Preferences > Add-ons > Granny Runtime Importer/Exporter** (Granny DLL field)
2. The `GRANNY_DLL` environment variable
3. `granny2_x64.dll` placed in the same folder as the addon files

---

## Building / Contributing

No build step is required — the addon is pure Python. Clone the repo, place `granny2_x64.dll` next to the addon files, and install the folder directly in Blender.
