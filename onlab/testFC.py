# Test DBN: use the matrices of weights and biases obtained by MATLAB simulations to generate a DBN
# Output: Error Rate
# Input parameters: 
	#Nodes: Topology of the DBN, i.e. No. of layers and nodes in each layer (Note: This topology should be similar to the topology defined in MATLAB for training.
############################################################
#                                                          #
#                        2018 Ramtin Zand.                 #
#                    ramtinmz@knights.ucf.edu              #
#                                                          #
############################################################
import re
import os
import time
import math
import random
import mapFC
import mapWB

import sys

import subprocess, shlex

start = time.time()
# function to change the input voltage in the neuron.sp file, which includes the probabilistic activation function
def update_neuron (rp,rap):
	ff=open("neuron.sp", "r+")
	i=0
	data= ff.readlines()
	for line in data:
		i+=1
		if  'Rlow' in line:
			data[i-1]='Rlow in2 input ' + str(rp) +'\n'
		if  'Rhigh' in line:
			data[i-1]='Rhigh input out ' + str(rap) +'\n'

	ff.seek(0)
	ff.truncate()
	ff.writelines(data)
	ff.close()



#function to find the measured average voltage or power in the output text file genrated by SPICE(Specifically for MEAUSURE FROM-TO)
def findavg (line):
	i=0
	m=0
	while (m == 0):
		i+=1;
		if (line[i]=='='):
			s1=i+1;
		if (line[i]=='f'):
			s2=i-1;
			m=1;
		if (line[i]=='\n'):
			s2=i;
			m=1;
	volt=line[s1:s2]
	volt=volt.replace(" ","")
	volt=volt.replace("m","e-3")
	volt=volt.replace("u","e-6")
	volt=volt.replace("n","e-9")
	volt=volt.replace("p","e-12")
  	volt=volt.replace("f","e-15")
  	volt=volt.replace("a","e-18")
	return volt

#function to find the measured voltage in the output2 text file genrated by SPICE (Specifically for MEASURE AT)
def findat (line):
	i=0
	m=0
	while (m == 0):
		i+=1;
		if (line[i]=='='):
			s1=i+1;
		if (line[i]=='w'):
			s2=i-1;
			m=1;
		if (line[i]=='\n'):
			s2=i;
			m=1;
	volt=line[s1:s2]
	volt=volt.replace(" ","")
	volt=volt.replace("m","e-3")
	volt=volt.replace("u","e-6")
	volt=volt.replace("n","e-9")
	volt=volt.replace("p","e-12")
  	volt=volt.replace("f","e-15")
  	volt=volt.replace("a","e-18")  
	return volt

#pbit=open("pbitin.txt", "r+")
#pbit.truncate()
#pbit.close


f=open("../../testinput.txt", "r")   # testinput.text is the output of the MATLAB code, which includes the test images in the MNIST Dataset
f2=open("../../testlabel.txt", "r")  # testlabel.text is the output of the MATLAB code, which includes the labels of the test images in the MNIST Dataset
in_data=f.readlines()
label=f2.readlines()
noise=0.000;   #maximum noise amplitude in Volt
weight_var=0.0; #variation in the resistance of the synapses in Kohms
testnum=200
firstimage=int(sys.argv[1])   #0
Vdd=0.8
nodes=[784, 16, 10]
lMTJ=50e-9
wMTJ=30e-9
RA=7e-12
TMR=200
err=[] 
avgpower=0
avgpwrneuron=0
length=len(nodes)
power=0
total_power=0
AreaMTJ=(math.pi)*lMTJ*wMTJ/4
rp=RA/AreaMTJ
# print(rp)
rap=(1+(TMR/100.0))*rp
# print(rap)
update_neuron(rp,rap)
mapWB.mapWB(length,rp,rap)
for ii in range(testnum):
	# print(ii+1)
	out_list=[]
	out2_list=[]
	#power=0	
	#pwrneuron=0
	i=ii+firstimage
	err.append(int(0))	
	input_data=in_data[(i*nodes[0]):((i+1)*nodes[0])]
	label_data=label[(i*nodes[len(nodes)-1]):((i+1)*nodes[len(nodes)-1])]
	g=open("singletestinput1.txt", "w")
	for j2 in range(nodes[0]):
		g.write("%f\n"%((float(input_data[j2])*Vdd*2)-Vdd))	
		#g.write("%f\n"%(float(input_data[j2])*Vdd))	
	g.close()
	mapFC.mapFC(nodes,length,weight_var)
	#os.system('hspice classifier.sp >output.txt')
	#h=open("output.txt", "r")
	proc = subprocess.Popen(
	 	shlex.split('bash -c \'hspice classifier.sp 2>error.txt | grep "vout\|pwr\|powr"\''),
		stdout = subprocess.PIPE,
		close_fds = True)
	proc.wait()
	# h = os.popen('hspice classifier.sp -mt 6 | grep "vout\|pwr\|powr"')
	
	for l in proc.stdout:
		if  'vout' in l:
			z=findat(l)
			out_list.append(z)
		if  'pwr' in l:
			z2=findavg(l)
			power+=float(z2)
		if  'powr' in l:
			z3=findavg(l)
			total_power+=float(z3)
	# print(out_list)
	for i in range(len(out_list)):
		out_list[i]=float(out_list[i])
	# print(out_list)	
	list_max = max(out_list)                      # find the highest output of the neurons in each layer					
	# print(list_max)	
	for i2 in range (nodes[len(nodes)-1]):
		if (out_list[i2]==list_max):          # the neuron generating maximum output value represents the corrosponding class
			out_list[i2]=1
		else:
			out_list[i2]=0
		if (err[ii]==0):		
			if (out_list[i2] != int(label_data[i2])):
				err[ii]=1
	# print(out_list)	
	# print ("sum error= %d"%(sum(err)))
	# f1=open("error.txt", "w")
	# f1.write("Number of wrong recognitions in %d input image(s) = %d\n"% ((ii+1), sum(err)))
	# f1.close()


f.close()
f2.close()

print("error rate = %f"%(sum(err)/float(testnum)))   #calculate error rate
print("average vdd power = %f"%(power/float(testnum)))   #calculate average power consumption
print("average total power = %f"%(total_power/float(testnum)))   #calculate average power consumption

#print("average neuron power = %f"%(avgpwrneuron/float(testnum)))   #calculate average neuronpower consumption

#measure the run time
end = time.time()
second=math.floor(end-start)
minute=math.floor(second/60)
hour=math.floor(minute/60)
tmin=minute-(60*hour)
tsec=second-(hour*3600)-(tmin*60)

print("Program Execution Time = %d hours %d minutes %d seconds"%(hour,tmin,tsec))



		
 
