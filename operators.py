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

# All Operator

import bpy
import bmesh

from bpy.types import Operator
from bpy.props import (
        IntProperty,
        FloatProperty,
        )

from . import (
        report,
        )


def clean_float(text):
    # strip trailing zeros: 0.000 -> 0.0
    index = text.rfind(".")
    if index != -1:
        index += 2
        head, tail = text[:index], text[index:]
        tail = tail.rstrip("0")
        text = head + tail
    return text

# ---------------
# Geometry Checks

def execute_check(self, context):
    obj = context.active_object

    info = []
    self.main_check(obj, info)
    report.update(*info)

    multiple_obj_warning(self, context)

    return {'FINISHED'}


def multiple_obj_warning(self, context):
    if len(context.selected_objects) > 1:
        self.report({"INFO"}, "Multiple selected objects. Only the active one will be evaluated")


class DroneSetTimeline(Operator):
    """Ensure minimum thickness"""
    bl_idname = "drone.set_timeline"
    bl_label = "Drone Show Set Timeline"

    def execute(self, context):
        scene = bpy.context.scene
        drone_show = scene.drone_show
        show_length = drone_show.show_length

        scene.frame_start = 0
        scene.frame_end = show_length
        scene.unit_settings.system = 'METRIC'

        return {'FINISHED'}

class DroneCheckStatistics(Operator):
    """Check Drone Show Statistics"""
    bl_idname = "drone.check_statistics"
    bl_label = "Drone Show Check Statistics"

    @staticmethod
    def main_check(obj, info):
        import math
        scene = bpy.context.scene
        drone_show = scene.drone_show
        show_length = drone_show.show_length
        max_waypoints = drone_show.max_waypoints
        blender_frame_rate = scene.render.fps #blender scene framerate
        show_length_h = (float(show_length/blender_frame_rate)/3600) #length in hours
        
        hours = int(show_length_h) #hours to display
        minutes = (show_length_h*60) % 60 #minutes to display
        seconds = (show_length_h*3600) % 60 #seconds to display

        drone_fps = min(4 ,math.floor(max_waypoints/(show_length/blender_frame_rate))) #1fps - 4fps
        drone_waypoints_stored = show_length / (blender_frame_rate/ drone_fps)

        info.append("Blender frame rate: " + str(blender_frame_rate))

        if (blender_frame_rate % drone_fps != 0):
            nth_frame = int(round(blender_frame_rate / drone_fps))
        else:
            nth_frame = int(blender_frame_rate / drone_fps)

        info.append("Calculating waypoints for every " + str(nth_frame) + "th frame")

        info.append(("Num UAVs: %d " % (drone_show.rows_x * drone_show.rows_y)))
        info.append(("Show Length: %d:%02d.%02d (h:m.s) " % (hours, minutes, seconds)))
        info.append(("autopilot framerate: %d fps " % drone_fps))
        info.append(("%d waypoints will be stored in the drone" % drone_waypoints_stored))

    def execute(self, context):
        return execute_check(self, context)

class DroneCheckDistance(Operator):
    """Check geometry for self intersections"""
    bl_idname = "drone.check_distance"
    bl_label = "Check Distance Between Drones"
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def main_check(obj, info):
        import math
        scene = bpy.context.scene
        drone_show = scene.drone_show
        show_length = drone_show.show_length
        distance_min = drone_show.distance_min

        number_of_uavs = drone_show.rows_x * drone_show.rows_y # number of uavs in blender scene
        scene_frames = show_length # length of animation in frames

        d_treshold = distance_min*100 # distance threshold in centimeters 

        blender_frame_rate = scene.render.fps
        drone_fps = min(4 ,math.floor(drone_show.max_waypoints/(show_length/blender_frame_rate))) #1fps - 4fps

        if (blender_frame_rate % drone_fps != 0):
            nth_frame = int(round(blender_frame_rate / drone_fps))
        else:
            nth_frame = int(blender_frame_rate / drone_fps)

        print("\nChecking every " + str(nth_frame) + "th frame")
        info.append("Checking every " + str(nth_frame) + "th frame")
        print("\nRunning distance check\n")
        info.append("Running distance check")

        for i in range(0, number_of_uavs):
            ob = bpy.data.objects['drone_' + str(i)]

            print("\nChecking drone " + str(i))
            info.append("Checking drone " + str(i))

            for f in range(scene.frame_start, scene.frame_end):
                if ((f-1) % nth_frame == 0):
                    scene.frame_set(f)
                    x = int(ob.matrix_world.to_translation().x*100)
                    y = int(ob.matrix_world.to_translation().y*100)
                    z = int(ob.matrix_world.to_translation().z*100)
                    for k in range(i+1, number_of_uavs):
                        if (k != i):
                            ob2 = bpy.data.objects['drone_' + str(k)]
                            x2 = int(ob2.matrix_world.to_translation().x*100)
                            y2 = int(ob2.matrix_world.to_translation().y*100)
                            z2 = int(ob2.matrix_world.to_translation().z*100)
                            dx = x2 - x
                            dy = y2 - y
                            dz = z2 - z
                            d = math.sqrt(dx*dx + dy*dy + dz*dz)
                            if (d < d_treshold):
                                print("Danger! Distance = " + str(round(d/100,2)) + " m between " + str(i) + " and " + str(k) + " on frame " + str(f))
                                info.append("Danger! Distance = " + str(round(d/100,2)) + " m between " + str(i) + " and " + str(k) + " on frame " + str(f))
                        
        print("\nDone checking distance")
        info.append("Done checking distance")

    def execute(self, context):
        return execute_check(self, context)


class DroneCheckVelocity(Operator):
    """Check geometry for self intersections"""
    bl_idname = "drone.check_velocity"
    bl_label = "Check Drone Velocity"
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def main_check(obj, info):
        import math
        scene = bpy.context.scene
        drone_show = scene.drone_show
        show_length = drone_show.show_length

        number_of_uavs = drone_show.rows_x * drone_show.rows_y # number of uavs in blender scene
        scene_frames = show_length # length of animation in frames

        speed_treshold = drone_show.velocity_max # speed treshold in meters per second

        blender_frame_rate = scene.render.fps
        drone_fps = min(4 ,math.floor(drone_show.max_waypoints/(show_length/blender_frame_rate))) #1fps - 4fps

        l_x = 0
        l_y = 0
        l_z = 0

        if (blender_frame_rate % drone_fps != 0):
            nth_frame = int(round(blender_frame_rate / drone_fps))
        else:
            nth_frame = int(blender_frame_rate / drone_fps)

        print("\nChecking every " + str(nth_frame) + "th frame")
        info.append("Checking every " + str(nth_frame) + "th frame")
        print("\nRunning velocity check")
        info.append("Running velocity check")

        for i in range(0, number_of_uavs):
            ob = bpy.data.objects['drone_' + str(i)]
            print("\nChecking drone " + str(i))
            info.append("Checking drone " + str(i))
            for f in range(scene.frame_start, scene.frame_end):
                if ((f-1) % nth_frame == 0):
                    scene.frame_set(f)
                    if (f>nth_frame):
                        x = ob.matrix_world.to_translation().x
                        y = ob.matrix_world.to_translation().y
                        z = ob.matrix_world.to_translation().z
                        dx = l_x - x
                        dy = l_y - y
                        dz = l_z - z
                        d = math.sqrt(dx*dx + dy*dy + dz*dz)
                        s = d * drone_fps
                        if (s > speed_treshold):
                            print("Danger! Speed = " + str(round(s,2)) + " m\s for " + str(i) + " on frame " + str(f))
                            info.append("Danger! Speed = " + str(round(s,2)) + " m\s for " + str(i) + " on frame " + str(f))
                        l_x = x
                        l_y = y
                        l_z = z
                    else:
                        l_x = ob.matrix_world.to_translation().x
                        l_y = ob.matrix_world.to_translation().y
                        l_z = ob.matrix_world.to_translation().z

        print("\nDone checking velocity")
        info.append("Done checking velocity")

    def execute(self, context):
        return execute_check(self, context)

class DroneAddDrones(Operator):
    """Check geometry for self intersections"""
    bl_idname = "drone.add_drones"
    bl_label = "Spawn Drones"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    # ------------------------------
    # Poll
    # ------------------------------
    
    def poll(cls, context):
        scene = bpy.context.scene
        drone_show = scene.drone_show
        if drone_show.drones_added == True:
            return False
        else:
            return True


    def execute(self, context):
        import math
        scene = bpy.context.scene
        drone_show = scene.drone_show
        drones_x = drone_show.rows_x
        drones_y = drone_show.rows_y
        distance_between_drones = drone_show.drone_distance
        drone_diameter = drone_show.drone_diameter

        n = 0
        bpy.ops.object.select_all(action='DESELECT')# Deselect all
        for y in range(drones_y):
            for x in range(drones_x):

                # Create an empty mesh and the object.
                mesh = bpy.data.meshes.new('drone')
                basic_sphere = bpy.data.objects.new('drone_' + str(n), mesh)
                basic_sphere.location[0] = (x - (drones_x - 1) / 2) * distance_between_drones
                basic_sphere.location[1] = (y - (drones_y - 1) / 2) * distance_between_drones
                basic_sphere.location[2] = 0.0
                # Add the object into the scene.
                scene.objects.link(basic_sphere)        
                scene.objects.active = basic_sphere
                basic_sphere.select = True
                basic_sphere.show_name = True

                # Create a material.
                mat = bpy.data.materials.new(name = 'drone_'+ str(n))
         
                # Set some properties of the material.
                mat.diffuse_color = (0., 0., 0.)
                mat.use_shadeless = 1
         
                # Assign the material to the drone.
                mesh.materials.append(mat)

                # Construct the bmesh sphere and assign it to the blender mesh.
                bm = bmesh.new()
                bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, diameter=drone_diameter)
                bm.to_mesh(mesh)
                bm.free()

                #bpy.ops.object.modifier_add(type='SUBSURF')
                bpy.ops.object.shade_smooth()
                #bpy.ops.material.new()

                n += 1

        bpy.ops.object.select_all(action='DESELECT')# Deselect all
        drone_show.drones_added = True
        return {'FINISHED'}


class DroneRemoveDrones(Operator):
    """Check geometry for self intersections"""
    bl_idname = "drone.remove_drones"
    bl_label = "Delete Drones"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    # ------------------------------
    # Poll
    # ------------------------------
    
    def poll(cls, context):
        scene = bpy.context.scene
        drone_show = scene.drone_show
        if drone_show.drones_added == True:
            return True
        else:
            return False


    def execute(self, context):
        import math
        scene = bpy.context.scene
        drone_show = scene.drone_show

        objects = bpy.context.scene.objects
        materials = bpy.data.materials
        meshes = bpy.data.meshes

        #maybe add group instead of object name?
        #remove material data
        for m in bpy.data.materials: 
            if "drone" in m.name:
                m.user_clear()
                materials.remove(m)
        #remove mesh data
        for mesh in bpy.data.meshes:
            if "drone" in mesh.name:
                mesh.user_clear()
                meshes.remove(mesh)
        #remove object data
        for o in objects:
            bpy.ops.object.select_all(action='DESELECT')# Deselect all

            if "drone" in o.name:
                o.select = True
                bpy.ops.object.delete()
        
        drone_show.drones_added = False
        return {'FINISHED'}

class DroneShowCheckAll(Operator):
    """Run all checks"""
    bl_idname = "drone.check_all"
    bl_label = "Drone Show Check All"

    check_cls = (
        DroneCheckStatistics,
        DroneCheckDistance,
        DroneCheckVelocity,
        )

    def execute(self, context):
        obj = context.active_object

        info = []
        for cls in self.check_cls:
            cls.main_check(obj, info)

        report.update(*info)

        multiple_obj_warning(self, context)

        return {'FINISHED'}




# -------------
# Select Report
# ... helper function for info UI

class DroneShowSelectReport(Operator):
    """Select the data associated with this report"""
    bl_idname = "drone.select_report"
    bl_label = "Drone Show Select Report"
    bl_options = {'INTERNAL'}

    index = IntProperty()

    _type_to_mode = {
        bmesh.types.BMVert: 'VERT',
        bmesh.types.BMEdge: 'EDGE',
        bmesh.types.BMFace: 'FACE',
        }

    _type_to_attr = {
        bmesh.types.BMVert: "verts",
        bmesh.types.BMEdge: "edges",
        bmesh.types.BMFace: "faces",
        }

    def execute(self, context):
        obj = context.edit_object
        info = report.info()
        text, data = info[self.index]
        bm_type, bm_array = data

        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(type=self._type_to_mode[bm_type])

        bm = bmesh.from_edit_mesh(obj.data)
        elems = getattr(bm, Print3DSelectReport._type_to_attr[bm_type])[:]

        try:
            for i in bm_array:
                elems[i].select_set(True)
        except:
            # possible arrays are out of sync
            self.report({'WARNING'}, "Report is out of date, re-run check")

        # cool, but in fact annoying
        # bpy.ops.view3d.view_selected(use_all_regions=False)

        return {'FINISHED'}



# ------
# Export

class DroneShowExport(Operator):
    """Export active object using print3d settings"""
    bl_idname = "drone.export"
    bl_label = "Drone Show Export"
    @classmethod
    def poll(cls, context):
        scene = bpy.context.scene
        drone_show = scene.drone_show
        if drone_show.drones_added == True:
            return True
        else:
            return False

    def execute(self, context):
        from . import export

        info = []
        ret = export.write_mesh(context, info, self.report)
        report.update(*info)

        if ret:
            return {'FINISHED'}
        else:
            return {'CANCELLED'}
