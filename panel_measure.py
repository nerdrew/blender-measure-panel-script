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
__version__ = '0.2.1'
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
v0.2.1 - Small fix (selecting nothing didn't calculate the distance
    of the cursor from the origin anymore)
v0.2 - Distance value is now displayed via a FloatProperty widget (and
    therefore saved to file too right now [according to ideasman42].
    The value is save inside the scene right now.)
    Thanks goes to ideasman42 (Campbell Barton) for helping me out on this.
v0.1 - Initial revision. Seems to work fine for most purposes.
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
        obj = context.object

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
