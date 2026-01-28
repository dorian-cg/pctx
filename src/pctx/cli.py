import typer
from .commands.scan import scan
from .commands.learn import learn
from .commands.find import find
from .commands.ask import ask

app = typer.Typer()

app.command()(scan)
app.command()(learn)
app.command()(find)
app.command()(ask)

