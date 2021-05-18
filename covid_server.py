from mesa_geo.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter
from covid_model import InfectedModel, PersonAgent
from mesa_geo.visualization.MapModule import MapModule


class InfectedText(TextElement):
    """
      to show the processed steps
    """

    def __init__(self):
        pass

    def render(self, model):
        return "Steps: " + str(model.steps)



model_params = {
    "pop_size": UserSettableParameter("slider", "population", 500, 100, 1000, 200),
    "init_infected": UserSettableParameter(
        "slider", "initial infected", 0.2, 0.00, 1.0, 0.05
    ),
    "exposure_distance": UserSettableParameter(
        "slider", "exposure distance", 500, 100, 1000, 100
    ),
    "infection_risk": UserSettableParameter(
        "slider", "infection risk", 0.1, 0.00, 1.0, 0.05
    ),

}



def infected_draw(agent):
    """
     visualization  with  portrayal 
    """
    portrayal = dict()
    if isinstance(agent, PersonAgent):
        portrayal["radius"] = "2"
    if agent.atype in ["hotspot", "infected"]:
        portrayal["color"] = "Red"
    elif agent.atype in ["safe", "susceptible"]:
        portrayal["color"] = "Blue"
    return portrayal


infected_text = InfectedText()
map_element = MapModule(infected_draw, InfectedModel.MAP_COORDS, 10, 500, 800)
infected_chart = ChartModule(
    [
        {"Label": "infected", "Color": "Red"},
        {"Label": "susceptible", "Color": "Blue"},

    ]
)
server = ModularServer(
    InfectedModel,
    [map_element, infected_text, infected_chart],
    "Basic agent-based covid model",
    model_params,
)
server.launch()
