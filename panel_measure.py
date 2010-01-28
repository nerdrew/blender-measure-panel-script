# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.props import *

# Precicion for display of float values.
PRECISION = 6

"""
Name: 'Measure panel'
Blender: 250
"""
__author__ = ["Buerbaum Martin (Pontiac)"]
__url__ = ["http://gitorious.org/blender-scripts/blender-measure-panel-script",
    "http://blenderartists.org/forum/showthread.php?t=177800"]
__version__ = '0.4'
__bpydoc__ = """
Measure panel

This script displays in OBJECT MODE:
* The distance of the 3D cursor to the origin of the
  3D space (if NOTHING is selected).
* The distance of the 3D cursor to the center of an object
  (if exactly ONE object is selected).
* The distance between 2 object centers
  (if exactly TWO objects are selected).
* The surface area of any selected mesh object.

Display in EDIT MODE (Local and Global space supported):
* The distance of the 3D cursor to the origin
  (in Local space it is the object center instead).
* The distance of the 3D cursor to a selected vertex.
* The distance between 2 selected vertices.

Usage:

This functionality can be accessed via the
"Properties" panel in 3D View ([N] key).

It's very helpful to use one or two "Empty" objects with
"Snap during transform" enabled for fast measurement.

Version history:
v0.4 - Calculate & display the surface area of mesh
    objects (local space only right now).
    Expanded global/local switch.
    Made "local" option for 3Dcursor-only in edit mode actually work.
    Fixed local/global calculation for 3Dcursor<->vertex in edit mode.
v0.3.2 - Fixed calculation & display of local/global coordinates.
    The user can now select via dropdown which space is wanted/needed
    Basically this is a bugfix and new feature at the same time :-)
v0.3.1 - Fixed bug where "measure_panel_dist" wasn't defined
    before it was used.
    Also added the distance calculation "origin -> 3D cursor" for edit mode.
v0.3 - Support for mesh edit mode (1 or 2 selected vertices)
v0.2.1 - Small fix (selecting nothing didn't calculate the distance
    of the cursor from the origin anymore)
v0.2 - Distance value is now displayed via a FloatProperty widget (and
    therefore saved to file too right now [according to ideasman42].
    The value is save inside the scene right now.)
    Thanks goes to ideasman42 (Campbell Barton) for helping me out on this.
v0.1 - Initial revision. Seems to work fine for most purposes.

TODO:

There is a random segmentation fault when moving the 3D cursor in edit mode.
Mainly this happens when clicking inside the white circle of the translation
manipulator. There may be other cases though.

See the other "todo" comments below.
"""


# Calculate the surface area of a mesh object.
# Set selectedOnly=1 if you only want to count selected faces.
# Note: Be sure you have updated the mesh data before
#       running this with selectedOnly=1!
# @todo: Support global surface area. (apply matrix before area-calc?)
def objectFaceArea(obj, selectedOnly):
    areaTotal = 0

    if (obj and obj.type == 'MESH' and obj.data):
        mesh = obj.data

        for face in mesh.faces:
            if (not selectedOnly
                or face.selected):
                areaTotal += face.area

        return areaTotal

    # We can not calculate an area for this.
    return -1


class VIEW3D_PT_measure(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Measure"
    bl_default_closed = False

    def draw(self, context):
        from Mathutils import Vector, Matrix

        layout = self.layout

        # Get the active object.
        obj = context.active_object

        # Define a temporary attribute for the distance value
        context.scene.FloatProperty(
            name="Distance",
            attr="measure_panel_dist",
            precision=PRECISION)
        context.scene.FloatProperty(
            #name="Area",
            attr="measure_panel_area1",
            precision=PRECISION)
        context.scene.FloatProperty(
            #name="Area",
            attr="measure_panel_area2",
            precision=PRECISION)

        TRANSFORM = [
            ("measure_global", "Global",
                "Calculate values in global space."),
            ("measure_local", "Local",
                "Calculate values inside the local object space.")]

        # Define dropdown for the global/local setting
        bpy.types.Scene.EnumProperty(
            attr="measure_panel_transform",
            name="Space",
            description="Choose in which space you want to measure.",
            items=TRANSFORM,
            default='measure_global')

        if (context.mode == 'EDIT_MESH'):
            if (obj and obj.type == 'MESH' and obj.data):
                # We need to make sure we have the most recent mesh state!
                # The "selected" attributes need to be correct.
                # For this we exit and re-enter edit mode -> updated selection.
                # @todo: Better way to do this?
                #        This may even cause those Segmentation faults.
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.editmode_toggle()

                # Get mesh data from Object.
                mesh = obj.data

                # Get transformation matrix from object.
                ob_mat = obj.matrix
                # Also make an inversed copy! of the matrix.
                ob_mat_inv = ob_mat.copy()
                Matrix.invert(ob_mat_inv)

                # Get the selected vertices.
                # @todo: Better (more efficient) way to do this?
                verts_selected = [v for v in mesh.verts if v.selected == 1]

                if len(verts_selected) == 0:
                    # Nothing selected.
                    # We measure the distance from the origin to the 3D cursor.
                    test = Vector(context.scene.cursor_location)

                    # Convert to local space, if needed.
                    space = context.scene.measure_panel_transform
                    if space == "measure_local":
                        test = (test - obj.location) * ob_mat_inv

                    context.scene.measure_panel_dist = test.length

                    row = layout.row()
                    row.prop(context.scene, "measure_panel_dist")

                    row = layout.row()
                    row.label(text="", icon='CURSOR')
                    row.label(text="", icon='ARROW_LEFTRIGHT')
                    row.label(text="Origin [0,0,0]")

                    row = layout.row()
                    row.prop(context.scene,
                        "measure_panel_transform",
                        expand=True)

                elif len(verts_selected) == 1:
                    # One vertex selected.
                    # We measure the distance from the
                    # selected vertex object to the 3D cursor.
                    cur_loc = Vector(context.scene.cursor_location)
                    vert_loc = Vector(verts_selected[0].co)

                    # Convert to local or global space.
                    space = context.scene.measure_panel_transform
                    if space == "measure_local":
                        test = vert_loc - (cur_loc - obj.location) * ob_mat_inv
                    else:
                        test = vert_loc * ob_mat + obj.location - cur_loc

                    context.scene.measure_panel_dist = test.length

                    row = layout.row()
                    row.prop(context.scene, "measure_panel_dist")

                    row = layout.row()
                    row.label(text="", icon='CURSOR')
                    row.label(text="", icon='ARROW_LEFTRIGHT')
                    row.label(text="", icon='VERTEXSEL')

                    row = layout.row()
                    row.prop(context.scene,
                        "measure_panel_transform",
                        expand=True)
                    #Dropdown:
                    #row.prop(context.scene, "measure_panel_transform")

                elif len(verts_selected) == 2:
                    # Two vertices selected.
                    # We measure the distance between the
                    # two selected vertices.
                    vert1_loc = Vector(verts_selected[0].co)
                    vert2_loc = Vector(verts_selected[1].co)

                    # Convert to local or global space.
                    space = context.scene.measure_panel_transform
                    if space == "measure_local":
                        test = vert1_loc - vert2_loc
                    else:
                        test = vert1_loc * ob_mat - vert2_loc * ob_mat

                    context.scene.measure_panel_dist = test.length

                    row = layout.row()
                    row.prop(context.scene, "measure_panel_dist")

                    row = layout.row()
                    row.label(text="", icon='VERTEXSEL')
                    row.label(text="", icon='ARROW_LEFTRIGHT')
                    row.label(text="", icon='VERTEXSEL')

                    row = layout.row()
                    row.prop(context.scene,
                        "measure_panel_transform",
                        expand=True)

                else:
                    row = layout.row()
                    row.label(text="Selection not supported.", icon='INFO')

        elif (context.mode == 'OBJECT'):
            # We are working on object mode.

            if (context.selected_objects
                and len(context.selected_objects) > 2):
                # We have more that 2 objects selected...

                mesh_objects = [o for o in context.selected_objects
                    if (obj.type == 'MESH' and obj.data)]

                if (len(mesh_objects) > 0):
                    # ... and at least one of them is a mesh.

                    # Calculate and display surface area of the objects.
                    row = layout.row()
                    row.label(text="Surface area (Local):")

                    row = layout.row()
                    for o in mesh_objects:
                        row = layout.row()
                        row.label(text=o.name, icon='OBJECT_DATA')
                        row.label(text=str(
                            round(objectFaceArea(o, 0), PRECISION)))

            elif (context.selected_objects
                and len(context.selected_objects) == 2):
                # 2 objects selected.
                # We measure the distance between the 2 selected objects.
                obj1 = context.selected_objects[0]
                obj2 = context.selected_objects[1]
                obj1_loc = Vector(obj1.location)
                obj2_loc = Vector(obj2.location)
                test = Vector(obj1.location) - Vector(obj2.location)

                context.scene.measure_panel_dist = test.length

                row = layout.row()
                row.prop(context.scene, "measure_panel_dist")

                row = layout.row()
                row.label(text="", icon='OBJECT_DATA')
                row.prop(obj1, "name", text="")

                row.label(text="", icon='ARROW_LEFTRIGHT')

                row.label(text="", icon='OBJECT_DATA')
                row.prop(obj2, "name", text="")

                # Calculate and display surface area of the objects.
                area1 = objectFaceArea(obj1, 0)
                area2 = objectFaceArea(obj2, 0)
                if (area1 >= 0 or area2 >= 0):
                    row = layout.row()
                    row.label(text="Surface area (Local):")

                if (area1 >= 0):
                    row = layout.row()
                    row.label(text=obj1.name, icon='OBJECT_DATA')
                    context.scene.measure_panel_area1 = area1
                    row.prop(context.scene, "measure_panel_area1")

                if (area2 >= 0):
                    row = layout.row()
                    row.label(text=obj2.name, icon='OBJECT_DATA')
                    context.scene.measure_panel_area2 = area2
                    row.prop(context.scene, "measure_panel_area2")

            elif (obj and  obj.selected
                and context.selected_objects
                and len(context.selected_objects) == 1):
                # One object selected.
                # We measure the distance from the
                # selected & active) object to the 3D cursor.
                cur_loc = Vector(context.scene.cursor_location)
                obj_loc = Vector(obj.location)
                test = obj_loc - cur_loc

                context.scene.measure_panel_dist = test.length

                row = layout.row()
                #row.label(text=str(test.length))
                row.prop(context.scene, "measure_panel_dist")

                row = layout.row()
                row.label(text="", icon='CURSOR')

                row.label(text="", icon='ARROW_LEFTRIGHT')

                row.label(text="", icon='OBJECT_DATA')
                row.prop(obj, "name", text="")

                # Calculate and display surface area of the object.
                area = objectFaceArea(obj, 0)
                if (area >= 0):
                    row = layout.row()
                    row.label(text="Surface area (Local):")

                    row = layout.row()
                    row.label(text=obj.name, icon='OBJECT_DATA')
                    context.scene.measure_panel_area1 = area
                    row.prop(context.scene, "measure_panel_area1")

            elif (not context.selected_objects
                or len(context.selected_objects) == 0):
                # Nothing selected.
                # We measure the distance from the origin to the 3D cursor.
                test = Vector(context.scene.cursor_location)
                context.scene.measure_panel_dist = test.length

                row = layout.row()
                row.prop(context.scene, "measure_panel_dist")

                row = layout.row()
                row.label(text="", icon='CURSOR')
                row.label(text="", icon='ARROW_LEFTRIGHT')
                row.label(text="Origin [0,0,0]")

            else:
                row = layout.row()
                row.label(text="Selection not supported.", icon='INFO')

bpy.types.register(VIEW3D_PT_measure)
