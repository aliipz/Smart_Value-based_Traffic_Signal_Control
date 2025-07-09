import os
import random
from SUMOextractor import in_out_nodes



def generate_routes(net, output_path, desnity=800, mini=20, maxi=150):
    # Make sure the directory exists
    os.makedirs(output_path, exist_ok=True)
    rou_path = os.path.join(output_path, f"{net}.rou.xml")
    sumo_home = os.getenv('SUMO_HOME')
    nodes=in_out_nodes(net,sumo_home)
    print(nodes)
    flows = create_flows(nodes,desnity,mini,maxi)
    content = ['''<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">''']

    # Generar cada flujo
    cont=1
    for origin, destination, rate in flows:
        flow_id = f"flow_{cont}"
        cont += 1
        color = random_color()
        content.append(f'  <flow id="{flow_id}" fromJunction="{origin}" toJunction="{destination}" '
                         f'begin="{0}" end="{3600}" period="exp({rate})" color="{color}"/>')

    content.append("</routes>")

    # Guardar el archivo
    with open(rou_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(content))

    print("Generated .rou.xml file at:", output_path)
    crear_sumocfg(net,  output_path)
    print(f"Please remember to move your .rou and .sumocnfg files to your {sumo_home} folder.")


# Generates a .sumocfg file linking the network and routes
def crear_sumocfg(net, output_path,  tiempo_inicio=0, tiempo_fin=3600):

    config_path = os.path.join(output_path, f"{net}.sumocfg")
    net_path=f"{net}.net.xml"
    rou_path= f"{net}.rou.xml"

    # Content of the .sumocfg file
    content = f'''<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="{net_path}"/>
        <route-files value="{rou_path}"/>
    </input>
</configuration>'''

    # Save the .sumocfg file
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Generated .sumocfg file at: {config_path}")


def create_flows(nodes,density,mini,maxi):
    flows=[]
    while(density!=0):
        n = min(random.randint(mini, maxi),density)
        seleccion = random.sample(nodes, 2)
        origen, destino = seleccion
        flujo=[origen,destino,n/3600]
        flows.append(flujo)
        density-=n
    return flows

def rnadom_color():
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    return f"{r},{g},{b}"

if __name__ == "__main__":
   ruta = r"C:\Users\aLICIA\Downloads"
   # generate_routes(network_name, output_path, density, min flow rate, max flow rate)
   generate_routes("small_network",ruta, densidad=400, mini=5,maxi=40)