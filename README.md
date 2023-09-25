# Modflow calculation service

## Api for results

### Get result for given calculation_id, head or drawdown, layer and timestep

```
GET /<calculation_id>/results/types/<head|drawdown>/layers/<layer_idx>/idx/<total_time_idx>
```
returns json with all results for given calculation_id, head or drawdown, layer_idx and total_time_idx

### Get image for given calculation_id, head or drawdown, layer and timestep

```
GET /<calculation_id>/results/types/<head|drawdown>/layers/<layer_idx>/idx/<total_time_idx>?output=image
```

returns image for given calculation_id, head or drawdown, layer_idx and total_time_idx

### Get colorscale for given calculation_id, head or drawdown and timestep

```
GET /<calculation_id>/results/types/<head|drawdown>/idx/<total_time_idx>?output=colorscale
```
