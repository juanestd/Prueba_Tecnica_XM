# Prueba Técnica - Parte 1

import pandas as pd
import matplotlib.pyplot as plt
from pydataxm.pydatasimem import ReadSIMEM


class ClienteSIMEM:

    # Clase encargada de consumir la información desde la API de SIMEM

    def __init__(self, id_dataset, fecha_inicio, fecha_fin):
        self.id_dataset = id_dataset
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin

    def obtener_datos(self):
        # Descarga la información del dataset para el rango de fechas definido
        lector = ReadSIMEM(
            self.id_dataset,
            self.fecha_inicio,
            self.fecha_fin
        )
        datos = lector.main(filter=False)
        return datos


class ProcesadorPrecios:
    # Clase encargada de procesar y transformar los datos del precio de bolsa

    def __init__(self, datos):
        self.df = datos

    def filtrar_tx1(self):
        # Se filtran únicamente los registros correspondientes a la versión TX1
        self.df = self.df[self.df["Version"] == "TX1"]
        return self.df

    def agregar_periodo(self):
        # A partir de la fecha y hora se obtiene el periodo horario 
        self.df["FechaHora"] = pd.to_datetime(self.df["FechaHora"])
        self.df["Periodo"] = self.df["FechaHora"].dt.hour
        return self.df

    def calcular_estadisticas(self):
        # Cálculo del precio máximo, mínimo y promedio del periodo analizado
        precio_maximo = self.df["Valor"].max()
        precio_minimo = self.df["Valor"].min()
        precio_promedio = self.df["Valor"].mean()
        return precio_maximo, precio_minimo, precio_promedio

    def obtener_periodos_extremos(self, cantidad=3):
        # Identificación de los periodos con precios más altos y más bajos
        precios_altos = self.df.nlargest(cantidad, "Valor")[["FechaHora", "Periodo", "Valor"]]
        precios_bajos = self.df.nsmallest(cantidad, "Valor")[["FechaHora", "Periodo", "Valor"]]
        return precios_altos, precios_bajos


class Visualizador:
    # Clase encargada de la visualización de resultados

    @staticmethod
    def graficar_precios(df, precio_maximo, precio_minimo, precio_promedio):
        
        df = df.sort_values("FechaHora")

        plt.figure(figsize=(14, 6))

        plt.plot(
            df["FechaHora"],
            df["Valor"],
            label="Precio Bolsa Nacional",
            alpha=0.7
        )

        
        plt.axhline(precio_maximo, linestyle="--", linewidth=2,
                    label=f"Máximo: {precio_maximo:.2f}")
        plt.axhline(precio_minimo, linestyle="--", linewidth=2,
                    label=f"Mínimo: {precio_minimo:.2f}")
        plt.axhline(precio_promedio, linestyle="--", linewidth=2,
                    label=f"Promedio: {precio_promedio:.2f}")

        plt.xlabel("Fecha y Hora")
        plt.ylabel("Precio de Bolsa (COP/kWh)")
        plt.title("Precio de Bolsa Nacional Horario - Diciembre 2025 (TX1)")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()



# Función principal


def main():
  
    id_dataset = "EC6945"
    fecha_inicio = "2025-12-01"
    fecha_fin = "2025-12-31"

    # 1. Extracción de datos desde SIMEM
    cliente = ClienteSIMEM(id_dataset, fecha_inicio, fecha_fin)
    datos = cliente.obtener_datos()

    # 2. Procesamiento de la información
    procesador = ProcesadorPrecios(datos)
    df_tx1 = procesador.filtrar_tx1()
    df_tx1 = procesador.agregar_periodo()

    # 3. Cálculo de estadísticas
    precio_maximo, precio_minimo, precio_promedio = procesador.calcular_estadisticas()

    print("\nEstadísticas del Precio de Bolsa:")
    print(f"Precio máximo: {precio_maximo:.2f}")
    print(f"Precio mínimo: {precio_minimo:.2f}")
    print(f"Precio promedio: {precio_promedio:.2f}")

    # 4. Identificación de periodos 
    periodos_altos, periodos_bajos = procesador.obtener_periodos_extremos()

    print("\nTres periodos con el precio más alto:")
    print(
        periodos_altos.rename(columns={
            "FechaHora": "Fecha",
            "Valor": "Precio de Bolsa COP/kWh"
        })
    )

    print("\nTres periodos con el precio más bajo:")
    print(
        periodos_bajos.rename(columns={
            "FechaHora": "Fecha",
            "Valor": "Precio de Bolsa COP/kWh"
        })
    )

    # 5. Visualización
    Visualizador.graficar_precios(
        df_tx1,
        precio_maximo,
        precio_minimo,
        precio_promedio
    )


if __name__ == "__main__":
    main()
