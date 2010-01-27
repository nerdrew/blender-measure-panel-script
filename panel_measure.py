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

"""
Name: 'Measure panel'
Blender: 250
"""
__author__ = ["Buerbaum Martin (Pontiac)"]
__url__ = ["http://gitorious.org/blender-scripts/blender-measure-panel-script",
    "http://blenderartists.org/forum/showthread.php?t=177800"]
__version__ = '0.3'
__bpydoc__ = """
Measure panel

This script displays the distance:
* of the 3D cursor to the origin of the 3D space (if NOTHING is selected)
* of the 3D cursor to the center of an object
  (if exactly ONE object is selected).
* between 2 object centers (if exactly TWO objects are selected)

Usage:

This functionality can be accessed via the
"Properties" panel in 3D View ([N] key).

It's very helpful to use one or two "Empty" objects with
"Snap during transform" enabled for fast measurement.

Version history:

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
Mainly this happens when clickin inside the white circle of the translation
manipulator.
"""


class VIEW3D_PT_measure(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Measure"
    bl_default_closed = False

    def draw(self, context):
        from Mathutils import Vector

        layout = self.layout

        # Get the active object.
        obj = context.active_object

        if (context.mode == 'EDIT_MESH'):
            if (obj and obj.type == 'MESH' and obj.data):
                # We need to make sure we have the most recent mesh state!
                # The "selected" attributes need to be correct.
                # For this we exit and re-enter edit mode -> updated selection.
                # @todo: Better way to do this?
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.editmode_toggle()

                # Get mesh data from Object.
                mesh = obj.data

                # Get the selected vertices.
                # @todo: Better 8more efficient) way to do this?
                verts_selected = [v for v in mesh.verts if v.selected == 1]

                if len(verts_selected) == 1:
                    # One vertex selected.
                    # We measure the distance from the
                    # selected vertex object to the 3D cursor.
                    cur_loc = Vector(context.scene.cursor_location)
                    vert_loc = Vector(verts_selected[0].co)
                    test = vert_loc - cur_loc

                    context.scene.measure_panel_dist = test.length

                    row = layout.row()
                    row.prop(context.scene, "measure_panel_dist")

                    row = layout.row()
                    row.label(text="", icon='CURSOR')
                    row.label(text="", icon='ARROW_LEFTRIGHT')
                    row.label(text="", icon='VERTEXSEL')

                elif len(verts_selected) == 2:
                    # Two vertices selected.
                    # We measure the distance between the
                    # two selected vertices.
                    vert1_loc = Vector(verts_selected[0].co)
                    vert2_loc = Vector(verts_selected[1].co)
                    test = vert1_loc - vert2_loc

                    context.scene.measure_panel_dist = test.length

                    row = layout.row()
                    row.prop(context.scene, "measure_panel_dist")

                    row = layout.row()
                    row.label(text="", icon='VERTEXSEL')
                    row.label(text="", icon='ARROW_LEFTRIGHT')
                    row.label(text="", icon='VERTEXSEL')

                else:
                    row = layout.row()
                    row.label(text="Selection not supported.", icon='INFO')

        elif (context.mode == 'OBJECT'):
            # Define a temporary attribute for the distance value
            context.scene.FloatProperty(
                name="Distance",
                attr="measure_panel_dist",
                precision=6)

            if (context.selected_objects
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
