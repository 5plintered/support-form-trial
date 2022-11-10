#!/d/sw/miniconda3/envs/web_support/bin/python
from wsgiref.handlers import CGIHandler
from support import create_app

app = create_app()
app.debug = True

CGIHandler().run(app)
