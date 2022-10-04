from email.policy import default
import click
import pandas as pd
from pathlib import Path

@click.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.option("--output", default=Path("./output.csv"), type=click.Path(path_type=Path))
def wrangle(input: Path(), output: Path()) -> None:
    df = pd.read_excel(input, skiprows=[0])
    df = pd.melt(frame=df, id_vars=[
                 'Country', 'Currency', 'Economic Indicators'], var_name='Year', value_name='Value')
    df["Unit"] = "Million"
    df.to_csv(output, index=False)
    return

if __name__ == "__main__":
    wrangle()
