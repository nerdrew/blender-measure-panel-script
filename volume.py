import bpy

def volume(obj):
    obj.selected = True
    bpy.ops.object.scale_apply()
    volume = 0.0
    for face in obj.data.faces:
        if len(face.verts) > 3: return -1
        volume += obj.data.verts[face.verts[0]].co.cross(obj.data.verts[face.verts[1]].co).dot(obj.data.verts[face.verts[2]].co)
    # blender's natural units are meters. 1m = 1bu. Imperial units use yards.
    return volume / 6 * (bpy.context.scene.unit_settings.scale_length ** 3)

