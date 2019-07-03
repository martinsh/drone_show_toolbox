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

# <pep8 compliant>

bl_info = {
    "name": "Drone Show Toolbox",
    "author": "Martins Upitis",
    "blender": (2, 65, 0),
    "location": "3D View > Toolbox",
    "description": "Utilities for Drone Show Animation",
    "warning": "",
    "wiki_url": "https://www.basemotion.eu",
    "support": 'COMMUNITY',
    "category": "Animation"}


if "bpy" in locals():
    import importlib
    importlib.reload(ui)
    importlib.reload(operators)
else:
    import bpy
    from bpy.props import (
            StringProperty,
            BoolProperty,
            FloatProperty,
            EnumProperty,
            PointerProperty,
            IntProperty,
            )
    from bpy.types import (
            AddonPreferences,
            PropertyGroup,
            )
    from . import (
            ui,
            operators,
            )

import math


class DroneShowSettings(PropertyGroup):

    export_path = StringProperty(
            name="Export Directory",
            description="Path to directory where the files are created",
            default="//", maxlen=1024, subtype="DIR_PATH",
            )
    rows_x = IntProperty(
            name="Grid X",
            description="Drone count X",
            default=5, min=1, max=100)

    rows_y = IntProperty(
            name="Grid Y",
            description="Drone count Y",
            default=4, min=1, max=100)

    show_length = IntProperty(
            name="Show Length",
            description="Show length in frames",
            default=10000, min=1, max=50000)

    show_length_t = FloatProperty(
            name="Show Length Time",
            description="Show length in seconds",
            unit = 'TIME',
            default=5.0,  # 5min
            min=0.0, max=900.0,
            )

    drone_fps = IntProperty(
            name="Drone Framerate",
            description="framerate in drone",
            default=4, min=1, max=24)

    max_waypoints = IntProperty(
            name="Max Waypoints",
            description="Maximum waypoints stored in drone",
            default=2000, min=1, max=50000)

    drone_distance = FloatProperty(
            name="Grid Spacing",
            description="Distance between drones on starting grid",
            subtype='DISTANCE',
            default=3.0,  # 3m
            min=0.0, max=10.0,
            )

    drone_diameter = FloatProperty(
            name="Drone Diamater",
            description="Preview Diameter of Drone Spheres",
            unit = 'LENGTH',
            default=0.15,  # 
            min=0.0, max=10.0,
            )

    distance_min = FloatProperty(
            name="Min Distance",
            description="Minium allowed proximity distance",
            subtype='DISTANCE',
            default=2.5,  # 3m
            min=0.0, max=10.0,
            )

    velocity_max = FloatProperty(
            name="Max Velocity",
            description="Maximum allowed drone velocity",
            unit='VELOCITY',
            default=3.0,  # 3m/s
            min=0.0, max=10.0,
            )

    drones_added = BoolProperty(
            name="Drones Added",
            description="Are drones in the scene",
            default=False,
            )


# Add-ons Preferences Update Panel

# Define Panel classes for updating
panels = (
    ui.DroneShowToolBarObject,
    ui.DroneShowToolBarMesh,
    )


def update_panel(self, context):
    message = "DroneShow Toolbox: Updating Panel locations has failed"
    try:
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)

        for panel in panels:
            panel.bl_category = context.user_preferences.addons[__name__].preferences.category
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
        pass


class printpreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    category = StringProperty(
                name="Tab Category",
                description="Choose a name for the category of the panel",
                default="Drone Show",
                update=update_panel
                )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column()

        col.label(text="Tab Category:")
        col.prop(self, "category", text="")


classes = (
    ui.DroneShowToolBarObject,
    ui.DroneShowToolBarMesh,

    operators.DroneSetTimeline,
    operators.DroneCheckStatistics,
    operators.DroneCheckDistance,
    operators.DroneCheckVelocity,
    operators.DroneAddDrones,
    operators.DroneRemoveDrones,

    operators.DroneShowCheckAll,

    operators.DroneShowSelectReport,

    operators.DroneShowExport,

    DroneShowSettings,
    printpreferences,
    )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.drone_show = PointerProperty(type=DroneShowSettings)

    update_panel(None, bpy.context)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.drone_show
