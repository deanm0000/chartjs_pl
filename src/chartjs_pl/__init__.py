from IPython.display import HTML, Javascript, display
from uuid import uuid4
import polars as pl
import json


def bar(
    df: pl.DataFrame,
    x: str = None,
    y: str = None,
    title: str = None,
    subtitle: str = None,
    legend_on: bool = True,
    legend_dict: dict = None,
) -> None:
    """
    bar(df, x=None, y=None, title="")

    Parameters
    ----------
    df: polars DataFrame
    x: str
        The name of the column to be used for the x axis
    y: str
        The name of the column to be used for the y axis
    title: str
        The title of the graph
    subtitle: str
        The title of the graph
    legend_on: bool
        Whether or not to display a legend, default is True
    legend_dict: dict
        A dict for customizing the legend according to chart.js docs
        https://www.chartjs.org/docs/master/configuration/legend.html
    """
    if legend_on is False and isinstance(legend_dict, dict):
        raise ValueError("Don't set legend_on to False while also set legend_dict")
    if legend_dict is not None and not isinstance(legend_dict, dict):
        raise ValueError("legend_dict must be a dictionary")
    if y is None and x is None:
        y = df.columns[0]
        x = df.columns[1]
    if y is None or x is None:
        raise ValueError("If either x or y is specificed then both must be specified")
    if y not in df.columns:
        raise ValueError(f"supplied y='{y}' not found in {df.columns}")
    if x not in df.columns:
        raise ValueError(f"supplied x='{x}' not found in {df.columns}")
    this_data = (
        df.sort(x)
        .select(pl.col(x).cast(pl.Utf8).alias("x"), pl.col(y).alias("y"))
        .write_json(row_oriented=True)
    )
    # Chart.js takes all its data, config, options, etc from one single object. The
    # rust based json writer ought to be faster than the python json.dumps so I want
    # to maintain using write_json from the df. That needs to be embedded into the
    # big object and the way I accomplish that is use a big integer with mostly
    # arbitrary digits that gets string replaced after the json.dumps with
    # the polars generated json. It seems a bit hacky, maybe there's a better way
    # that doesn't resort to converting the df to dicts and relying on json.dumps
    # to serialize all the data.
    DATA_PLACEHOLDER = 98765432198534713548495867192850923476

    this_id = str(uuid4())
    cfg = dict(
        type="bar",
        data=dict(datasets=[dict(data=DATA_PLACEHOLDER)]),
        options=dict(
            # I'd like this to work with parsing=False but it doesn't. I'm not sure how to feed it the
            # data to make it work. It's probably pointless to trade javascript parsing just for python parsing though
            # parsing=False,
            plugins=dict(
                zoom=dict(
                    zoom=dict(
                        wheel=dict(enabled=True, speed=0.01),
                        drag=dict(enabled=True),
                        mode="y",
                    )
                ),
            ),
        ),
    )
    if title is not None:
        cfg["options"]["plugins"]["title"] = dict(display=True, text=title)
    if subtitle is not None:
        cfg["options"]["plugins"]["subtitle"] = dict(display=True, text=subtitle)
    if isinstance(legend_dict, dict):
        cfg["options"]["plugins"]["legend"] = legend_dict
    elif legend_on is False:
        cfg["options"]["plugins"]["legend"] = dict(display=False)

    cfg = json.dumps(cfg).replace(str(DATA_PLACEHOLDER), this_data)
    display(HTML(f"""<canvas  id="{this_id}"></canvas>"""))
    display(
        Javascript(
            """
        require(['https://www.unpkg.com/chartbundle@1.0.0/dist/chartBundle.umd.js'], function(chartjs) {
            var ctx = document.getElementById("%s");
            chartjs.Chart.register(chartjs.zoomPlugin);
            new chartjs.Chart(ctx, %s);
            })"""
            % (this_id, cfg)
        )
    )
