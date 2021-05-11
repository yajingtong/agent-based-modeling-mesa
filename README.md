# agent-based-modeling-mesa Epidemics model
agent-based modeling with mesa, mesa-geo

# Summary
This is a geoversion of a simple agent-based pandemic model, utilizing the capabilities of mesa-geo.

It uses geographical data of wenatchee's regions on top of a an Leaflet map to show the location of agents (in a continuous space).

Person agents are initially located in random positions in the city, then start moving around unless they are infected. A fraction of agents start with an infection and may move or stop (based on the setting) in each step. Susceptible agents (those who have never been infected) who come in proximity with an infected agent may become infected.

Neighbourhood agents represent neighbourhoods in the wenatchee city, and become hot-spots (colored red) if there are infected agents inside them. Data obtained from this link.The save agents & regions ramain colour blue.

# How to run
To run the model interactively, run mesa runserver in this directory. e.g.

```
mesa runserver
```
Then open your browser to http://127.0.0.1:8521/, set the desired parameters, press Reset, and then Run.

# Reference
https://github.com/projectmesa/mesa
