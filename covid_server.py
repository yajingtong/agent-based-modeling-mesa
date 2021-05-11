from mesa_geo.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter
from covid_model import InfectedModel, PersonAgent
from mesa_geo.visualization.MapModule import MapModule


class InfectedText(TextElement):
    """
      展示已进行的步骤数量
    """

    def __init__(self):
        pass

    def render(self, model):
        return "Steps: " + str(model.steps)


model_params = {
    "pop_size": UserSettableParameter("slider", "人口数量", 500, 100, 1000, 200),
    "init_infected": UserSettableParameter(
        "slider", "最初感染人数占比", 0.2, 0.00, 1.0, 0.05
    ),
    "exposure_distance": UserSettableParameter(
        "slider", "接触距离", 500, 100, 1000, 100
    ),
}


def infected_draw(agent):
    """
        使用portrayal模型可视化
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
        {"Label": "感染者", "Color": "Red"},
        {"Label": "未感染人群", "Color": "Blue"},

    ]
)
server = ModularServer(
    InfectedModel,
    [map_element, infected_text, infected_chart],
    "Basic agent-based covid model",
    model_params,
)
server.launch()
