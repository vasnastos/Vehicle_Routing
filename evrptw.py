import os
import  docplex.cp as cpx

class Customer:
    def __init__(self,customer_id,longtitude,latitude,customer_demand,customer_ready_time,customer_due_date,customer_service_time):
        self.cid=customer_id
        self.lon=longtitude
        self.lat=latitude
        self.demand=customer_demand
        self.time_window=(customer_ready_time,customer_due_date)
        self.service_time=customer_service_time

    def __eq__(self,cid:str):
        return self.id==cid

    def __str__(self):
        return f'Id={self.cid}  Coordinates=({self.lon},{self.lat})  Service Time={self.service_time}  Time Window={self.time_window}'

class RefuelPoint:
    def __init__(self,refuelpoint_id,x,y):
        self.id=refuelpoint_id
        self.lon=x
        self.lat=y

    def __eq__(self,rp_id:str):
        return self.id==rp_id 
    
    def __str__(self):
        return f'Id:{self.id}  Coordinates:({self.lon},{self.lat})'

class Problem:
    @staticmethod
    def get_instances():
        return os.listdir(Problem.path_to_datasets)

    path_to_datasets=os.path.join('','datasets')
    def __init__(self):
        self.customers=list()
        self.service_time=list()
        self.refuel_points=list()
        self.depot=None
        self.Q=None
        self.C=None
        self.r=None
        self.g=None
        self.v=None
    
    def read(self,file_id):
        self.id=file_id.removesuffix('.txt')
        category='Customers'
        with open(os.path.join(Problem.path_to_datasets,file_id),'r') as reader:
            for i,line in enumerate(reader):
                if i==0: continue
                if line.strip()=="":
                    category="Stats"

                if category=="Customers":
                    row=line.strip().split()
                    if row[1]=='d':
                        self.depot=Customer(row[0],row[2],row[3],row[4],row[5],row[6],row[7])
                    elif row[1]=='f':
                        self.refuel_points.append(RefuelPoint(row[0],row[2],row[3]))
                    else:
                        self.customers.append(Customer(row[0],row[2],row[3],row[4],row[5],row[6],row[7]))
                elif category=="Stats":
                    row=line.strip().split('\\')
                    if line.strip().startswith("Q"):
                        self.Q=float(row[1].strip().removesuffix("/"))
                    elif line.strip().startswith("C"):
                        self.C=float(row[1].strip().removesuffix("/"))
                    elif line.strip().startswith("r"):
                        self.r=float(row[1].strip().removesuffix("/"))
                    elif line.strip().startswith("g"):
                        self.g=float(row[1].strip().removesuffix("/"))
                    elif line.strip().startswith("v"):
                        self.v=float(row[1].strip().removesuffix("/"))
    
    def __str__(self):
        return f"Id:{self.id} Customers:{len(self.customers)} Rufuel Points:{len(self.refuel_points)} Depot:{self.depot.time_window}\nQ:{self.Q} C:{self.C}  r:{self.r}  g:{self.g}  v:{self.v}"


if __name__=='__main__':
    instances=Problem.get_instances()



                







