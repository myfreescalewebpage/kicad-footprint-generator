#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(sys.path[0], "..", ".."))
import argparse
import yaml
from KicadModTree import *

# Load parent path of tools
sys.path.append(os.path.join(sys.path[0], "..", "tools"))
from footprint_text_fields import addTextFields

# Function used to generate footprint
def generate_footprint(params, part_params, mpn, configuration):

    # Build footprint name
    fp_name = "Connector_Wuerth_{series_prefix}_{type}_{rows}x{pins:02d}_P{pitch}_{orientation}_{mpn}".format(
        series_prefix=params['series_prefix'], type=params['type'], rows=part_params['rows'], pins=part_params['pins']//2, pitch=params['pitch'], orientation=params['orientation'], mpn=mpn)

    # Create footprint
    kicad_mod = Footprint(fp_name)
    
    # Set SMD attribute if required
    if params['type'] == 'SMD':
        kicad_mod.setAttribute('smd')

    # Description
    kicad_mod.setDescription("Connector Wuerth, WR-PHD {pitch}mm Dual Socket Header Bottom Entry {type}, Wuerth electronics {mpn} ({datasheet}), generated with kicad-footprint-generator".format(
        pitch=params['pitch'], type=params['type'], mpn=mpn, datasheet=part_params['datasheet']))
        
    # Keywords
    kicad_mod.setTags("Connector Wuerth WR-PHD {pitch}mm {mpn}".format(
        pitch=params['pitch'], mpn=mpn))
        
    # Pads
    if params['type'] == 'SMD':
        kicad_mod.append(PadArray(initial=1, start=[0, 0], y_spacing=params['pitch'], pincount=part_params['pins']//2, increment=2, 
            size=[params['pads']['x'], params['pads']['y']], type=Pad.TYPE_SMT, shape=Pad.SHAPE_RECT, layers=['F.Cu', 'F.Mask']))
        kicad_mod.append(PadArray(initial=2, start=[-params['pitch']-2*params['holes']['offset'], 0], y_spacing=params['pitch'], pincount=part_params['pins']//2, increment=2,
            size=[params['pads']['x'], params['pads']['y']], type=Pad.TYPE_SMT, shape=Pad.SHAPE_RECT, layers=['F.Cu', 'F.Mask']))
    else:
        kicad_mod.append(PadArray(initial=1, start=[0, 0], y_spacing=params['pitch'], pincount=part_params['pins']//2, increment=2, 
            size=[params['pads']['diameter'], params['pads']['diameter']], drill=params['pads']['drill'], type=Pad.TYPE_THT, tht_pad1_shape=Pad.SHAPE_RECT, shape=Pad.SHAPE_OVAL, layers=['*.Cu', '*.Mask']))
        kicad_mod.append(PadArray(initial=2, start=[-params['pitch']-2*params['holes']['offset'], 0], y_spacing=params['pitch'], pincount=part_params['pins']//2, increment=2,
            size=[params['pads']['diameter'], params['pads']['diameter']], drill=params['pads']['drill'], type=Pad.TYPE_THT, tht_pad1_shape=Pad.SHAPE_RECT, shape=Pad.SHAPE_OVAL, layers=['*.Cu', '*.Mask']))
    
    # Bottom entry holes
    kicad_mod.append(PadArray(initial="", start=[-params['holes']['offset'], 0], y_spacing=params['pitch'], pincount=part_params['pins']//2, increment="",
        size=params['holes']['drill'], drill=params['holes']['drill'], type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE, layers=Pad.LAYERS_NPTH))
    kicad_mod.append(PadArray(initial="", start=[-params['pitch']-params['holes']['offset'], 0], y_spacing=params['pitch'], pincount=part_params['pins']//2, increment="",
        size=params['holes']['drill'], drill=params['holes']['drill'], type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE, layers=Pad.LAYERS_NPTH))
    
    # Add fab layer
    body_top_left = [(params['width']-params['pitch'])/2-params['holes']['offset'], -params['top']]
    body_bottom_right = [(params['width']-params['pitch'])/2-params['width']-params['holes']['offset'], params['top']+params['pitch']*(part_params['pins']//2-1)]
    kicad_mod.append(RectLine(start=body_top_left, end=body_bottom_right, layer='F.Fab', width=configuration['fab_line_width']))
    
    # Add silkscreen layer
    silk_top_right = [body_top_left[0] + configuration['silk_fab_offset'], body_top_left[1] - configuration['silk_fab_offset']]
    silk_bottom_left = [body_bottom_right[0] - configuration['silk_fab_offset'], body_bottom_right[1] + configuration['silk_fab_offset']]
    # -> Top part
    kicad_mod.append(Line(start=[silk_top_right[0], silk_top_right[1]], end=[silk_bottom_left[0], silk_top_right[1]], layer='F.SilkS', width=configuration['silk_line_width']))
    kicad_mod.append(Line(start=[silk_top_right[0], silk_top_right[1]], end=[silk_top_right[0], silk_top_right[1] + 1.27/2], layer='F.SilkS', width=configuration['silk_line_width']))
    kicad_mod.append(Line(start=[silk_bottom_left[0], silk_top_right[1]], end=[silk_bottom_left[0], silk_top_right[1] + 1.27/2], layer='F.SilkS', width=configuration['silk_line_width']))
    kicad_mod.append(Line(start=[silk_top_right[0], silk_top_right[1] + 1.27/2], end=[silk_top_right[0] + 1.27/2, silk_top_right[1] + 1.27/2], layer='F.SilkS', width=configuration['silk_line_width']))
    # -> Dashes between the pads
    for x in range(0, part_params['pins']//2-1):
        kicad_mod.append(Line(start=[silk_bottom_left[0], 3*params['pitch']/8 + x * params['pitch']], end=[silk_bottom_left[0], 3*params['pitch']/8 + params['pitch']/4 + x * params['pitch']], layer='F.SilkS', width=configuration['silk_line_width']))
        kicad_mod.append(Line(start=[silk_top_right[0], 3*params['pitch']/8 + x * params['pitch']], end=[silk_top_right[0], 3*params['pitch']/8 + params['pitch']/4 + x * params['pitch']], layer='F.SilkS', width=configuration['silk_line_width']))
    # -> Bottom part
    kicad_mod.append(Line(start=[silk_bottom_left[0], silk_bottom_left[1]], end=[silk_bottom_left[0], silk_bottom_left[1] - 1.27/2], layer='F.SilkS', width=configuration['silk_line_width']))
    kicad_mod.append(Line(start=[silk_top_right[0], silk_bottom_left[1]], end=[silk_top_right[0], silk_bottom_left[1] - 1.27/2], layer='F.SilkS', width=configuration['silk_line_width']))
    kicad_mod.append(Line(start=[silk_top_right[0], silk_bottom_left[1]], end=[silk_bottom_left[0], silk_bottom_left[1]], layer='F.SilkS', width=configuration['silk_line_width']))
    
    # Add courtyard layer
    courtyard_top_left = [body_top_left[0] + configuration['courtyard_offset']['connector'], body_top_left[1] - configuration['courtyard_offset']['connector']]
    if params['type'] == 'SMD':
        if courtyard_top_left[0] < 0 + params['pads']['x']/2 + configuration['courtyard_offset']['connector']:
            courtyard_top_left[0] = 0 + params['pads']['x']/2 + configuration['courtyard_offset']['connector']
    else:
        if courtyard_top_left[0] < 0 + params['pads']['diameter']/2 + configuration['courtyard_offset']['connector']:
            courtyard_top_left[0] = 0 + params['pads']['diameter']/2 + configuration['courtyard_offset']['connector']
    courtyard_bottom_right = [body_bottom_right[0] - configuration['courtyard_offset']['connector'], body_bottom_right[1] + configuration['courtyard_offset']['connector']]
    if params['type'] == 'SMD':
        if courtyard_bottom_right[0] > -params['pitch']-2*params['holes']['offset'] - params['pads']['x']/2 - configuration['courtyard_offset']['connector']:
            courtyard_bottom_right[0] = -params['pitch']-2*params['holes']['offset'] - params['pads']['x']/2 - configuration['courtyard_offset']['connector']
    else:
        if courtyard_bottom_right[0] > -params['pitch']-2*params['holes']['offset'] - params['pads']['diameter']/2 - configuration['courtyard_offset']['connector']:
            courtyard_bottom_right[0] = -params['pitch']-2*params['holes']['offset'] - params['pads']['diameter']/2 - configuration['courtyard_offset']['connector']
    kicad_mod.append(RectLine(start=courtyard_top_left, end=courtyard_bottom_right, layer='F.CrtYd', width=configuration['courtyard_line_width']))
    
    # Add texts
    body_edge={'left': body_top_left[0], 'right': body_bottom_right[0], 'top': body_top_left[1], 'bottom': body_bottom_right[1]}
    addTextFields(kicad_mod=kicad_mod, configuration=configuration, body_edges=body_edge, fp_name=fp_name, text_y_inside_position='top',
        courtyard={'top': body_edge['top'] - configuration['courtyard_offset']['connector'], 'bottom': body_edge['bottom'] + configuration['courtyard_offset']['connector'] + 0.2})

    # 3D model definition
    model3d_path_prefix = configuration.get('3d_model_prefix', '${KISYS3DMOD}/')
    model_name = "{model3d_path_prefix:s}Connector_Wuerth_{series_prefix}_Bottom-Entry.3dshapes/{fp_name:s}.wrl".format(
        model3d_path_prefix=model3d_path_prefix, series_prefix=params['series_prefix'], fp_name=fp_name)
    kicad_mod.append(Model(filename=model_name))

    # Create output directory
    output_dir = 'Connector_Wuerth_{series_prefix}_Bottom-Entry.pretty/'.format(series_prefix=params['series_prefix'])
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    filename =  '{output_dir:s}{fp_name:s}.kicad_mod'.format(output_dir=output_dir, fp_name=fp_name)

    # Create footprint
    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile(filename)

if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(description='use config .yaml files to create footprints.')
    parser.add_argument('--global_config', type=str, nargs='?', help='the config file defining how the footprint will look like. (KLC)', default='../tools/global_config_files/config_KLCv3.0.yaml')
    parser.add_argument('--params', type=str, nargs='?', help='the part definition file', default='./wuerth_wr_phd_bottom_entry.yaml')
    args = parser.parse_args()

    # Load configuration
    with open(args.global_config, 'r') as config_stream:
        try:
            configuration = yaml.safe_load(config_stream)
        except yaml.YAMLError as exc:
            print(exc)

    # Load yaml file for this library
    with open(args.params, 'r') as params_stream:
        try:
            params = yaml.safe_load(params_stream)
        except yaml.YAMLError as exc:
            print(exc)

    # Create each part
    for series in params:
        for mpn in params[series]['parts']:
            generate_footprint(params[series], params[series]['parts'][mpn], mpn, configuration)
