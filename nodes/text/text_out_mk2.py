# This file is part of project Sverchok. It's copyrighted by the contributors
# recorded in the version control history of the file, available from
# its original location https://github.com/nortikin/sverchok/commit/master
#  
# SPDX-License-Identifier: GPL3
# License-Filename: LICENSE

# made by: Linus Yng, haxed by zeffii to mk2
# pylint: disable=c0326

import io
import csv
import json
import itertools
import pprint
import sverchok

import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty

from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import node_id, multi_socket, updateNode, levels_of_list_or_np

from sverchok.utils.sv_text_io_common import (
    FAIL_COLOR, READY_COLOR, TEXT_IO_CALLBACK,
    get_socket_type,
    new_output_socket,
    name_dict,
    text_modes
)


def get_csv_data(node):
    data_out = []
    for socket in node.inputs:
        if socket.is_linked:
            tmp = socket.sv_get(deepcopy=False)

            # flatten list
            if tmp:
                data_out.extend(list(itertools.chain.from_iterable([tmp])))

    csv_str = io.StringIO()
    writer = csv.writer(csv_str, dialect=node.csv_dialect)
    for row in zip(*data_out):
        writer.writerow(row)

    return csv_str.getvalue()


def get_json_data(node):
    data_out = {}

    socket_order = []
    for socket in node.inputs:
        if socket.is_linked:
            tmp = socket.sv_get(deepcopy=False)
            if tmp:
                link = socket.links[0]
                tmp_name = link.from_node.name + ':' + link.from_socket.name
                name = tmp_name
                j = 1
                while name in data_out:
                    name = tmp_name + str(j)
                    j += 1

                data_out[name] = (get_socket_type(node, socket.name), tmp)
                socket_order.append(name)

    data_out['socket_order'] = socket_order

    if node.json_mode == 'pretty':
        out = json.dumps(data_out, indent=4)
    else:
        out = json.dumps(data_out, separators=(',', ':'))

    return out

def format_to_text(data):
    deptl = levels_of_list_or_np(data)
    out = ''
    if deptl > 1:
        for i, sub_data in enumerate(data):
            if i> 0:
                out += '\n'
            sub_data_len = len(sub_data)-1
            for i, d in enumerate(sub_data):
                out += str(d)
                if i< sub_data_len:
                    out += '\n'

    else:
        for d in data:
            out += str(d)+'\n'
    return out

def get_text_data(node):
    out = []
    if node.inputs['Text'].links:
        data = node.inputs['Text'].sv_get(deepcopy=False)
        out = format_to_text(data)

    return out

def get_sv_data(node):
    out = []
    if node.inputs['Data'].links:
        data = node.inputs['Data'].sv_get(deepcopy=False)
        if node.sv_mode == 'pretty':
            out = pprint.pformat(data)
        else:
            out = str(data)

    return out


class SvTextOutNodeMK2(bpy.types.Node, SverchCustomTreeNode):
    """
    Triggers: Text Out to datablock
    Tooltip: Quickly write data from NodeView to text datablock
    """
    bl_idname = 'SvTextOutNodeMK2'
    bl_label = 'Text Out+'
    bl_icon = 'COPYDOWN'

    sv_modes = [
        ('compact',     'Compact',      'Using str()',        1),
        ('pretty',      'Pretty',       'Using pretty print', 2)]

    json_modes = [
        ('compact',     'Compact',      'Minimal',            1),
        ('pretty',      'Pretty',       'Indent and order',   2)]

    csv_dialects = [
        ('excel',       'Excel',        'Standard excel',     1),
        ('excel-tab',   'Excel tabs',   'Excel tab format',   2),
        ('unix',        'Unix',         'Unix standard',      3)]

    def change_mode(self, context):
        self.inputs.clear()

        if self.text_mode == 'CSV':
            self.inputs.new('SvStringsSocket', 'Col 0')
            self.base_name = 'Col '
        elif self.text_mode == 'JSON':
            self.inputs.new('SvStringsSocket', 'Data 0')
            self.base_name = 'Data '
        elif self.text_mode == 'SV':
            self.inputs.new('SvStringsSocket', 'Data')
        elif self.text_mode == 'TEXT':
            self.inputs.new('SvStringsSocket', 'Text')

    def pointer_update(self, context):
        if self.file_pointer:
            self.text = self.file_pointer.name
        else:
            self.text = ""
        # need to do other stuff?

    text: StringProperty(name='text')
    file_pointer: bpy.props.PointerProperty(type=bpy.types.Text, poll=lambda s, o: True, update=pointer_update)

    text_mode: EnumProperty(items=text_modes, default='CSV', update=change_mode, name="Text format")
    csv_dialect: EnumProperty(items=csv_dialects, default='excel', name="Dialect")
    sv_mode: EnumProperty(items=sv_modes, default='compact', name="Format")
    json_mode: EnumProperty(items=json_modes, default='pretty', name="Format")

    append: BoolProperty(default=False, description="Append to output file")
    base_name: StringProperty(name='base_name', default='Col ')
    multi_socket_type: StringProperty(name='multi_socket_type', default='SvStringsSocket')

    autodump: BoolProperty(default=False, description="autodump", name="auto dump")
    unwrap: BoolProperty(default=True, description="unwrap", name="unwrap")

    def sv_init(self, context):
        self.inputs.new('SvStringsSocket', 'Col 0')

    def draw_buttons(self, context, layout):

        col = layout.column(align=True)
        col.prop(self, 'autodump', toggle=True)
        row = col.row(align=True)
        row.prop_search(self, 'file_pointer', bpy.data, 'texts', text="Write")
        row.operator("text.new", icon="ZOOM_IN", text='')

        row = col.row(align=True)
        row.prop(self, 'text_mode', expand=True)

        row = col.row(align=True)
        if self.text_mode == 'CSV':
            row.prop(self, 'csv_dialect')
        elif self.text_mode == 'SV':
            row.prop(self, 'sv_mode', expand=True)
        elif self.text_mode == 'JSON':
            row.prop(self, 'json_mode', expand=True)

        if not self.autodump:
            col2 = col.column(align=True)
            row = col2.row(align=True)
            row.scale_y = 4.0 if self.prefs_over_sized_buttons else 1
            row.operator(TEXT_IO_CALLBACK, text='D U M P').fn_name = 'dump'
            col2.prop(self, 'append', text="Append")

    def process(self):

        # upgrades older versions of ProfileMK3 to the version that has self.file_pointer
        if self.text and not self.file_pointer:
            text = self.get_bpy_data_from_name(self.text, bpy.data.texts)
            if text:
                self.file_pointer = text

        if self.text_mode in {'CSV', 'JSON'}:
            multi_socket(self, min=1)

        if self.autodump:
            self.append = False
            self.dump()

    # build a string with data from sockets
    def dump(self):
        out = self.get_data()
        if len(out) == 0:
            return False

        if self.file_pointer:
            self.text = self.file_pointer.name

        if not self.append:
            bpy.data.texts[self.text].clear()
        bpy.data.texts[self.text].write(out)
        self.color = READY_COLOR

        return True

    def get_data(self):
        out = ""
        if self.text_mode == 'CSV':
            out = get_csv_data(node=self)
        elif self.text_mode == 'JSON':
            out = get_json_data(node=self)
        elif self.text_mode == 'SV':
            out = get_sv_data(node=self)
        elif self.text_mode == 'TEXT':
            out = get_text_data(node=self)
        return out


def register():
    bpy.utils.register_class(SvTextOutNodeMK2)


def unregister():
    bpy.utils.unregister_class(SvTextOutNodeMK2)
