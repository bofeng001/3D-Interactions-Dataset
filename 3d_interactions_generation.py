import os
import bpy
import random
import numpy as np

# Shapes
SHAPES_NUM = [2, 3, 4]
SHAPES = ['SmoothCube_v2', 'SmoothCylinder', 'Sphere'] # toon, glossy, toon

# Materials
MATERIAL = ['Rubber', 'MyMetal']

# Colors
COLORS_NAME = ['Pink', 'Red', 'Blue', 'Green', 'Yellow']
COLORS = {'Pink':[0.8, 0.3, 0.7, 1.0], 'Red':[0.8, 0.2, 0.2, 1.0], 'Blue':[0.2, 0.2, 0.8, 1.0], 'Green':[0.2, 0.8, 0.3, 1.0], 'Yellow':[0.7, 0.8, 0.2, 1.0]}
# Colors = {'Blue':[0, 0, 1, 1], 'Red':[1, 0, 0, 1], 'Green':[0, 0.215861, 0, 1], 'Yellow':[1, 1, 0, 1], 'Brown':[0.376262, 0.0231533, 0.0231534, 1]}

# Size
SCALE = [0.70, 0.75, 0.80] # [0.6, 0.7, 0.8]

# Coordinates (Eliminate Overlapping)
# Set Range: x->(0.6, 1), y->(0.6, 1)
'''
def inital_xy_coordinates():
    coordinates = []

    x_range = round(random.uniform(0.8, 1.5), 2)
    y_range = round(random.uniform(-3.0, -1.0), 2)
    coordinates.append([x_range, y_range])

    x_range = round(random.uniform(-1.5, -0.8), 2)
    y_range = round(random.uniform(-3.0, -1.0), 2)
    coordinates.append([x_range, y_range])

    x_range = round(random.uniform(-1.5, -0.8), 2)
    y_range = round(random.uniform(1.0, 3.0), 2)
    coordinates.append([x_range, y_range])

    x_range = round(random.uniform(0.8, 1.5), 2)
    y_range = round(random.uniform(1.0, 3.0), 2)
    coordinates.append([x_range, y_range])

    return coordinates
'''
def inital_xy_coordinates():
    coordinates = []

    x_range = round(random.uniform(0.8, 2.0), 2)
    y_range = round(random.uniform(-2.0, -0.8), 2)
    coordinates.append([x_range, y_range])

    x_range = round(random.uniform(-2.0, -0.8), 2)
    y_range = round(random.uniform(0.8, 2.0), 2)
    coordinates.append([x_range, y_range])
    
    x_range = round(random.uniform(-2.0, -0.8), 2)
    y_range = round(random.uniform(-2.0, -0.8), 2)
    coordinates.append([x_range, y_range])

    x_range = round(random.uniform(0.8, 2.0), 2)
    y_range = round(random.uniform(0.8, 2.0), 2)
    coordinates.append([x_range, y_range])

    return coordinates

# Container
SHAPES_CONTAINER = []
MATERIAL_CONTAINER = []
INDEX_CONTAINER = {'SmoothCube_v2': 0, 'SmoothCylinder': 0, 'Sphere': 0}


def draw_scene(filepath, shape, material, color, scale, coor, index):

    # draw shape
    shape_filename = filepath + '/shapes/' + shape + '.blend/Object/' + shape
    bpy.ops.wm.append(filename = shape_filename)
    bpy.ops.transform.resize(value=(scale, scale, scale))
    bpy.ops.transform.translate(value=(coor[0], coor[1], scale))

    # Give shape a new name to avoid conflicts
    shape_new_name = '%s_%d' % (shape, index)
    bpy.data.objects[shape].name = shape_new_name
    # Record
    SHAPES_CONTAINER.append(shape_new_name)

    # Set active
    bpy.context.view_layer.objects.active = bpy.data.objects[shape_new_name]

    # Set Physics
    set_physics()

    # load material
    material_filename = filepath + '/materials/' + material + '.blend/NodeTree/' + material
    bpy.ops.wm.append(filename = material_filename)

    mat_count = len(bpy.data.materials)
    bpy.ops.material.new()
    mat = bpy.data.materials['Material']
    mat.name = 'Material_%d' % (mat_count + 1)
    # Record
    MATERIAL_CONTAINER.append(mat.name)

    obj = bpy.context.active_object
    # assert len(obj.data.materials) == 0
    obj.data.materials.append(mat)

    output_node = None
    for n in mat.node_tree.nodes:
        if n.name == 'Material Output':
            output_node = n
            break

    group_node = mat.node_tree.nodes.new('ShaderNodeGroup')
    group_node.node_tree = bpy.data.node_groups[material]

    # Find and set the "Color" input of the new group node
    for inp in group_node.inputs:
        print(inp.name)
        if inp.name in ['Color']:
            inp.default_value = color

    # Wire the output of the new group node to the input of
    # the MaterialOutput node
    mat.node_tree.links.new(
        group_node.outputs['Shader'],
        output_node.inputs['Surface'],
    )

    # Link Material and Shape
    bpy.data.objects[shape_new_name].active_material = bpy.data.materials[mat.name]

    # Deactivate
    bpy.context.view_layer.objects.active = None

def set_physics(): 
    bpy.ops.rigidbody.object_add()
    bpy.context.object.rigid_body.mass = 100

    bpy.context.object.rigid_body.friction = 0
    bpy.context.object.rigid_body.restitution = 1.0

    bpy.context.object.rigid_body.use_margin = True
    bpy.context.object.rigid_body.collision_margin = 0.01

    bpy.context.object.rigid_body.use_deactivation = True
    bpy.context.object.rigid_body.use_start_deactivated = True

def make_circle_coor(radius, y_axis):
    x_axis = np.sqrt(radius ** 2 - y_axis ** 2)
    
    # sign = [-1, 1]
    # x_sign = random.choice(sign)
    # y_sign = random.choice(sign)
    
    # x_axis = x_sign * x_axis
    # y_axis = y_sign * y_axis
    return [x_axis, y_axis]

def clamp(x, minimum, maximum):
    return max(minimum, min(x, maximum))

def camera_view_bounds_2d(scene, cam_ob, me_ob):
    """
    Returns camera space bounding box of mesh object.

    Negative 'z' value means the point is behind the camera.

    Takes shift-x/y, lens angle and sensor size into account
    as well as perspective/ortho projections.

    :arg scene: Scene to use for frame size.
    :type scene: :class:`bpy.types.Scene`
    :arg obj: Camera object.
    :type obj: :class:`bpy.types.Object`
    :arg me: Untransformed Mesh.
    :type me: :class:`bpy.types.Mesh´
    :return: a Box object (call its to_tuple() method to get x, y, width and height)
    :rtype: :class:`Box`
    """

    mat = cam_ob.matrix_world.normalized().inverted()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh_eval = me_ob.evaluated_get(depsgraph)
    me = mesh_eval.to_mesh()
    me.transform(me_ob.matrix_world)
    me.transform(mat)

    camera = cam_ob.data
    frame = [-v for v in camera.view_frame(scene=scene)[:3]]
    camera_persp = camera.type != 'ORTHO'

    lx = []
    ly = []

    for v in me.vertices:
        co_local = v.co
        z = -co_local.z

        if camera_persp:
            if z == 0.0:
                lx.append(0.5)
                ly.append(0.5)
            # Does it make any sense to drop these?
            # if z <= 0.0:
            #    continue
            else:
                frame = [(v / (v.z / z)) for v in frame]

        min_x, max_x = frame[1].x, frame[2].x
        min_y, max_y = frame[0].y, frame[1].y

        x = (co_local.x - min_x) / (max_x - min_x)
        y = (co_local.y - min_y) / (max_y - min_y)

        lx.append(x)
        ly.append(y)

    '''
    min_x = clamp(min(lx), 0.0, 1.0)
    max_x = clamp(max(lx), 0.0, 1.0)
    min_y = clamp(min(ly), 0.0, 1.0)
    max_y = clamp(max(ly), 0.0, 1.0)
    '''
    min_x = min(lx)
    max_x = max(lx)
    min_y = min(ly)
    max_y = max(ly)

    mesh_eval.to_mesh_clear()

    r = scene.render
    fac = r.resolution_percentage * 0.01
    dim_x = r.resolution_x * fac
    dim_y = r.resolution_y * fac

    # Sanity check
    if round((max_x - min_x) * dim_x) == 0 or round((max_y - min_y) * dim_y) == 0:
        return (0, 0, 0, 0)

    return [
        round(min_x * dim_x),            # X
        round(dim_y - max_y * dim_y),    # Y
        round((max_x - min_x) * dim_x),  # Width
        round((max_y - min_y) * dim_y)   # Height
    ]
# print(camera_view_bounds_2d(bpy.context.scene, bpy.context.scene.camera, bpy.context.object))


# Dataset
episode = 100
filepath = '.'
fram_num = 100
# Bounding Box
BOUNDING_BOX = np.zeros((episode, fram_num, 5, 4))
OBJ_PRES = np.zeros((episode, fram_num, 5))
MID_FILE_NAME = 'generated_test_images_1'

for ep in range(episode):

    coors = inital_xy_coordinates()
    shape_num = random.choice(SHAPES_NUM)
    # shape_num = 2
    # print(shape_num)
    
    SHAPES_CONTAINER = []
    MATERIAL_CONTAINER = []
    INDEX_CONTAINER['SmoothCube_v2'] = 0
    INDEX_CONTAINER['SmoothCylinder'] = 0
    INDEX_CONTAINER['Sphere'] = 1

    # Load basic scene
    bpy.ops.wm.open_mainfile(filepath = './base_scene.blend')

    # Make inital ball
    r_initial_ball = 6.0
    # Set input angle
    y_initial_ball = round(random.uniform((0 - r_initial_ball), -1), 2)
    coor_initial_ball = make_circle_coor(r_initial_ball, y_initial_ball)
    color_initial_ball = COLORS[random.choice(COLORS_NAME)]
    scale_initial_ball = random.choice(SCALE)
    draw_scene(filepath, 'Sphere', 'Rubber', color_initial_ball, scale_initial_ball, coor_initial_ball, 1)
    # Make Force Field
    r_force = 7.0
    x_force = (coor_initial_ball[0] / r_initial_ball) * r_force
    y_force = (coor_initial_ball[1] / r_initial_ball) * r_force
    bpy.ops.object.effector_add(type='FORCE', location=(x_force, y_force, scale_initial_ball))
    # Strength
    bpy.context.object.field.strength = 11000
    bpy.context.object.field.use_min_distance = True
    bpy.context.object.field.use_max_distance = True
    bpy.context.object.field.distance_min = 3.5
    bpy.context.object.field.distance_max = 3.5
    bpy.context.object.field.seed = 54


    for sam in range(shape_num):
        # Select Shapes
        shape = random.choice(SHAPES)
        # Select Shapes
        material = random.choice(MATERIAL)
        # Select Colors
        color = COLORS[random.choice(COLORS_NAME)]
        # Select Size
        scale = random.choice(SCALE)
        # Coordinates
        coor = coors[sam]
        # Index
        INDEX_CONTAINER[shape] += 1
        index = INDEX_CONTAINER[shape]

        # Draw Scene
        draw_scene(filepath, shape, material, color, scale, coor, index)

    # Render
    frame_start = 1
    bpy.context.scene.frame_start = frame_start
    frame_end = fram_num
    bpy.context.scene.frame_end = frame_end

    for i in range(frame_start, frame_end + 1):

        # Check the file existence
        # path = '/Users/fubofeng/Desktop/billiard/' + str(ep)
        path = '/data/bf312/3D-Billiard/' + MID_FILE_NAME + '/' + str(ep)
        # path = './output/' + str(ep)

        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)
        file_path = path + '/test_{}.png'.format(i)

        bpy.context.scene.frame_set(i)
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.render.filepath = file_path
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.resolution_x = 128 #perhaps set resolution in code
        bpy.context.scene.render.resolution_y = 128
        bpy.context.scene.render.resolution_percentage = 100
        # bpy.context.scene.render.tile_x = 256
        # bpy.context.scene.render.tile_y = 256
        bpy.context.scene.cycles.blur_glossy = 2.0
        bpy.context.scene.cycles.samples = 512
        bpy.context.scene.cycles.min_light_bounces = 8
        bpy.context.scene.cycles.min_transparent_bounces = 8

        # Turn on GPU
        '''
        cycles_prefs = bpy.context.preferences.addons['cycles'].preferences
        cycles_prefs.compute_device_type = 'CUDA'
        print(cycles_prefs.devices)
        cycles_prefs.devices[0].use= True
        bpy.context.scene.cycles.device = 'GPU'
        '''
        bpy.data.scenes['Scene'].cycles.device = 'GPU'
        print(bpy.data.scenes['Scene'].cycles.device)
        print(bpy.context.preferences.addons['cycles'].preferences.compute_device_type)
        print(bpy.context.preferences.addons['cycles'].preferences.devices)
        for device in bpy.context.preferences.addons['cycles'].preferences.devices:
            print(device)
            print(device.use)

        bpy.context.scene.render.tile_x = 8
        bpy.context.scene.render.tile_y = 8

        # FPS
        bpy.context.scene.render.fps = 16

        bpy.ops.render.render(write_still=True, use_viewport=True)
        '''
        if i < 21:
            bpy.ops.render.render(write_still=False, use_viewport=True)
        else:
            bpy.ops.render.render(write_still=True, use_viewport=True)
        '''

        # Draw bounding box
        bbox_obj = []
        for obj in bpy.data.objects:
            if 'Sphere' in obj.name:
                bbox_obj.append(obj.name)
            if 'SmoothCube' in obj.name:
                bbox_obj.append(obj.name)
            if 'SmoothCylinder' in obj.name:
                bbox_obj.append(obj.name)
        for b in range(len(bbox_obj)):
            bpy.context.view_layer.objects.active = None
            bpy.context.view_layer.objects.active = bpy.data.objects[bbox_obj[b]]
            temp = camera_view_bounds_2d(bpy.context.scene, bpy.context.scene.camera, bpy.context.object)
            print(temp)
            BOUNDING_BOX[ep, (i - 1), b] = np.array(temp)
        # Compute Pres
        for p in range(len(bbox_obj)):
            OBJ_PRES[ep, i - 1, p] = 1.0

        bpy.context.view_layer.update()
        print("Frame %d:" % i)

    # Recycle
    print(MATERIAL_CONTAINER)
    for i in MATERIAL_CONTAINER:
        print(i)
        bpy.data.materials.remove(bpy.data.materials[i])
    for i in SHAPES_CONTAINER:
        bpy.data.objects[i].select_set(False)
    for i in SHAPES_CONTAINER:
        print(i)
        bpy.data.objects[i].select_set(True)
        bpy.ops.object.delete()
    
    # Delete Force Field
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['Field'].select_set(True)
    bpy.ops.object.delete()


# Store Bounding Box and Presence
bbox_path = '/data/bf312/3D-Billiard/' + MID_FILE_NAME + '/bbox.npy'
f = open(bbox_path, 'wb')
np.save(f, BOUNDING_BOX)
f.close()

pres_path = '/data/bf312/3D-Billiard/' + MID_FILE_NAME + '/pres.npy'
f = open(pres_path, 'wb')
np.save(f, OBJ_PRES)
f.close()

