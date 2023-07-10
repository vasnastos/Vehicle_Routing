import os
import networkx as nx

path_to_datasets_euro_neurips = os.path.join('..', 'EURO_NeurIPS_ORTEC_datasets')

class Transform:
    """Used to transform ORTEC instances to Solomon style instances"""
    
    def __init__(self, ds_name):
        """Initiates Transform class and reads dataset"""
        
        dp = True
        self.id = ds_name
        cfp = {}

        with open(os.path.join(path_to_datasets_euro_neurips, ds_name), 'r') as RF:
            for _ in range(8):
                line=RF.readline()
                data=line.split(':')
                cfp[data[0].strip()] = data[1].strip()
            
            content = ''
            edge_node_counter = 0
            self.nodes = {i:{'x':0,'y':0} for i in range(int(cfp['DIMENSION']))}
            self.time_windows = {i:(0,0) for i in range(int(cfp['DIMENSION']))}
            self.service_time = {i:0 for i in range(int(cfp['DIMENSION']))}
            self.demand = {i:0 for i in range(int(cfp['DIMENSION']))}
            self.G = nx.Graph()
            self.G.add_nodes_from([i for i in range(int(cfp['DIMENSION']))])

            for line in RF:
                if line == 'EOF': 
                    break
                
                if line[0].isalpha():
                    content = line.strip()
                    continue
            
                data=line.split()
                if content == 'EDGE_WEIGHT_SECTION':
                    continue
                
                elif content == 'NODE_COORD_SECTION':
                    self.nodes[int(data[0])-1]['x'] = int(data[1])
                    self.nodes[int(data[0])-1]['y'] = int(data[2])
                
                elif content == 'DEMAND_SECTION':
                    self.demand[int(data[0])-1] = int(data[1])
                
                elif content == 'SERVICE_TIME_SECTION':
                    self.service_time[int(data[0])-1] = int(data[1])
                
                elif content == 'TIME_WINDOW_SECTION':
                    self.time_windows[int(data[0])-1] = (int(data[1]), int(data[2]))

        self.vehicles = int(cfp['VEHICLES'])
        self.capacity = int(cfp['CAPACITY'])
        self.customers=list(self.G.nodes)

    def make_file(self):
        with open(os.path.join("..", "Datasets", "euro_neurips_transform", self.id), "w") as WF:
            WF.write(self.id + "\n")
            WF.write("\n")
            WF.write("VEHICLE\n")
            WF.write("NUMBER \t CAPACITY\n")
            WF.write(f"{self.vehicles} \t {self.capacity}\n")
            WF.write("\n")
            WF.write("CUSTOMER\n")
            WF.write("CUST NO.  XCOORD.   YCOORD.    DEMAND   READY TIME  DUE DATE   SERVICE TIME\n")
            WF.write("\n")
            for i in range(len(self.customers)):
                WF.write(f"  {i} \t {self.nodes[i]['x']} \t\t {self.nodes[i]['y']} \t {self.demand[i]} \t {self.time_windows[i][0]} \t\t {self.time_windows[i][1]} \t {self.service_time[i]}\n")


if __name__ == "__main__":
    for dataset in os.listdir(path_to_datasets_euro_neurips):
        transform = Transform(dataset)
        transform.make_file()
        