import time
import pymotor
import os

tctEnable = True

class Stage():
    def __init__(self,device):
        self.Xaxis = device[0]
        self.Yaxis = device[1]
        self.Zaxis = device[2]
        self.flag = 1

    def SetSpeed(self,step,speed):
        self.Xaxis.set_speed(step[0],speed[0])
        self.Yaxis.set_speed(step[1],speed[1])
        self.Zaxis.set_speed(step[2],speed[2])


    def Home(self,motor):
            if tctEnable:
                motor.home()

    def Stop(self):
        if tctEnable:
            self.Xaxis.stop()
            self.Yaxis.stop()
            self.Zaxis.stop()

    '''
    def Limits(self):
        self.Limits = Limits(self)
    '''
    def MoveAB(self,pos_X,pos_Y,pos_Z):
        if tctEnable:
            self.Xaxis.move(pos_X)
            self.Yaxis.move(pos_Y)
            self.Zaxis.move(pos_Z)

    def MoveRE(self,motor,movement):
        UpperLimit = 25000
        LowerLimit = -25000
        currentPos = motor.get_status_position()
        if currentPos + movement > UpperLimit:
            movement = UpperLimit - currentPos
        elif currentPos + movement < LowerLimit:
            movement = LowerLimit - currentPos

        if tctEnable:
            motor.forward(movement)
        time.sleep(0.1)


    def Scan(self,pos_o,dp,Np):
        self.x0 = pos_o[0]
        self.y0 = pos_o[1]
        self.z0 = pos_o[2]
        self.dx = dp[0]
        self.dy = dp[1]
        self.dz = dp[2]
        self.Nx = Np[0]
        self.Ny = Np[1]
        self.Nz = Np[2]
        pos_file = open("file"+str(time.strftime("%Y%m%d%H%M%S", time.gmtime()))+".txt", "w")

        if self.flag == 1:
            self.MoveAB(self.x0,self.y0,self.z0)
            #delay 1 second for motor moving to (x0,y0.z0)
            time.sleep(2)

            # # scan step by step
            # self.flag1 = self.flag2 = -1
            # for self.i in range(0, self.Nz):
            #     self.MoveRE(self.Zaxis, self.dz)
            #     self.flag1 = self.flag1 * (-1)
            #     for self.j in range(0, self.Nx):
            #         self.MoveRE(self.Xaxis, self.flag1 * self.dx)
            #         self.flag2 = self.flag2 * (-1)
            #         for self.k in range(0, self.Ny):
            #             self.MoveRE(self.Yaxis, self.flag2 * self.dy)
            #             #print(self.Xaxis.get_status_position(),self.Yaxis.get_status_position(),self.Zaxis.get_status_position())
            #             print(self.ui.CurrentPosX_2.value(),self.ui.CurrentPosY_2.value(),self.ui.CurrentPosZ_2.value())
            #             self.timer.timeout.connect(self.UpdateDesiredPos)
            #             self.timer.start(100)
            #             #self.UpdateDesiredPos()


            for self.PZ in range(self.z0, self.z0 + ((self.Nz + 1) * self.dz) , self.dz):
                if self.flag == 0:
                    break
                for self.PX in range(self.x0, self.x0 + ((self.Nx + 1) * self.dx) , self.dx):
                    if self.flag == 0:
                        print('####break######')
                        break
                    for self.PY in range(self.y0, self.y0 + ((self.Ny + 1) * self.dy) , self.dy):
                        if self.flag == 0:
                            break
                        self.MoveAB(self.PX, self.PY, self.PZ)
                        print(self.Xaxis.get_status_position(),self.Yaxis.get_status_position(),self.Zaxis.get_status_position())
                        pos_file.write("{x}\t{y}\t{z}".format(x=self.Xaxis.get_status_position(),
                                                              y=self.Yaxis.get_status_position(),
                                                              z=self.Zaxis.get_status_position()))
                        os.chdir("/home/chenlj/Documents/Code/kc705/bin")
                        os.system("SystemTest -c sample_sim.json")
                        time.sleep(2)
                        #self.timer.timeout.connect(self.UpdateDesiredPos)
                        #self.timer.start(100)
                        #time.sleep(0.1)

            pos_file.close()
