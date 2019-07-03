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

import bpy
import os
import math

#function to clamp rgb values
def clamp(val, valMin, valMax):
    return max(min(val, valMax), valMin)

def write_mesh(context, info, report_cb):
    scene = bpy.context.scene
    unit = scene.unit_settings
    drone_show = scene.drone_show

    obj_base = scene.object_bases.active
    obj = obj_base.object

    path_mode = 'AUTO'
    export_path = bpy.path.abspath(drone_show.export_path)

    # Create name 'export_path/blendname-objname'
    # add the filename component
    if bpy.data.is_saved:
        name = os.path.basename(bpy.data.filepath)
        name = os.path.splitext(name)[0]
    else:
        name = "untitled"
    # add object name
    name += "-%s" % bpy.path.clean_name(obj.name)

    # first ensure the path is created
    if export_path:
        # this can fail with strange errors,
        # if the dir cant be made then we get an error later.
        try:
            os.makedirs(export_path, exist_ok=True)
        except:
            import traceback
            traceback.print_exc()

    #filepath = os.path.join(export_path, name)
    filepath = export_path


###############
        
    show_length = drone_show.show_length
    number_of_uavs = drone_show.rows_x * drone_show.rows_y # number of uavs in blender scene
    blender_frame_rate = scene.render.fps
    frame_rate = min(4 ,math.floor(drone_show.max_waypoints/(show_length/blender_frame_rate))) #1fps - 4fps

    print("\nBlender frame rate: " + str(blender_frame_rate))
    print("Target frame rate: " + str(frame_rate))

    if (blender_frame_rate % frame_rate != 0):
        nth_frame = int(round(blender_frame_rate / frame_rate))
    else:
        nth_frame = int(blender_frame_rate / frame_rate)

    print("\nCalculating coordinates for every " + str(nth_frame) + "th frame")
    info.append("Calculating coordinates for every " + str(nth_frame) + "th frame")

    exported = False
    for i in range(0, number_of_uavs):
        ob = bpy.data.objects['drone_' + str(i)]
        # create PATH file for every object
        file = open(str(filepath) + '/APM-' + str(i+1) + '.PATH', 'wb')
        # iterate through frames
        for f in range(scene.frame_start, scene.frame_end):
            if (((f-1) % nth_frame) == 0):
                scene.frame_set(f)
                # get scaled position
                x = int(ob.matrix_world.to_translation().x * 100)
                y = int(ob.matrix_world.to_translation().y * 100)
                z = int(ob.matrix_world.to_translation().z * 100)
                # get color
                r = int(clamp(ob.active_material.diffuse_color.r,0.0,1.0) * 255)
                g = int(clamp(ob.active_material.diffuse_color.g,0.0,1.0) * 255)
                b = int(clamp(ob.active_material.diffuse_color.b,0.0,1.0) * 255)
                file.write((x).to_bytes(2, byteorder='little', signed=True))
                file.write((y).to_bytes(2, byteorder='little', signed=True))
                file.write((z).to_bytes(2, byteorder='little', signed=True))
                file.write((r).to_bytes(2, byteorder='little', signed=True))
                file.write((g).to_bytes(2, byteorder='little', signed=True))
                file.write((b).to_bytes(2, byteorder='little', signed=True))
        print("Path APM-"+ str(i+1)+" exported")
        info.append("Path APM-"+ str(i+1)+" exported")

        file.close()

    exported = True
    print("\nFinished path file export")

###############
    if exported == True:
        info.append(("finished"))

        if report_cb is not None:
            report_cb({'INFO'}, "Exported: %r" % filepath)
        return True
    else:
        info.append(("%r fail" % os.path.basename(filepath)))
        return False
