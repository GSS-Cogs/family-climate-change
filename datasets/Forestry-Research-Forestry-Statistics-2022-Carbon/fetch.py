# https://cdn.forestresearch.gov.uk/2022/09/Ch4_Carbon_FS2022.xlsx

import click
import pandas as pd
from pathlib import Path


@click.command()
@click.option("--output", default=Path("./output.csv"), type=click.Path(path_type=Path))
def fetch(output: Path()) -> None:

    df = pd.read_excel(
        "https://cdn.forestresearch.gov.uk/2022/09/Ch4_Carbon_FS2022.xlsx",
        sheet_name="Figure_4.1_data",
        header=4,
    )

    df = pd.melt(
        df,
        id_vars="Year",
        var_name="Geography",
        value_name="Observation",
        ignore_index=True,
    )
    df.to_csv(output, index=False)
    return


if __name__ == "__main__":
    fetch()
