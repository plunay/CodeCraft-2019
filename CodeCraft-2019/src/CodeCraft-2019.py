import logging
import sys
from utils import parse_file, parse_answer
import numpy as np

# =============================================================================
# logging.basicConfig(level=logging.DEBUG,
#                     filename='../logs/CodeCraft-2019.log',
#                     format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S',
#                     filemode='a')
# =============================================================================


def main():
# =============================================================================
#     if len(sys.argv) != 5:
#         logging.info('please input args: car_path, road_path, cross_path, answerPath')
#         exit(1)
# =============================================================================

    car_path = sys.argv[1]
    road_path = sys.argv[2]
    cross_path = sys.argv[3]
    answer_path = sys.argv[4]

# =============================================================================
#     logging.info("car_path is %s" % (car_path))
#     logging.info("road_path is %s" % (road_path))
#     logging.info("cross_path is %s" % (cross_path))
#     logging.info("answer_path is %s" % (answer_path))
# =============================================================================
    
    
    CROSSDICT,CARDICT,ROADDICT ={},{},{}
    
    class Car:
        def __init__(self, ID = None,
                     FROM = None,
                     TO = None,
                     SPEED = None,
                     PLANTIME = None):
            self.ID = ID
            self.SPEED = SPEED
            self.FROM = FROM # cross ID
            self.TO = TO # cross ID
            self.PLANTIME = PLANTIME
            # dynamic parameters
            self.state,self.x,self.y = 0, 0, 0 # car state: 0,1,2,3 in carport,waiting,finishing,end
            self.presentRoadID, self.nextCrossId = None, self.FROM
            self.route, self.routeIndex = None, None
            
            self.dijkstraRoute = []
            
            
        def initRoute(self, PLANTIME, route): # load car route to this car
            self.route = []
            self.PLANTIME = PLANTIME
            for i in range(len(route)):
                if i == 0:
                    if self.nextCrossId == ROADDICT[route[i]].FROM:
                        self.route.append(route[i])
                    else:
                        self.route.append(-route[i])
                else:
                    if ROADDICT[route[i]].FROM == ROADDICT[self.route[-1]].TO:
                        self.route.append(route[i])
                    else:
                        self.route.append(-route[i])
            self.route = np.array(self.route)
            
    
    class Road:
        def __init__(self, ID = None,
                     LENGTH = None,
                     SPEED = None,
                     CHANNEL = None,
                     FROM = None,
                     TO = None,
                     ISDUPLEX = None):
            self.ID = ID
            self.LENGTH = LENGTH
            self.SPEED = SPEED
            self.CHANNEL = CHANNEL
            self.FROM = FROM # cross ID
            self.TO = TO # cross ID
            self.ISDUPLEX = ISDUPLEX
            # dynamic parameters
            self.array = np.zeros([self.CHANNEL, self.LENGTH]) # store car ID in array
            self.done = False
            
             
    class Cross:
        def __init__(self, ID = None,
                     UP = None,
                     RIGHT = None,
                     DOWN = None,
                     LEFT = None):
            self.ID = ID
            self.UP = self.checkRoad(UP if UP == 1 or ROADDICT[UP].TO == ID else -UP )
            self.DOWN = self.checkRoad(DOWN if DOWN == 1 or ROADDICT[DOWN].TO == ID else -DOWN)
            self.LEFT = self.checkRoad(LEFT if LEFT == 1 or ROADDICT[LEFT].TO == ID else -LEFT )
            self.RIGHT = self.checkRoad(RIGHT if RIGHT == 1 or ROADDICT[RIGHT].TO == ID else -RIGHT)
            self.IN = np.array([self.UP, self.RIGHT, self.DOWN, self.LEFT])
            #self.IN = self.IN[np.argsort(np.abs(self.IN))] # sort by abs
            
            self.UP_OUT = self.checkRoad(-self.UP if self.UP != 1 else self.UP)
            self.DOWN_OUT = self.checkRoad(-self.DOWN if self.DOWN != 1 else self.DOWN) 
            self.LEFT_OUT = self.checkRoad(-self.LEFT if self.LEFT != 1 else self.LEFT )
            self.RIGHT_OUT = self.checkRoad(-self.RIGHT if self.RIGHT != 1 else self.RIGHT) 
            self.OUT = np.array([self.UP_OUT, self.RIGHT_OUT, self.DOWN_OUT, self.LEFT_OUT])
            
            # dynamic parameters
            self.directionMap = {UP: {RIGHT: 1, DOWN: 2, LEFT: -1}, \
                                 RIGHT: {DOWN: 1, LEFT: 2, UP: -1}, \
                                 DOWN: {LEFT: 1, UP: 2, RIGHT: -1}, \
                                 LEFT: {UP: 1, RIGHT: 2, DOWN: -1}}
            self.carport = {}
            self.left = []
            self.readyCars = []
            self.crossCar = []
            
        def checkRoad(self, roadID):
            if roadID not in ROADDICT:
                return 1
            else:
                return roadID
            
            
    class Dijkstra:
        def __init__(self, FROM,
                     TO,
                     CROSSDICT,
                     ROADDICT):
            self.FROM = FROM
            self.TO = TO
            self.CROSSDICT = CROSSDICT
            self.ROADDICT = ROADDICT
            
            self.disDic = {}
            self.route = {}
            for i in CROSSDICT.keys():
                self.route[i] = ''
                    
        def getdis(self):
            for i in CROSSDICT.keys():
                self.disDic[i] = float('inf')
            self.disDic[self.FROM] = 0
            S = []
            Q = [key for key in CROSSDICT.keys()]
            while Q:
                u = self.nearest(Q, self.disDic)
                S.append(u)
                Q.remove(u)
                for v in self.neighbour(u):
                    if self.disDic[v] > self.disDic[u] + self.w(u, v):
                        self.disDic[v] = self.disDic[u] + self.w(u, v)
                        self.route[v] = self.route[u] + str(u) + ' '
                        
 
            return (self.route[self.TO] + str(self.TO)).split()
                    
        def neighbour(self, u):
            neighbour = []
            for road in CROSSDICT[u].OUT:
                if road != 1:
                    neighbour.append(ROADDICT[road].TO)
            return neighbour
                
        def nearest(self, Q, disDic):
            newDic = {}
            for i in Q:
                newDic[i] = disDic[i]
            nearestVal = min(newDic.values())
            for key in newDic.keys():
                if newDic[key] == nearestVal:
                    return key
        
        def w(self, u, v):
            for road in CROSSDICT[u].OUT:
                if road != 1:
                    if ROADDICT[road].TO == v:
                        return ROADDICT[road].LENGTH
            
        def crossToRoad(self, route):
            route = list(map(int, route))
            routeRoad = []
            for i in range(len(route)-1):
                cross = CROSSDICT[route[i]]
                for roadID in cross.OUT:
                    if roadID != 1 and ROADDICT[roadID].TO == route[i+1]:
                        routeRoad.append(roadID)
            
            return routeRoad
                    
        
        
    
    def test():
        def loadCar():
            for i in car.index:
                CARDICT[i] = Car(i,*(car.loc[i,:]))
        
        def loadRoad():
            for i in road.index:
                ROADDICT[i] = Road(i,*(road.loc[i,:]))
                if road.loc[i].isDuplex == 1:
                    ROADDICT[-i] = Road(-i,*(road.loc[i,:]))
                    ROADDICT[-i].FROM, ROADDICT[-i].TO = ROADDICT[-i].TO, ROADDICT[-i].FROM
                    # exchange from to for -road
        def loadCross():
            for i in cross.index:
                CROSSDICT[i] = Cross(i,*(cross.loc[i,:]))
                
        PATH_CAR = car_path
        PATH_ROAD = road_path
        PATH_CROSS = cross_path
        #PATH_ANSWER = './toyconfig/answer.txt'
    
        road = parse_file(PATH_ROAD)
        cross = parse_file(PATH_CROSS)
        car = parse_file(PATH_CAR)
        # ans = parse_answer(PATH_ANSWER)
        # create road object
        loadRoad()
        # create cross object
        loadCross()
        # create car object
        loadCar()
        # load route to car
    # =============================================================================
    #     for i in ans.index:
    #         CARDICT[i].initRoute(ans.loc[i].StartTime, ans.loc[i].values[1:][ans.loc[i].values[1:]>0]) # del 0
    # =============================================================================
        def caculateOneCAR(CarID):
            car = CARDICT[CarID]
            
            testDijkstra = Dijkstra(car.FROM, car.TO, CROSSDICT, ROADDICT)
            route = testDijkstra.getdis()
            routeRoad = testDijkstra.crossToRoad(route)
            disDic = testDijkstra.disDic
            length = disDic[car.TO]
            
            roadSpeed = []
            for i in routeRoad:
                roadSpeed.append(ROADDICT[i].SPEED)
                

            speed = min(min(roadSpeed), car.SPEED)
            
            time = length//speed + 1 # ceil is better
            
            return np.abs(np.array(routeRoad)).tolist(), time
        
        answer = [[],[],[]]
        
        latestPlanTime = 0
        for carID in CARDICT.keys():
            if CARDICT[carID].PLANTIME > latestPlanTime:
                latestPlanTime = CARDICT[carID].PLANTIME
    
        thisTime = latestPlanTime
        
        
        carlist = []
        for i in CARDICT.keys():
            carlist.append(i)
            
        batchsize = 200
        for i in range(len(carlist)//batchsize):
            batch = carlist[i*batchsize: (i+1)*batchsize]
            batchAnswer = [[],[],[]]
            for carID in batch:
                routeRoad, time = caculateOneCAR(carID)  
                batchAnswer[0].append(CARDICT[carID].ID)
                batchAnswer[1].append(time)
                batchAnswer[2].append(routeRoad)
            #print(i)
            #print(batchAnswer[2])
            thisTime += max(batchAnswer[1])
            
            answer[0].extend(batchAnswer[0])
            answer[1].extend(np.array([thisTime] * batchsize) + 1)
            answer[2].extend(batchAnswer[2])
        
        if len(carlist) % batchsize != 0:
            lastBatch = carlist[-(len(carlist) % batchsize):]
            
            batchAnswer = [[],[],[]]
            for carID in lastBatch:
                routeRoad, time = caculateOneCAR(carID)  
                batchAnswer[0].append(CARDICT[carID].ID)
                batchAnswer[1].append(time)
                batchAnswer[2].append(routeRoad)
            
            thisTime += max(batchAnswer[1])
            
            answer[0].extend(batchAnswer[0])
            answer[1].extend(np.array([thisTime] * len(lastBatch)) + 1)
            answer[2].extend(batchAnswer[2])        

       
# =============================================================================
#         
#         for i in CARDICT.keys():
#             
#             routeRoad, time = caculateOneCAR(i)        
#             answer[0].append(CARDICT[i].ID)
#             answer[1].append(np.array(thisTime) + 1)
#             answer[2].append(routeRoad)
#             
#             thisTime += time
# =============================================================================
            
            
        def writeAnswer(answer):
            fp = open(answer_path, 'w')
            seq = []
            
            for i in range(len(answer[0])):
                route = ', '.join(list(map(str, answer[2][i])))
                seq.append('(%d, %d, %s)\n' %(answer[0][i], answer[1][i], route)) 
    
            fp.writelines(seq)
            
        writeAnswer(answer)
    
    test()


    

# to read input file
# process
# to write output file


if __name__ == "__main__":
    main()