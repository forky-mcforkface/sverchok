# This file is part of project Sverchok. It's copyrighted by the contributors
# recorded in the version control history of the file, available from
# its original location https://github.com/nortikin/sverchok/commit/master
#  
# SPDX-License-Identifier: GPL3
# License-Filename: LICENSE

import bpy
from bpy.props import FloatProperty, StringProperty, BoolProperty, EnumProperty, IntProperty

from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, ensure_nesting_level, zip_long_repeat, throttle_and_update_node, get_data_nesting_level
from sverchok.utils.surface.core import SvSurface
from sverchok.utils.surface.freecad import is_solid_face_surface, surface_to_freecad
from sverchok.utils.voronoi3d import lloyd_on_fc_face
from sverchok.dependencies import scipy, FreeCAD

if scipy is None or FreeCAD is None:
    add_dummy('SvLloydSolidFaceNode', "Lloyd on Solid Face", 'scipy and FreeCAD')

if FreeCAD is not None:
    import Part

class SvLloydSolidFaceNode(bpy.types.Node, SverchCustomTreeNode):
    """
    Triggers: Lloyd Solid Face
    Tooltip: Redistribute 3D points on the Solid Face object uniformly by use of Lloyd's algorithm
    """
    bl_idname = 'SvLloydSolidFaceNode'
    bl_label = 'Lloyd on Solid Face'
    bl_icon = 'OUTLINER_OB_EMPTY'
    sv_icon = 'SV_VORONOI'

    iterations : IntProperty(
        name = "Iterations",
        description = "Number of Lloyd algorithm iterations",
        min = 0,
        default = 3,
        update = updateNode)

    thickness : FloatProperty(
        name = "Thickness",
        default = 1.0,
        min = 0.0,
        update=updateNode)

    def sv_init(self, context):
        self.inputs.new('SvSurfaceSocket', "SolidFace")
        self.inputs.new('SvVerticesSocket', "Sites")
        self.inputs.new('SvStringsSocket', 'Thickness').prop_name = 'thickness'
        self.inputs.new('SvStringsSocket', 'Iterations').prop_name = 'iterations'
        self.outputs.new('SvVerticesSocket', "Sites")
        self.outputs.new('SvVerticesSocket', "UVPoints")

    def process(self):

        if not any(socket.is_linked for socket in self.outputs):
            return

        surface_in = self.inputs['SolidFace'].sv_get()
        sites_in = self.inputs['Sites'].sv_get()
        iterations_in = self.inputs['Iterations'].sv_get()
        thickness_in = self.inputs['Thickness'].sv_get()

        surface_in = ensure_nesting_level(surface_in, 2, data_types=(SvSurface,))
        input_level = get_data_nesting_level(sites_in)
        sites_in = ensure_nesting_level(sites_in, 4)
        iterations_in = ensure_nesting_level(iterations_in, 2)
        thickness_in = ensure_nesting_level(thickness_in, 2)

        nested_output = input_level > 1

        verts_out = []
        uvpoints_out = []
        for params in zip_long_repeat(surface_in, sites_in, iterations_in, thickness_in):
            new_verts = []
            new_uvpoints = []
            for surface, sites, iterations, thickness in zip_long_repeat(*params):
                if is_solid_face_surface(surface):
                    fc_face = surface.face
                else:
                    fc_face = surface_to_freecad(surface, make_face=True).face

                uvpoints, sites = lloyd_on_fc_face(fc_face, sites, thickness, iterations)

                new_verts.append(sites)
                new_uvpoints.append(uvpoints)
            if nested_output:
                verts_out.append(new_verts)
                uvpoints_out.append(new_uvpoints)
            else:
                verts_out.extend(new_verts)
                uvpoints_out.extend(new_uvpoints)

        self.outputs['Sites'].sv_set(verts_out)
        self.outputs['UVPoints'].sv_set(uvpoints_out)

def register():
    if scipy is not None and FreeCAD is not None:
        bpy.utils.register_class(SvLloydSolidFaceNode)

def unregister():
    if scipy is not None and FreeCAD is not None:
        bpy.utils.unregister_class(SvLloydSolidFaceNode)
