import os

class Customer:
    def __init__(self,cid,customer_type,xpoint,ypoint,customer_demand,customer_ready_time,customer_due_date,customer_service_time):
        self.id=cid
        self.ctype=customer_type
        self.lon=xpoint
        self.lat=ypoint
        self.demand=customer_demand
        self.time_window=(customer_ready_time,customer_due_date)
        self.service_time=customer_service_time
    
    def __eq__(self,customer_id):
        return self.id==customer_id

    def __str__(self):
        return f'{self.id=} {self.ctype=}=>({self.lon},{self.lat})  {self.demand=}  {self.time_window=}  {self.service_time=}'

class RefuelPoint:
    def __init__(self,RefId,RefType,xpoint,ypoint):
        self.id=RefId
        self.lon=xpoint
        self.lat=ypoint
        self.rtype=RefType
    
    def __eq__(self, point_id):
        return self.id==point_id

    def __str__(self):
        return f'{self.id=} {self.rtype}=>({self.lon},{self.lat})'
    

class Problem:
    path_to_datasets=os.path.join('','evrptw_instances')
    def __init__(self,path_to_selected_dataset):
        self.refuel_points=list()
        self.customers=list()
        self.depot=None
        self.settings=dict()
        in_dataset_category='customers'
        with open(os.path.join(Problem.path_to_datasets,path_to_selected_dataset),'r') as RF:
            for i,line in enumerate(RF):
                if i==0: continue

                if line=='':
                    in_dataset_category='cargo_settings'
                elif line.strip().startswith('D'):
                    in_dataset_category='depot'
                elif line.strip().startswith('S'):
                    in_dataset_category='refuel'
                elif line.strip().startswith('c'):
                    in_dataset_category='customers'

                if in_dataset_category=='customers':
                    data=line.split()
                    assert(len(data)==8)
                    self.customers.append(Customer(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7]))
                elif in_dataset_category=='depot':
                    self.refuel_points.append(RefuelPoint(data[0],data[1],data[2],data[3]))
                    self.depot=RefuelPoint(data[0],data[1],data[2],data[3])
                elif in_dataset_category=='refuel':
                    self.refuel_points.append(RefuelPoint(data[0],data[1],data[2],data[3]))
                else:
                    self.settings[line.strip()[0]]=line[line.find('/'):line.find('\\')]
    
    def fuel_capacity(self):
        return self.settings['Q']
    
    def load_capacity(self):
        return self.settings['C']
    
    def fuel_consumption(self):
        return self.settings['r']
    
    def inverse_refueling_rate(self):
        return self.settings['g']
    
    def average_velocity(self):
        return self.settings['v']
