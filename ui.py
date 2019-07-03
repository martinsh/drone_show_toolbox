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
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

# Interface for this addon.

import bmesh
from bpy.types import Panel
from . import report


class DroneShowToolBar:
    bl_label = "Drone Show Toolbox"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    _type_to_icon = {
        bmesh.types.BMVert: 'VERTEXSEL',
        bmesh.types.BMEdge: 'EDGESEL',
        bmesh.types.BMFace: 'FACESEL',
        }

    @classmethod


    def poll(cls, context):
        return True
        #obj = context.active_object
        #return obj and obj.type == 'MESH' and context.mode in {'OBJECT','EDIT_MESH'}

    @staticmethod
    def draw_report(layout, context):
        """Display Reports"""
        info = report.info()
        if info:
            obj = context.edit_object

            layout.label("Output:")
            box = layout.box()
            col = box.column(align=False)
            #box.alert = True
            for i, (text) in enumerate(info):
                if obj and data and data[1]:
                    bm_type, bm_array = data
                    col.operator("rone.select_report",
                                 text=text,
                                 icon=DroneShowToolBar._type_to_icon[bm_type]).index = i
                    #layout.operator("mesh.select_non_manifold", text='Non Manifold Extended')
                else:
                    col.label(text)


    def draw(self, context):
        layout = self.layout

        scene = context.scene
        drone_show = scene.drone_show

        # ADD DRONES ROW

        #column -> col = layout.column(align=True)
        #row ----> row = layout.row(align=True)

        row = layout.row()
        row.label("Show Parameters:")

        col = layout.column(align=True)
        col.prop(drone_show, "show_length")
        col.operator("drone.set_timeline", text="Apply to Timeline")
        #col.prop(drone_show, "show_length_t")
        
        #col.prop(drone_show, "drone_fps")
        
        row = layout.row()
        row.label("Add Drones:")
    
        col = layout.column(align=True)
        col.prop(drone_show, "rows_x")
        col.prop(drone_show, "rows_y")
        col.prop(drone_show, "drone_distance")
        col.prop(drone_show, "drone_diameter")
        col.operator("drone.add_drones", text="Add Drones", icon="GROUP_VERTEX")
        col.operator("drone.remove_drones", text="Remove Drones",icon="X")

        row = layout.row()
        row.label("Limits:")

        col = layout.column(align=True)
        col.prop(drone_show, "distance_min")
        col.prop(drone_show, "velocity_max")
        col.prop(drone_show, "max_waypoints")

        row = layout.row()
        row.label("Checks:")
        col = layout.column(align=True)
        col.operator("drone.check_statistics", text="Statiscics")
        col.operator("drone.check_distance", text="Proximity")
        col.operator("drone.check_velocity", text="Velocity")
        col = layout.column()
        col.operator("drone.check_all", text="Check All")

        col = layout.column()
        rowsub = col.row(align=True)
        rowsub.label("Export Drone Paths:")
        #rowsub.prop(drone_show, "use_apply_scale", text="", icon='MAN_SCALE')
        #rowsub.prop(drone_show, "use_export_texture", text="", icon='FILE_IMAGE')
        rowsub = col.row()
        rowsub.prop(drone_show, "export_path", text="")

        rowsub = col.row(align=True)
        rowsub.operator("drone.export", text="Export", icon='EXPORT')

        DroneShowToolBar.draw_report(layout, context)


# So we can have a panel in both object mode and editmode
class DroneShowToolBarObject(Panel, DroneShowToolBar):
    bl_category = "Drone Show"
    bl_idname = "MESH_PT_drone_show_object"
    bl_context = "objectmode"


class DroneShowToolBarMesh(Panel, DroneShowToolBar):
    bl_category = "Drone Show"
    bl_idname = "MESH_PT_drone_show_mesh"
    bl_context = "mesh_edit"
