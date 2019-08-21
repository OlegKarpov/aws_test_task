import os

from sceptre.context import SceptreContext
from sceptre.plan.plan import SceptrePlan

context = SceptreContext(os.path.abspath('cloud_formation'), 'dev/lambda.yaml')
plan = SceptrePlan(context)
plan.launch()
