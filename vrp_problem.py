# Solver and problem description for the vehicle routing problem
import os,math
import tkinter as tk
from tkinter import filedialog
from itertools import product
import docplex.mp.model as mpx
from docplex.mp.conflict_refiner import ConflictRefiner
from docplex.mp.relaxer import Relaxer
import gurobipy as grb 



class Customer:
    def __init__(self,customer_id,customer_xcoord,customer_ycoord,customer_demand,customer_ready_time,customer_due_date,customer_service_time):
        self.id=customer_id
        self.coordinates={"x":customer_xcoord,"y":customer_ycoord}
        self.demand=customer_demand
        self.ready_time=customer_ready_time
        self.due_date=customer_due_date
        self.service_time=customer_service_time
    
    def distance(self,other_customer):
        return math.sqrt(math.pow(self.coordinates['x']-other_customer.coordinates['x'],2)+math.pow(self.coordinates['y']+other_customer.coordinates['y'],2))

    def __str__(self):
        return f"{self.id},({self.coordinates['x']},{self.coordinates['y']}),{self.demand},{self.ready_time},{self.due_date},{self.service_time}"


class Problem:
    path_to_solomon_datasets=os.path.join('','solomon_datasets')
    path_to_evrptw_datasets=os.path.join('','EURO_NeurIPS_ORTEC_datasets')

    path_to_datasets=None

    @staticmethod
    def change_path_to_datasets(ui=True,**args):
        if ui:
            root=tk.Tk()
            root.withdraw()
            folder_path=filedialog.askdirectory()
            if folder_path:
                Problem.path_to_datasets=folder_path
        else:
            if 'path' not in args:
                raise ValueError('Ui arg setted to false and no path value provided')

            folder_path=args['path']
            Problem.path_to_datasets=folder_path

    def __init__(self,dataset_name,skiprows=0):
        self.customers=list()
        self.vehicles=None
        self.capacity=None
        self.depot=None

        with open(os.path.join(Problem.path_to_datasets,dataset_name),'r') as reader:
            for row_counter,line in enumerate(reader):
                if row_counter==4:
                    data=line.strip().split()
                    self.vehicles=int(data[0])
                    self.capacity=int(data[1])

                if row_counter<=skiprows:
                    continue
                
                if line.strip()=="": continue
                data=line.strip().split()
                if len(data)!=7: continue
                self.customers.append(Customer(int(data[0]),int(data[1]),int(data[2]),int(data[3]),int(data[4]),int(data[5]),int(data[6])))

        self.depot=self.customers[0]
        self.customers.append(self.depot)

        self.travel_time={i:{j:self.customers[i].distance(self.customers[j])+self.customers[i].service_time if i!=j else 0 for j in range(self.no_customers())} for i in range(self.no_customers())}

    def no_customers(self):
        return len(self.customers)
    
    def statistics(self):
        # Todo DimGkiok
        # Average Demand,StdDemand
        # Average,Std ServiceTime
        # Average,Std TimeWindow
        pass

def solve_vrptw_cplex(problem:Problem,K,timelimit):
    C=range(1,problem.no_customers()-1)
    N=range(problem.no_customers())

    model=mpx.Model(name='VRPModel')
    xvars={(i,j,v):model.binary_var(name=f'c{i}_c{j}_v{v}') for i in N for j in N for v in range(problem.vehicles)}
    service_time={(i,v):model.integer_var(lb=problem.customers[i].ready_time,ub=problem.customers[i].due_date) for i in N for v in range(problem.vehicles)}

    # 1. In each arc only a route should be applied
    for i in C:
        model.add(
            sum([
                xvars[(i,j,v)]
                for j in N
                for v in range(problem.vehicles)
            ])==1
        )
    
    # 2. No customer can loop into itself
    for i in C:
        model.add(
            sum([
                xvars[(i,i,v)]
                for v in range(problem.vehicles)
            ])==0
        )

    # Depot and termination node constraints
    model.add(sum([xvars[(i,0,v)] for i in N for v in range(problem.vehicles)])==0)
    model.add(sum([xvars[(problem.no_customers()-1,j,v)] for j in N for v in range(problem.vehicles)])==0)

    # 3. Capacity constraint
    for v in range(problem.vehicles):
        sum([
            xvars[(i,j,v)] * problem.customers[i].demand
            for i in C
            for j in N
        ])<=problem.capacity
    
    # 4. All vehicles must start from depot
    for v in range(problem.vehicles):
        model.add(
            sum([
                xvars[(0,j,v)]
                for j in N
            ])==1
        )

        model.add(
            sum([
                xvars[(i,problem.no_customers()-1,v)]
                for i in N 
            ])==1
        )

    
    # 5. Incoming and Outcoming vertices
    for v in range(problem.vehicles):
        for cid in C:
            model.add(
                sum([
                    xvars[(i,cid,v)]
                    for i in N
                ])-sum([
                    xvars[(cid,j,v)]
                    for j in N
                ])==0
            )
    
    # 6. Time window constraint
    for i in N:
        for j in N:
            for v in range(problem.vehicles):
                model.add(
                    service_time[(i,v)]+problem.travel_time[i][j]-K*(1-xvars[(i,j,v)])<=service_time[(j,v)]
                )

    # 7. Objective
    objective=sum([
        problem.customers[i].distance(problem.customers[j]) * xvars[(i,j,v)]
        for i in N
        for j in N
        for v in range(problem.vehicles)
    ])

    # 8. Refine and relaxation loop
    ConflictRefiner().refine_conflict(model, display=True)
    Relaxer().relax(model)
    model.print_information()
    model.set_log_output(True)

    model.minimize(objective)
    model.parameters.threads = os.cpu_count()
    model.parameters.timelimit = timelimit
    solution_model=model.solve(log_output=True)
    
    solution={}
    if solution_model:
        for (i,j,v) in list(product(N,N,range(problem.vehicles))):
            if model.solution.get_value(xvars[(i,j,v)])==1:
                solution[(i,j)]=v
    
    return solution,model.objective_value

def solve_per_route_cplex(problem:Problem,solution_hint:dict):
    # TODO nastos vasileios   Optimize a route 
    pass



if __name__=='__main__':
    Problem.change_path_to_datasets(ui=False,path=Problem.path_to_solomon_datasets)
    problem=Problem('c101.txt')

    print(solve_vrptw_cplex(problem,100000,600))