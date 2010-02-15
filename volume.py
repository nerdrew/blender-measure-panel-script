import bpy
import Mathutils

def volume(obj):
    #obj.selected = True
    #bpy.ops.object.scale_apply()
    volume = 0.0
    mesh = obj.data.copy()
    mesh.transform(obj.matrix)

    for face in mesh.faces:
        if len(face.verts) > 3: return -1
        volume += mesh.verts[face.verts[0]].co.cross(mesh.verts[face.verts[1]].co).dot(mesh.verts[face.verts[2]].co)
    # blender's natural units are meters. 1m = 1bu. Imperial units use yards.
    return volume / 6 * (bpy.context.scene.unit_settings.scale_length ** 3)
