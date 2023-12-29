# Chartjs-pl

## Purpose

This is the start of using Chart.js graphing for notebooks with polars as a backend. It gets inspiration from plotly but I like the look of Chart.js graphs more than Plotly plus, supposedly, the canvas based Chartjs should perform better than svg based plotly. Also, I sometimes make small React webapps that natively use Chart.js so I'd like my notebook output to look consistent with those. Lastly, I couldn't get ipychart to work in my environment and it gives an excuse to make a charting library with polars as backend with no pandas.

## Status

I struggled with importing the main chart.js plus plugins from a CDN using IPython calls to Javascript for awhile and eventually used vite to publish a bundled version of Chart.js with zoomPlugin and autocolors built in as a single umd.js file. That is [here](https://www.npmjs.com/package/chartbundle?activeTab=code).

With that done, we can run calls to

```python
Javascript(
    """
require(['https://www.unpkg.com/chartbundle@1.0.0/dist/chartBundle.umd.js'], function(chartjs) {
    var ctx = document.getElementById("%s");
    chartjs.Chart.register(chartjs.zoomPlugin);
    new chartjs.Chart(ctx, %s);
    })"""
    % (this_id, cfg)
)
```

Right now there's a bar function with some options exposed but it already needs some refactoring before more things are added and a thought to the future of making multiple graph types in one.

## Near term goals

1. Refactor and expose scatter, line charts
2. Create functions for generated graphs, ie histograms (bar), ecdf (line), etc
3. Expose more chart customizations/options
4. Wrap all functions in a class which is registered to pl.DataFrame namespace for `df.cx.scatter(...)` syntax.
5. Publish as pip installable package.

## Medium term goals

1. Expose mixed graphs, (ie lines and bars on same chart)
2. Incorporate animation as a dimension similar to [plotly](https://plotly.com/python/animations/)

## Aspirational idea(s) aka need help to do these

1. use mathbox.js for webgl 3d graphs (maybe this is new library)
2. connect wasm polars to Python polars to prevent serialization
