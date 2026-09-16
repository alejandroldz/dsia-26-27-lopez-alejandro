from pathlib import Path
import pandas as pd
import json

def leer_archivo(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"El archivo {path} no existe en el directorio actual.")
    return pd.read_csv(path)
    
    
def validar_ventas(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame['unidades'] = pd.to_numeric(frame["unidades"], errors="coerce") 
    frame['precio_unitario'] = pd.to_numeric(frame["precio_unitario"], errors="coerce") 
    mascara = (
        frame["unidades"].notna()
        & (frame["unidades"] > 0)
        & frame["precio_unitario"].notna()
        & (frame["precio_unitario"] > 0)
    )
    new_frame = frame[mascara].copy()
    errores = frame[~mascara].copy() 
    new_frame["importe"] = new_frame["unidades"] * new_frame["precio_unitario"]
    return new_frame, errores

if __name__ == "__main__":
    DATA_DIR = Path("Datos") #asegurar que en la terminal estamos en la carpeta correcta
    path = DATA_DIR / "ventas.csv"
    print(path)
    df = leer_archivo(path)
    print(df.shape)
    print(df.dtypes)
    print(df.isna().sum())
    validos, errores = validar_ventas(df)
    print(len(validos))
    print(len(errores))
    
    importe_por_region = validos.groupby("region", as_index=False)["importe"].sum().sort_values("importe", ascending=False)
    print(importe_por_region)
    top_3 = validos.groupby("producto", as_index=False)["importe"].sum().sort_values("importe")[:3]
    print(top_3)
    compras = validos["cliente_id"].value_counts()
    print(compras)
    clientes = compras[compras > 1]
    print(clientes)
    
    validos.to_csv("Datos/ventas_limpias.csv", index=False)
    datos = {
    "filas_totales": int(len(df)),
    "filas_validas": int(len(validos)),
    "filas_invalidas": int(len(errores)),
    "importe_total": float(validos["importe"].sum()),
    }
    json_path = DATA_DIR / "calidad_datos.json"
    json_path.write_text(json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8")
