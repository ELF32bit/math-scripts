#!/usr/bin/python
import os, argparse, math

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("input", type=str, help = "|")
parser.add_argument("-n", "--swirl_number", type=int, default=8, help="|")
parser.add_argument("-s", "--swirl_step", type=float, default=0.125, help="|")
parser.add_argument("-b", "--split_border", action="store_true", help="|")
parser.add_argument("-r", "--svg_scale", type=float, default=1000.0, help="|")
parser.add_argument("-g", "--svg_glue_area_length", type=float, default=None, help="|")
parser.add_argument("-i", "--swirl_inset", type=float, default=0.0, help="|")
parser.add_argument("-o", "--output", type=str, help="|")
arguments = parser.parse_args()

# using input file name for the output if not provided
input_basename = os.path.basename(arguments.input)
input_name = os.path.splitext(input_basename)[0]
if arguments.output == None:
	arguments.output = input_name + "-swirly.obj"

def lerp(a, b, w):
	return a + (b - a) * w

def vector3_lerp(a, b, w):
	return [lerp(a[0], b[0], w), lerp(a[1], b[1], w), lerp(a[2], b[2], w)]

def vector3_add(a, b):
	return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]

def vector3_substract(a, b):
	return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]

def vector3_multiply_by_scalar(a, s):
	return [a[0] * s, a[1] * s, a[2] * s]

def vector3_length_squared(v):
	return v[0] * v[0] + v[1] * v[1] + v[2] * v[2]

def vector3_length(v):
	return math.sqrt(vector3_length_squared(v))

def vector3_normalize(v):
	length = vector3_length(v)
	if length:
		return [(v[0] / length), (v[1] / length), (v[2] / length)]
	return [0.0, 0.0, 0.0]

def vector2_add(a, b):
	return [a[0] + b[0], a[1] + b[1]]

def vector2_substract(a, b):
	return [a[0] - b[0], a[1] - b[1]]

def vector2_multiply_by_scalar(a, s):
	return [a[0] * s, a[1] * s]

def vector2_length_squared(v):
	return v[0] * v[0] + v[1] * v[1]

def vector2_length(v):
	return math.sqrt(vector2_length_squared(v))

def vector2_normalize(v):
	length = vector2_length(v)
	if length:
		return [(v[0] / length), (v[1] / length)]
	return [0.0, 0.0]

def triangle_inset(triangle, inset):
	inset_vertices = []
	v01 = vector3_substract(triangle[1], triangle[0])
	v02 = vector3_substract(triangle[2], triangle[0])
	v12 = vector3_substract(triangle[2], triangle[1])
	l01 = vector3_length(v01)
	l02 = vector3_length(v02)
	l12 = vector3_length(v12)
	b01 = vector3_add(triangle[0], vector3_multiply_by_scalar(v01, l02 / (l02 + l12)))
	b02 = vector3_add(triangle[0], vector3_multiply_by_scalar(v02, l01 / (l01 + l12)))
	b12 = vector3_add(triangle[1], vector3_multiply_by_scalar(v12, l01 / (l01 + l02)))
	b01 = vector3_substract(b01, triangle[2])
	b02 = vector3_substract(b02, triangle[1])
	b12 = vector3_substract(b12, triangle[0])
	t01 = vector3_length(vector3_add(b01, v02))
	t02 = vector3_length(vector3_add(b02, v01))
	t12 = vector3_length(vector3_substract(b12, v01))
	lb01 = vector3_length(b01) * (l02 / (l02 + t01))
	lb02 = vector3_length(b02) * (l01 / (l01 + t02))
	lb12 = vector3_length(b12) * (l01 / (l01 + t12))
	b, lb = [b12, b02, b01], [lb12, lb02, lb01]
	for index in range(3):
		adjusted_inset = (lb[index] if inset >= lb[index] else inset)
		inset_direction = vector3_multiply_by_scalar(vector3_normalize(b[index]), adjusted_inset)
		inset_vertex = vector3_add(triangle[index], inset_direction)
		inset_vertices.append(inset_vertex)
	return inset_vertices

def round_to_int(a):
	return (int(math.ceil(a)) if a >= 0.0 else int(math.floor(a)))

try:
	input_file = open(arguments.input, 'r')
except Exception:
	print(f"Failed opening input file: {arguments.input}")
	quit()

input_vertices = []
input_polygons = []
for line in input_file:
	split = line.split()
	if len(split) in [4, 7] and split[0] == "v":
		input_vertices.append([])
		input_vertices[-1].append(float(split[1]))
		input_vertices[-1].append(float(split[2]))
		input_vertices[-1].append(float(split[3]))
	elif len(split) >= 4 and split[0] == "f":
		input_polygons.append([])
		for index in range(1, len(split)):
			face_data = split[index].split("/")
			vertex_index = int(face_data[0]) - 1
			input_polygons[-1].append(input_vertices[vertex_index])

output_polygons = []
for polygon in input_polygons:
	polygon_size = len(polygon)
	output_polygons.append([])

	current_polygon = polygon
	for swirl_index in range(2 * arguments.swirl_number):
		next_polygon = []
		for vertex_index, vertex in enumerate(current_polygon):
			next_vertex_index = (vertex_index + 1) % polygon_size
			next_vertex = current_polygon[next_vertex_index]
			interpolated_vertex = vector3_lerp(vertex, next_vertex, arguments.swirl_step)
			if arguments.split_border and swirl_index == 0:
				interpolated_vertex = vector3_lerp(vertex, next_vertex, arguments.swirl_step / 2.0)
			next_polygon.append(interpolated_vertex)

		for vertex_index in range(polygon_size):
			next_vertex_index = (vertex_index + 1) % polygon_size
			output_polygons[-1].append([])
			output_polygons[-1][-1].append(next_polygon[vertex_index])
			output_polygons[-1][-1].append(current_polygon[next_vertex_index])
			output_polygons[-1][-1].append(next_polygon[next_vertex_index])
			output_polygons[-1][-1].append(swirl_index)

		current_polygon = next_polygon

if arguments.output.endswith(".svg"):
	import pysvg
	from pysvg import structure, builders
	svg_scale = arguments.svg_scale
	svg_glue_area_length = arguments.svg_glue_area_length
	if svg_glue_area_length != None:
		svg_glue_area_length *= svg_scale

	svg_document = pysvg.structure.svg()
	svg_shape_builder = pysvg.builders.ShapeBuilder()
	svg_view_box = [None, None, None, None]

	svg_polygons_points = []
	svg_border_line_points = []
	svg_glue_border_polygons_points = []
	svg_center_polygons_lines_points = []
	for polygon in output_polygons:
		for triangle_data in polygon:
			triangle = triangle_data[0:3]
			triangle_swirl_index = triangle_data[3]

			p1 = [triangle[0][0] * svg_scale, triangle[0][2] * svg_scale]
			p2 = [triangle[1][0] * svg_scale, triangle[1][2] * svg_scale]
			p3 = [triangle[2][0] * svg_scale, triangle[2][2] * svg_scale]

			if triangle_swirl_index == 0:
				svg_border_line_points.append("")
				svg_border_line_points[-1] += f"{p1[0]:g},{p1[1]:g} "
				svg_border_line_points[-1] += f"{p2[0]:g},{p2[1]:g} "
				svg_border_line_points[-1] += f"{p3[0]:g},{p3[1]:g} "
				x = [round_to_int(p1[0]), round_to_int(p2[0])]
				y = [round_to_int(p1[1]), round_to_int(p2[1])]

				if svg_glue_area_length != None:
					edge_direction = vector2_substract(p3, p2)
					normal_direction = vector2_normalize([-edge_direction[1], edge_direction[0]])
					normal_direction = vector2_multiply_by_scalar(normal_direction, svg_glue_area_length)
					pn2, pn3 = vector2_add(p2, normal_direction), vector2_add(p3, normal_direction)
					svg_glue_border_polygons_points.append("")
					svg_glue_border_polygons_points[-1] += f"{p3[0]:g},{p3[1]:g} "
					svg_glue_border_polygons_points[-1] += f"{pn3[0]:g},{pn3[1]:g} "
					svg_glue_border_polygons_points[-1] += f"{pn2[0]:g},{pn2[1]:g} "
					svg_glue_border_polygons_points[-1] += f"{p2[0]:g},{p2[1]:g} "
					x = x + [round_to_int(pn2[0]), round_to_int(pn3[0])]
					y = y + [round_to_int(pn2[1]), round_to_int(pn3[1])]

				if svg_glue_area_length != None:
					edge_direction = vector2_substract(p2, p1)
					normal_direction = vector2_normalize([-edge_direction[1], edge_direction[0]])
					normal_direction = vector2_multiply_by_scalar(normal_direction, svg_glue_area_length)
					pn1, pn2 = vector2_add(p1, normal_direction), vector2_add(p2, normal_direction)
					svg_glue_border_polygons_points.append("")
					svg_glue_border_polygons_points[-1] += f"{p2[0]:g},{p2[1]:g} "
					svg_glue_border_polygons_points[-1] += f"{pn2[0]:g},{pn2[1]:g} "
					svg_glue_border_polygons_points[-1] += f"{pn1[0]:g},{pn1[1]:g} "
					svg_glue_border_polygons_points[-1] += f"{p1[0]:g},{p1[1]:g} "
					x = x + [round_to_int(pn1[0]), round_to_int(pn2[0])]
					y = y + [round_to_int(pn1[1]), round_to_int(pn2[1])]

				if None in svg_view_box:
					svg_view_box[0], svg_view_box[2] = x[0], y[0]
					svg_view_box[1], svg_view_box[3] = x[0], y[0]
				for value in x:
					svg_view_box[0] = min(svg_view_box[0], value)
					svg_view_box[2] = max(svg_view_box[2], value)
				for value in y:
					svg_view_box[1] = min(svg_view_box[1], value)
					svg_view_box[3] = max(svg_view_box[3], value)
			elif triangle_swirl_index % 2 == 1:
				if triangle_swirl_index == 2 * arguments.swirl_number - 1:
					svg_center_polygons_lines_points.append("")
					svg_center_polygons_lines_points[-1] += f"{p1[0]:g},{p1[1]:g} "
					svg_center_polygons_lines_points[-1] += f"{p2[0]:g},{p2[1]:g} "
					svg_center_polygons_lines_points[-1] += f"{p3[0]:g},{p3[1]:g} "
					continue
				svg_polygons_points.append("")
				for vertex in triangle_inset(triangle, arguments.swirl_inset):
					svg_polygons_points[-1] += f"{vertex[0] * svg_scale:g},{vertex[2] * svg_scale:g} "

	if not None in svg_view_box:
		svg_width = svg_view_box[2] - svg_view_box[0]
		svg_document.set_width(svg_width)
		svg_height = svg_view_box[3] - svg_view_box[1]
		svg_document.set_height(svg_height)
		svg_document.set_viewBox(f"{svg_view_box[0]} {svg_view_box[1]} {svg_width} {svg_height}")
		svg_background_rect = svg_shape_builder.createRect(svg_view_box[0], svg_view_box[1], svg_width, svg_height, fill = "white")
		svg_document.addElement(svg_background_rect)
	for svg_border_line_points in svg_border_line_points:
		svg_border_line = svg_shape_builder.createPolyline(points = svg_border_line_points, strokewidth = 2, stroke = "black")
		svg_document.addElement(svg_border_line)
	for svg_glue_border_polygon_points in svg_glue_border_polygons_points:
		svg_glue_border_polygon = svg_shape_builder.createPolygon(points = svg_glue_border_polygon_points, strokewidth = 1, stroke = "black")
		svg_document.addElement(svg_glue_border_polygon)
	for svg_polygon_points in svg_polygons_points:
		svg_polygon = svg_shape_builder.createPolygon(points = svg_polygon_points, strokewidth = 1, fill = "lightgray", stroke = "black")
		svg_document.addElement(svg_polygon)
	for svg_center_polygons_line_points in svg_center_polygons_lines_points:
		svg_center_polygon = svg_shape_builder.createPolyline(points = svg_center_polygons_line_points, strokewidth = 2, stroke = "black")
		svg_document.addElement(svg_center_polygon)
	svg_document.save(arguments.output)
	quit()

# trying to open output file for writing
output_file = None
try:
	output_file = open(arguments.output, "w")
except Exception:
	print(f"Failed writing output file: {arguments.output}")
	quit()

output_index = 0
for polygon in output_polygons:
	for triangle_data in polygon:
		triangle = triangle_data[0:3]
		triangle_swirl_index = triangle_data[3]

		for vertex in triangle:
			output_file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
			output_index += 1

		if triangle_swirl_index % 2 == 0:
			output_file.write("f")
			for vertex_index in range(output_index - 2, output_index + 1):
				output_file.write(f" {vertex_index}")
			output_file.write("\n")
		elif arguments.swirl_inset != 0.0:
			if triangle_swirl_index == 2 * arguments.swirl_number - 1:
				continue
			for vertex in triangle_inset(triangle, arguments.swirl_inset):
				output_file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
				output_index += 1
			i = output_index - 5
			output_file.write(f"f {i + 0} {i + 1} {i + 4} {i + 3}\n")
			output_file.write(f"f {i + 1} {i + 2} {i + 5} {i + 4}\n")
			output_file.write(f"f {i + 2} {i + 0} {i + 3} {i + 5}\n")

# closing output file
output_file.close()
