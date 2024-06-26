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

import bpy
from bpy.props import BoolProperty, IntProperty, StringProperty

from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import (changable_sockets, dataCorrect, updateNode)
from numpy import stack, ndarray, split

def flip(data, level):
    level -= 1
    out = []
    if not level:
        for l in data:
            out.append(flip(l, level))
    else:
        if compatible_arrays(data):
            out = [o for o in stack(data, axis=1)]
        else:
            length = maxlen(data)
            for i in range(length):
                out_ = []
                for l in data:
                    try:
                        out_.append(l[i])
                    except IndexError:
                        continue
                out.append(out_)
    return out

def compatible_arrays(data):
    is_all_np_arrays = all([isinstance(d, ndarray) for d in data])
    return is_all_np_arrays and all([data[i].shape == data[i+1].shape for i in range(len(data[:-1]))])

def maxlen(data):
    le = []
    for l in data:
        le.append(len(l))
    return max(le)

class ListFlipNode(bpy.types.Node, SverchCustomTreeNode):
    '''
    Triggers: Transpose Lists Axis
    Tooltip: Flip axis of lists\n\t[1,2,3],[4,5,6] => [1,4],[2,5],[3,6]
    '''
    bl_idname = 'ListFlipNode'
    bl_label = 'List Flip'
    bl_icon = 'OUTLINER_OB_EMPTY'
    sv_icon = 'SV_LIST_FLIP'

    level: IntProperty(name='level_to_count', default=2, min=0, max=4, update=updateNode)
    typ: StringProperty(name='typ', default='')
    newsock: BoolProperty(name='newsock', default=False)

    def sv_init(self, context):
        self.inputs.new('SvStringsSocket', 'data')
        self.outputs.new('SvStringsSocket', 'data')

    def draw_buttons(self, context, layout):
        layout.prop(self, "level", text="level")

    def sv_update(self):
        inputsocketname = 'data'
        outputsocketname = ['data']
        changable_sockets(self, inputsocketname, outputsocketname)

    def process(self):
        if self.inputs['data'].is_linked and self.outputs['data'].is_linked:
            outEval = self.inputs['data'].sv_get(deepcopy=False)
            #outCorr = dataCorrect(outEval)  # this is bullshit, as max 3 in levels
            levels = self.level - 1
            out = flip(outEval, levels)
            self.outputs['data'].sv_set(out)


def register():
    bpy.utils.register_class(ListFlipNode)


def unregister():
    bpy.utils.unregister_class(ListFlipNode)
