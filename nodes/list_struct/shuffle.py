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

import random

import bpy
from bpy.props import BoolProperty, IntProperty, StringProperty

from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, changable_sockets
import numpy as np
from numpy import random as np_random, ndarray, array
class ListShuffleNode(bpy.types.Node, SverchCustomTreeNode):
    '''
    Triggers: Randomize list order
    Tooltip: Change randomly the order of the elements in a list\n\t [[0,1,2,3,4,5]] => [[4,2,1,0,5,3]]
    '''
    bl_idname = 'ListShuffleNode'
    bl_label = 'List Shuffle'
    bl_icon = 'OUTLINER_OB_EMPTY'
    sv_icon = 'SV_LIST_SHUFFLE'

    level: IntProperty(name='level_to_Shuffle', default=2, min=1, update=updateNode)
    seed: IntProperty(name='Seed', default=0, update=updateNode)
    typ: StringProperty(name='typ', default='')
    newsock: BoolProperty(name='newsock', default=False)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'level', text="level")
        if 'seed' not in self.inputs:
            layout.prop(self, 'seed', text="Seed")

    def sv_init(self, context):
        self.inputs.new('SvStringsSocket', "data")
        self.inputs.new('SvStringsSocket', "seed").prop_name = 'seed'

        self.outputs.new('SvStringsSocket', 'data')

    def sv_update(self):
        if 'data' in self.inputs and self.inputs['data'].links:
            inputsocketname = 'data'
            outputsocketname = ['data']
            changable_sockets(self, inputsocketname, outputsocketname)

    def process(self):
        if self.outputs[0].is_linked and self.inputs[0].is_linked:

            seed = self.inputs['seed'].sv_get(deepcopy=False)[0][0]

            random.seed(seed)
            np_random.seed(seed)
            data = self.inputs['data'].sv_get(deepcopy=False)
            output = self.shuffle(data, self.level)
            self.outputs['data'].sv_set(output)

    def shuffle(self, data, level):
        level -= 1
        if level:
            if level == 1 and isinstance(data, ndarray):
                out = np.array(data)
                for row in out:
                    np_random.shuffle(row)
                return out
            out = []
            for l in data:
                out.append(self.shuffle(l, level))
            return out
        elif isinstance(data, list):
            l = data.copy()
            random.shuffle(l)
            return l
        elif isinstance(data, tuple):
            data = list(data)
            random.shuffle(data)
            return tuple(data)
        elif isinstance(data, ndarray):
            out = array(data)
            np_random.shuffle(out)
            return out


def register():
    bpy.utils.register_class(ListShuffleNode)


def unregister():
    bpy.utils.unregister_class(ListShuffleNode)
