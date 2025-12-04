from src.database import simple_db


class Agent():
    def __init__(self):
        self.db = simple_db
        self.portfolio = {}
    
    def get_portfolio(self):
        holdings = self.db.get_holdings()
        for holding in holdings:
            self.portfolio[holding[1]] = self.portfolio.get(holding[1], 0) + holding[3]

agent = Agent()
agent.get_portfolio()
print(agent.portfolio)