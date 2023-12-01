# simulation

requirement

<img width="473" alt="image" src="https://github.com/CharlieChee/simulation/assets/99850422/97a9591a-2510-4bb7-8347-765896c71fb9">

Raw data: https://drive.google.com/drive/folders/17iZj6EE72_VXDpjPcio5dHsnUL9eDRle
In the data set, there are three types of data, each with 20 files, corresponding to different values of b (b = {1,2,3,4,5,6,7,8,9,10,20, 30,40,50,60,70,80,90,100})

Taking the video source as an example, select three different b and analyze their time series. It can be found that as b increases, the waiting time becomes significantly longer and is unstable.

![image](https://github.com/CharlieChee/simulation/assets/99850422/d161c2d6-aa6c-4807-91c0-5bb9e56f6473)
![image](https://github.com/CharlieChee/simulation/assets/99850422/a3b53982-1cb3-49e0-be95-ddaf4817e543)
![image](https://github.com/CharlieChee/simulation/assets/99850422/e515524a-9c83-4860-ac6f-242c6ef6c269)

comment:

<img width="864" alt="image" src="https://github.com/CharlieChee/simulation/assets/99850422/c83227f0-8646-4670-96bc-fffcfd5aefb8">

<img width="811" alt="image" src="https://github.com/CharlieChee/simulation/assets/99850422/e6a98374-e47b-4a8a-88d8-fb1342178f64">

Reasons why confidence intervals appear negative:
Because the confidence interval obtained is symmetrical, there will be situations where the waiting time is less than 0. In order to avoid this problem, you can choose to use the log function to correct it. But the impact is not big.
