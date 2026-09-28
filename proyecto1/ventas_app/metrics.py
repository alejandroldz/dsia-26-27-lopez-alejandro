import pandas as pd


def compute_metrics(validos: pd.DataFrame) -> dict:
    importe_por_region = (
        validos.groupby("region", as_index=False)["importe"]
        .sum()
        .sort_values("importe", ascending=False)
    )

    top_3 = (
        validos.groupby("producto", as_index=False)["importe"]
        .sum()
        .sort_values("importe")[:3]
    )

    compras = validos["cliente_id"].value_counts()
    clientes = compras[compras > 1]

    return {
        "importe_por_region": importe_por_region,
        "top_3": top_3,
        "clientes": clientes,
    }