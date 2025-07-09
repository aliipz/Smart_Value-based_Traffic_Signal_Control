import os
import xml.etree.ElementTree as ET


# Returns a dictionary with each traffic light-controlled intersection as keys,
# and their incoming lanes ordered clockwise starting from the top
def extract(net, sumo_home):
    # Load XML
    path = os.path.join(sumo_home, net + ".net.xml")
    tree = ET.parse(path)
    root = tree.getroot()

    # Dictionary containing information about the edges
    edges_info = {}

    for edge in root.findall('.//edge'):
        edge_id = edge.get('id')
        from_junction = edge.get('from')
        to_junction = edge.get('to')

        lane = edge.find('lane')
        shape = lane.get('shape') if lane is not None else ""

        direccion = compute_direction(shape)

        edges_info[edge_id] = {
            'from': from_junction,
            'to': to_junction,
            'direction': direccion
        }

    roads = {}

    #gets all junction with 4 roads (the ones with traffic lights)
    for junction in root.findall('junction'):
        if junction.get('type') == 'internal':
            continue

        junction_id = junction.get('id')
        inc_lanes = junction.get('incLanes', '')
        inc=inc_lanes.strip().split()
        if(len(inc)<4):
            continue #in-out node
        edges = [None, None, None, None]
        for lane_id in inc:

            edge = lane_id.split('_')[0]
            edge_id = edge.lstrip('-')
            direc=edges_info[edge_id]['direction']
            if("-" in edge):
                direc+=2
            direc=direc%4
            edges[direc] = edge


        roads[junction_id] = edges



    return roads

# Retrieves the entry and exit nodes of the network
def in_out_nodes(net, sumo_home):
    # Load XML
    path = os.path.join(sumo_home, net + ".net.xml")
    tree = ET.parse(path)
    root = tree.getroot()

    # Dictionary containing information about the edges
    edges_info = {}

    for edge in root.findall('.//edge'):
        edge_id = edge.get('id')
        from_junction = edge.get('from')
        to_junction = edge.get('to')

        lane = edge.find('lane')
        shape = lane.get('shape') if lane is not None else ""

        direccion = compute_direction(shape)

        edges_info[edge_id] = {
            'from': from_junction,
            'to': to_junction,
            'direccion': direccion
        }

    roads = {}
    nodes=[]

    for junction in root.findall('junction'):
        if junction.get('type') == 'internal':
            continue  # ignorar junctions internas

        junction_id = junction.get('id')
        inc_lanes = junction.get('incLanes', '')
        inc=inc_lanes.strip().split()
        if(len(inc)<4):
            nodes.append(junction_id)



    return nodes


def compute_direction(shape_str):
    # Retrieve the two coordinate points
    points = shape_str.strip().split()
    if len(points) < 2:
        return "unknown"

    x1, y1 = map(float, points[0].split(",")) # origin node
    x2, y2 = map(float, points[-1].split(",")) # destination node

    dx = x2 - x1
    dy = y2 - y1

    if abs(dx) > abs(dy):
        return 3 if dx > 0 else 1
    else:
        return 2 if dy > 0 else 0