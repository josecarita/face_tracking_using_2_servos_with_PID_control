clear
clc

t = xlsread('data.xlsx','A5:A243');
y = xlsread('data.xlsx','B5:b243');

datos = iddata(y,t,0.25)