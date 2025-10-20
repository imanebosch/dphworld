from aws_cdk import App, Environment
from config import settings
from stacks.platform import DataPlatform

app = App()

env = Environment(region=settings.region, account=settings.account)

dpworld_platform = DataPlatform(app, "DataPlatform", config=settings, env=env)

app.synth()
