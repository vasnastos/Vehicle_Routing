import os,math
import  docplex.mp.model as mpx

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
        self.target=None
        self.N=None # Number of Customers
        self.F=None # Number of recharging stations
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
                        self.target=Customer(row[0],row[2],row[3],row[4],row[5],row[6],row[7])
                        self.customers.append(self.depot) # First Customer
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

        self.customers.append(self.target)
        self.all_customers=self.refuel_points
        self.all_customers.extend(self.customers)

        self.CWF=len(self.all_customers)
        self.refuel_point_customers=list(range(0,self.F))
        self.customers_with_depot=list(range(0,self.CWF))
        self.customers_without_depot=list(range(1,self.CWF-1))
        self.customers_with_target_depot=list(range(self.F+1,self.CWF))
        self.customers_with_initial_depot=list(range(self.F,self.CWF-1))
        self.acustomers=list(range(self.F,self.CWF))

    def distance(self,i,j):
        if type(self.all_customers[i])!=Customer or type(self.all_customers[j])!=Customer:
            raise TypeError(f"Type {type(self.all_customers[i])} and {type(self.all_customers[j])} can not calculate eucledian distance")
        return math.sqrt(math.pow(self.all_customers[i].lon-self.all_customers[j].lon,2)+math.pow(self.all_customers[i].lat-self.all_customers[j].lat))

    def __str__(self):
        return f"Id:{self.id} Customers:{len(self.customers)} Rufuel Points:{len(self.refuel_points)} Depot:{self.depot.time_window}\nQ:{self.Q} C:{self.C}  r:{self.r}  g:{self.g}  v:{self.v}"

def solve(problem:"Problem",initial_solution:dict):
    model=mpx.Model(name='Electrical_vehicle_routing_problem')
    # We consider the first node as the depot node
    xvars={(i,j):model.binary(name=f'xvars_{i}_{j}') for i in problem.customers_with_initial_depot for j in problem.customers_with_target_depot}
    tvars={i:model.integer_var(name=f'Arrival_time_at_node_{i}',lb=problem.customers[i].time_window[0],ub=problem.customers[i].time_window[0]) for i in range(problem.CWF)}
    uvars=model.continuous_var_dict(keys=list(range(problem.CWF)))
    yvars={j:model.continuous_var(name=f'remaining_battery_{j}')  for j in problem.customers_with_target_depot}

    for i in range(problem.CWF):
        model.add(xvars[(i,i)]==0,name='same_vertex_non_equality')

    for i in problem.customers_without_depot:
        model.add(
            model.sum([xvars[(i,j)] for j in problem.customers_with_target_depot])==1,
            name='One_placement_constraint'
        )
    
    for i in problem.refuel_point_customers:
        model.add(
            model.sum([xvars[(i,j)] for j in problem.customers_with_target_depot])<=1
        )
    
    for j in problem.customers_without_depot:
        model.add(
            model.sum([xvars[(j,i)] for i in range(problem.customers_with_target_depot)])-
            model.sum([xvars[(i,j)] for i in problem.customers_with_initial_depot])==0
        )
    
    for i in problem.customers_with_initial_depot:
        for j in problem.customers_with_target_depot:
            model.add(
                tvars[i]+(problem.distance(i,j)+problem.all_customers[i].demand)*xvars[(i,j)]-problem.depot.time_window[1]*(1-xvars[(i,j)])<=tvars[j]
            )
    
    for i in problem.refuel_point_customers:
        for j in problem.customers_with_target_depot:
            model.add(
                tvars[i]+problem.distance(i,j)*xvars[(i,j)] * problem.g*(problem.Q-yvars[i])-(problem.depot.time_window[1]+problem.g*problem.Q)*(1-xvars[(i,j)])<=tvars[j]
            )
    




if __name__=='__main__':
    instances=Problem.get_instances()



                







