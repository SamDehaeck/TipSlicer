import numpy as np
import cv2

def makeBend(X,Y,startPointX,startPointY,thickness,startAngle,endAngle,bendRad,storeBends=False):
	# remap parameters to indices in the given X, Y matrix
	X_start = X[0,0]
	X_delta = X[0,1]-X[0,0]
	Y_start = Y[0,0]
	Y_delta = Y[1,0]-Y[0,0]

	startX_pix=int(np.round((startPointX-X_start)/X_delta))
	startY_pix=int(np.round((startPointY-Y_start)/Y_delta))

	thick_pix=int(np.round(thickness/X_delta))  # Y_delta and X_delta should be the same

	bendRad_pix=int(np.round(bendRad/X_delta))

	# now calculate the parameters for the ellipse
	centreX=int(startX_pix-bendRad_pix*np.cos(np.deg2rad(startAngle)))
	#print(centreX,startX_pix)
	centreY=int(startY_pix-bendRad_pix*np.sin(np.deg2rad(startAngle)))
	#print(centreY,startY_pix)
	T=np.zeros(X.shape,dtype=np.uint8)
	T=cv2.ellipse(T,(centreX,centreY),(int(bendRad_pix+thick_pix/2),int(bendRad_pix+thick_pix/2)),0,int(startAngle),int(endAngle),100,-1)
	T=cv2.ellipse(T,(centreX,centreY),(int(bendRad_pix-thick_pix/2-1),int(bendRad_pix-thick_pix/2-1)),0,int(startAngle),int(endAngle),0,-1)
	
	# now calculate endPoint
	endX_pix=centreX+(bendRad_pix)*np.cos(np.deg2rad(endAngle))
	endY_pix=centreY+(bendRad_pix)*np.sin(np.deg2rad(endAngle))
	endX=endX_pix*X_delta+X_start
	endY=endY_pix*Y_delta+Y_start
	if (storeBends):
		return T,endX,endY,[centreX,centreY,int(bendRad_pix-thick_pix/2),int(bendRad_pix+thick_pix/2),startAngle,endAngle]
	else:
		return T,endX,endY
	
def makeChannel(X,Y,startPointX,startPointY,endPointX,endPointY,thickness):
	# remap parameters to indices in the given X, Y matrix
	X_start = X[0,0]
	X_delta = X[0,1]-X[0,0]
	Y_start = Y[0,0]
	Y_delta = Y[1,0]-Y[0,0]

	startX_pix=int(np.round((startPointX-X_start)/X_delta))
	startY_pix=int(np.round((startPointY-Y_start)/Y_delta))
	endX_pix=int(np.round((endPointX-X_start)/X_delta))
	endY_pix=int(np.round((endPointY-Y_start)/Y_delta))

	thick_pix=int(np.round(thickness/X_delta))  # Y_delta and X_delta should be the same
	#print(startX_pix,endX_pix,startY_pix,endY_pix)

	angle=np.pi/2.+(np.arctan2((endPointY-startPointY),(endPointX-startPointX)))
	#print(np.rad2deg(angle))
	startX1=int(startX_pix+thick_pix/2*np.cos(angle))
	startY1=int(startY_pix+thick_pix/2*np.sin(angle))
	endX1=int(endX_pix+thick_pix/2*np.cos(angle))
	endY1=int(endY_pix+thick_pix/2*np.sin(angle))

	startX2=int(startX_pix+thick_pix/2*np.cos(angle+np.pi))
	startY2=int(startY_pix+thick_pix/2*np.sin(angle+np.pi))
	endX2=int(endX_pix+thick_pix/2*np.cos(angle+np.pi))
	endY2=int(endY_pix+thick_pix/2*np.sin(angle+np.pi))

	#ps=np.array([[startX_pix,startY_pix],[endX_pix,endY_pix],[endX2,endY2],[startX2,startY2]])
	ps=np.array([[startX1,startY1],[endX1,endY1],[endX2,endY2],[startX2,startY2]])
	T2=np.zeros(X.shape,dtype=np.uint8)
	T2=cv2.fillPoly(T2,[ps],1,100)   # Does not combine the way it should!!!
	return T2,endPointX,endPointY

# I will store the bendinfo by default. Don't use if not necessary..    
def makeOneLoop(X,Y,startX,startY,thickness,chanLen,bendRad,direction=-90):
	bendList=[]
	T,eX,eY=makeChannel(X,Y,startX,startY,startX+np.cos(np.deg2rad(direction+90))*chanLen/2,startY+np.sin(np.deg2rad(direction+90))*chanLen/2,thickness)
	T1,eX,eY,bendInfo=makeBend(X,Y,eX,eY,thickness,180+direction,0+direction,bendRad,True)
	bendList.append(bendInfo)
	T=np.logical_or(T,T1)
	T2,eX,eY=makeChannel(X,Y,eX,eY,eX+np.cos(np.deg2rad(direction-90))*chanLen,eY+np.sin(np.deg2rad(direction-90))*chanLen,thickness)
	T=np.logical_or(T,T2)
	T3,eX,eY,bendInfo=makeBend(X,Y,eX,eY,thickness,180+direction,360+direction,bendRad,True)
	bendList.append(bendInfo)
	T=np.logical_or(T,T3)
	T4,eX,eY=makeChannel(X,Y,eX,eY,eX+np.cos(np.deg2rad(direction+90))*chanLen/2,eY+np.sin(np.deg2rad(direction+90))*chanLen/2,thickness)
	T=np.logical_or(T,T4)
	return T,eX,eY,bendList
	
def makeEntrance(X,Y,startX,startY,thickness,entranceLen,chanLen,bendRad,direction):
	bendList=[]
	T,eX,eY=makeChannel(X,Y,startX,startY,startX+np.cos(np.deg2rad(direction))*entranceLen,startY+np.sin(np.deg2rad(direction))*entranceLen,thickness)
	T1,eX,eY,bendInfo=makeBend(X,Y,eX,eY,thickness,90+direction,0+direction,bendRad,True)
	bendList.append(bendInfo)
	T=np.logical_or(T,T1)
	T2,eX,eY=makeChannel(X,Y,eX,eY,eX+np.cos(np.deg2rad(direction-90))*(chanLen/2-bendRad),eY+np.sin(np.deg2rad(direction-90))*(chanLen/2-bendRad),thickness)
	T=np.logical_or(T,T2)
	T3,eX,eY,bendInfo=makeBend(X,Y,eX,eY,thickness,180+direction,360+direction,bendRad,True)
	bendList.append(bendInfo)
	T=np.logical_or(T,T3)
	T4,eX,eY=makeChannel(X,Y,eX,eY,eX+np.cos(np.deg2rad(direction+90))*chanLen/2,eY+np.sin(np.deg2rad(direction+90))*chanLen/2,thickness)
	T=np.logical_or(T,T4)
	return T,eX,eY,bendList
	
def makeExit(X,Y,startX,startY,thickness,entranceLen,chanLen,bendRad,direction):
	bendList=[]
	T,eX,eY=makeChannel(X,Y,startX,startY,startX+np.cos(np.deg2rad(direction+90))*chanLen/2,startY+np.sin(np.deg2rad(direction+90))*chanLen/2,thickness)
	T1,eX,eY,bendInfo=makeBend(X,Y,eX,eY,thickness,180+direction,0+direction,bendRad,True)
	bendList.append(bendInfo)
	T=np.logical_or(T,T1)
	T2,eX,eY=makeChannel(X,Y,eX,eY,eX+np.cos(np.deg2rad(direction-90))*(chanLen/2-bendRad),eY+np.sin(np.deg2rad(direction-90))*(chanLen/2-bendRad),thickness)
	T=np.logical_or(T,T2)
	T3,eX,eY,bendInfo=makeBend(X,Y,eX,eY,thickness,180+direction,270+direction,bendRad,True)
	bendList.append(bendInfo)
	T=np.logical_or(T,T3)
	T4,eX,eY=makeChannel(X,Y,eX,eY,eX+np.cos(np.deg2rad(direction))*entranceLen,eY+np.sin(np.deg2rad(direction))*entranceLen,thickness)
	T=np.logical_or(T,T4)
	return T,eX,eY,bendList
	
def makeSerpentin(X,Y,startX,startY,thick,entLen,chanLen,bendRad,numberSerp,orientation):
	allBends=[]
	T,eX,eY,bendL=makeEntrance(X,Y,startX,startY,thick,entLen,chanLen,bendRad,orientation)
	allBends.extend(bendL)
	for i in range(numberSerp):
		T2,eX,eY,bendL=makeOneLoop(X,Y,eX,eY,thick,chanLen,bendRad,orientation)
		allBends.extend(bendL)
		T=np.logical_or(T,T2)
	T2,eX,eY,bendL=makeExit(X,Y,eX,eY,thick,entLen,chanLen,bendRad,orientation)
	allBends.extend(bendL)
	T=np.logical_or(T,T2)
	return T,eX,eY,allBends
	
# this makes grooves in the curves of the serpentin, as in the article
# Cook, Fan et Hassan, Journal of Fluids Engineering, 135, 2013
def makeGrooves(T,Xc,Yc,Ri,Ro,phi,omega,theta,doBottom,fillValue=1):
	alpha=np.pi-np.arcsin(Ro*np.sin(theta)/Ri)
	beta=np.pi-theta-alpha

	amGrooves=int(np.round(np.pi/phi))

	Grooves=[]
	if (doBottom):
		for i in np.arange(amGrooves):
			A=np.array([Xc-Ro*np.cos(i*phi),Yc+Ro*np.sin(i*phi)])
			B=np.array([Xc-Ri*np.cos(i*phi+beta),Yc+Ri*np.sin(i*phi+beta)])
			C=np.array([Xc-Ro*np.cos(i*phi+omega),Yc+Ro*np.sin(i*phi+omega)])
			D=np.array([Xc-Ri*np.cos(i*phi+omega+beta),Yc+Ri*np.sin(i*phi+omega+beta)])
			points=np.row_stack((A,B,D,C))
			Grooves.append((points.round()).astype(np.int))
	else:
		for i in np.arange(amGrooves):
			A=np.array([Xc-Ro*np.cos(i*phi),Yc-Ro*np.sin(i*phi)])
			B=np.array([Xc-Ri*np.cos(i*phi+beta),Yc-Ri*np.sin(i*phi+beta)])
			C=np.array([Xc-Ro*np.cos(i*phi+omega),Yc-Ro*np.sin(i*phi+omega)])
			D=np.array([Xc-Ri*np.cos(i*phi+omega+beta),Yc-Ri*np.sin(i*phi+omega+beta)])
			points=np.row_stack((A,B,D,C))
			Grooves.append((points.round()).astype(np.int))
			
	R=cv2.fillPoly(T,Grooves,fillValue)
	return R
	
	
