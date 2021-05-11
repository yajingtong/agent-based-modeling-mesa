from mesa.datacollection import DataCollector
from mesa import Model
from mesa.time import BaseScheduler
from mesa_geo.geoagent import GeoAgent, AgentCreator
from mesa_geo import GeoSpace
from shapely.geometry import Point


class PersonAgent(GeoAgent):
    """Person Agent."""

    def __init__(
        self,
        unique_id,
        model,
        shape,
        agent_type="susceptible",
        mobility_range=1000,
        init_infected=0.1,
    ):
        """
        创建agent来表示感染者和未感染者
        :param unique_id:   agent ID
        :param model:       模型
        :param shape:       agent包含的Shape对象
        :param agent_type:  agent是否感染
        :param mobility_range:  agent移动距离的范围
        """
        super().__init__(unique_id, model, shape)
        # 设置agent参数
        self.atype = agent_type
        self.mobility_range = mobility_range

        # 随机选择被感染者
        if self.random.random() < init_infected:
            self.atype = "infected"
            self.model.counts["infected"] += 1  # 增加感染人群，调整初始计数
            self.model.counts["susceptible"] -= 1

    def move_point(self, dx, dy):
        """
        通过创建新店来移动原来的点的位置
        :param dx:  在横坐标移动的距离
        :param dy:  在纵坐标移动的距离
        """
        return Point(self.shape.x + dx, self.shape.y + dy)

    def step(self):
        """定义模型的一个步骤."""
        # 检查易感染人群是否暴露
        if self.atype == "susceptible":
            neighbors = self.model.grid.get_neighbors_within_distance(
                self, self.model.exposure_distance
            )
            for neighbor in neighbors:
                if (
                    neighbor.atype == "infected"
                    and self.random.random() < self.model.infection_risk
                ):
                    self.atype = "infected"
                    break



        # 如果没有感染，agent将继续移动
        if self.atype != "infected":
            move_x = self.random.randint(-self.mobility_range, self.mobility_range)
            move_y = self.random.randint(-self.mobility_range, self.mobility_range)
            self.shape = self.move_point(move_x, move_y)  # 移动到下一位置

        self.model.counts[self.atype] += 1  # 对agent类型进行计数

    def __repr__(self):
        return "Person " + str(self.unique_id)


class NeighbourhoodAgent(GeoAgent):
    """Neighbourhood agent. 根据感染人数改变颜色."""

    def __init__(self, unique_id, model, shape, agent_type="safe", hotspot_threshold=2):
        """
        创建Neighbourhood agent.
        :param unique_id:  agent ID
        :param model:       模型
        :param shape:       agent的shape属性对象
        :param agent_type:  定义agent是否感染 ("infected", "susceptible")
        :param hotspot_threshold:  有多少个感染者该区域会被看做疫情密集处
        """
        super().__init__(unique_id, model, shape)
        self.atype = agent_type
        self.hotspot_threshold = (
            hotspot_threshold
        )  # 当该区域是疫情密集处
        self.color_hotspot()

    def step(self):
        """使agent移动一步."""
        self.color_hotspot()
        self.model.counts[self.atype] += 1  # agent类型计数

    def color_hotspot(self):
        # 查看是否该区域是疫情密集处 (根据已感染人数的数量决定)
        neighbors = self.model.grid.get_intersecting_agents(self)
        infected_neighbors = [
            neighbor for neighbor in neighbors if neighbor.atype == "infected"
        ]
        if len(infected_neighbors) >= self.hotspot_threshold:
            self.atype = "hotspot"
        else:
            self.atype = "safe"

    def __repr__(self):
        return "Neighborhood " + str(self.unique_id)


class InfectedModel(Model):
    """定义模拟新冠病毒传播模型."""

    # 定义地图中心坐标
    MAP_COORDS = [47.42, -120.30]
    geojson_regions = "develop1.geojson"
    unique_id = "BLOCK_ID"

    def __init__(self, pop_size, init_infected, exposure_distance, infection_risk=0.2):
        """
       初始化模型
        :param pop_size:       人口数量
        :param init_infected:   初始设置已感染人群
        :param exposure_distance:   病毒暴露距离
        :param infection_risk:      密接人群的感染几率
        """
        self.schedule = BaseScheduler(self)
        self.grid = GeoSpace()
        self.steps = 0
        self.counts = None
        self.reset_counts()

        # 设置模型参数
        self.pop_size = pop_size
        self.counts["susceptible"] = pop_size
        self.exposure_distance = exposure_distance
        self.infection_risk = infection_risk

        self.running = True
        self.datacollector = DataCollector(
            {
                "infected": get_infected_count,
                "susceptible": get_susceptible_count,
            }
        )

        # 设置住宅区域
        AC = AgentCreator(NeighbourhoodAgent, {"model": self})
        neighbourhood_agents = AC.from_file(
            self.geojson_regions, unique_id=self.unique_id
        )
        self.grid.add_agents(neighbourhood_agents)

        # 生成agent
        ac_population = AgentCreator(
            PersonAgent, {"model": self, "init_infected": init_infected}
        )
        # 生成随机的位置, 将neighbourhood agent添加到grid和计时器中
        for i in range(pop_size):
            this_neighbourhood = self.random.randint(
                0, len(neighbourhood_agents) - 1
            )  # agent的起始位置
            center_x, center_y = neighbourhood_agents[
                this_neighbourhood
            ].shape.centroid.coords.xy
            n_bounds = neighbourhood_agents[this_neighbourhood].shape.bounds  #住宅区域的边界
            spread_x = int(
                n_bounds[2] - n_bounds[0]
            )  # 使agent随机向周围移动
            spread_y = int(n_bounds[3] - n_bounds[1])
            this_x = center_x[0] + self.random.randint(0, spread_x) - spread_x / 2
            this_y = center_y[0] + self.random.randint(0, spread_y) - spread_y / 2
            this_person = ac_population.create_agent(
                Point(this_x, this_y), "P" + str(i)
            )
            self.grid.add_agents(this_person)
            self.schedule.add(this_person)

        # 添加人口后，添加住宅区域agent
        # 依据 BaseScheduler改变颜色
        for agent in neighbourhood_agents:
            self.schedule.add(agent)

        self.datacollector.collect(self)

    def reset_counts(self):
        self.counts = {
            "susceptible": 0,
            "infected": 0,
            "safe": 0,
            "hotspot": 0,
        }

    def step(self):
        """模型运行一个步骤."""
        self.steps += 1
        self.reset_counts()
        self.schedule.step()
        self.grid._recreate_rtree()  # 在agent移动后，重新计算r树

        self.datacollector.collect(self)

        # 模型一直运行直到感染人数达到80%
        if self.counts["infected"] >= 0.8 * self.pop_size:
            self.running = False
    def writeagents(self):
        self.write()

# Functions needed for datacollector
def get_infected_count(model):
    return model.counts["infected"]


def get_susceptible_count(model):
    return model.counts["susceptible"]



