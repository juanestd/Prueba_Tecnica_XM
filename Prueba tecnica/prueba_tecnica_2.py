
#Prueba Técnica  - Parte 2

import pandas as pd

class CSVLoader:
    
    #Carga  los archivos CSV
    
    def __init__(self, ruta):
        self.ruta = ruta

    def load_lecturas(self):
        
        #Carga y concatena las lecturas
        
        l1 = pd.read_csv(f"{self.ruta}/Lecturas_parte1.csv")
        l2 = pd.read_csv(f"{self.ruta}/Lecturas_parte2.csv")

        lecturas = pd.concat([l1, l2], ignore_index=True)


        lecturas["Fecha"] = pd.to_datetime(lecturas["Fecha"])
        lecturas["Lectura"] = pd.to_numeric(lecturas["Lectura"])

        return lecturas

    def load_mapeo(self):

        mapeo = pd.read_csv(f"{self.ruta}/Mapeo.csv")


        mapeo["Fecha"] = pd.to_datetime(mapeo["Fecha"])
        mapeo["ValorLBC"] = pd.to_numeric(mapeo["ValorLBC"])

        return mapeo


class ConsumptionCalculator:
    
    #Calcula el consumo diario por frontera
   
    def __init__(self, lecturas):
        self.lecturas = lecturas

    def calculate_daily_ce(self):
        
        #CE = suma diaria de lecturas por frontera
        
        ce_diario = (
            self.lecturas
            .groupby(["Fecha", "CodFronteraDDV"], as_index=False)
            .agg(CE_kWh=("Lectura", "sum"))
        )
        return ce_diario


class DisconnectionCalculator:
   
    #Calcula la desconexión verificada
    
    def __init__(self, ce_diario, mapeo):
        self.ce = ce_diario
        self.mapeo = mapeo

    def calculate(self):
        
        #Desconexión = max(0, LBC - CE)
        
        df = self.ce.merge(
            self.mapeo,
            on=["Fecha", "CodFronteraDDV"],
            how="left"
        )


        df["Desconexion_kWh"] = (
            df["ValorLBC"] - df["CE_kWh"]
        ).clip(lower=0)

        return df


class Aggregator:
   
    #Agrega la información por mes y agente
   
    def __init__(self, df):
        self.df = df

    def aggregate_monthly(self):
        
        #Mensual por agente
        
        self.df["Mes"] = self.df["Fecha"].dt.to_period("M").astype(str)

        resultado = (
            self.df
            .groupby(["Mes", "AGENTE"], as_index=False)
            .agg(
                **{
                    "Desconexión Verificada kWh": ("Desconexion_kWh", "sum"),
                    "Total de Fronteras": ("CodFronteraDDV", "nunique")
                }
            )
            .sort_values("AGENTE")
        )


        resultado["Desconexión Verificada kWh"] = (
            resultado["Desconexión Verificada kWh"].round(2)
        )

        resultado.rename(columns={"Mes": "Fecha"}, inplace=True)
        return resultado



class Exporter:
    
    #Exporta el resultado final
    
    @staticmethod
    def to_csv(df, filename):
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"\n Archivo exportado: {filename}")




def main():
    ruta = "data_noviembre_2025"

    # 1. Carga de datos
    loader = CSVLoader(ruta)
    lecturas = loader.load_lecturas()
    mapeo = loader.load_mapeo()

    # 2. Cálculo del consumo diario
    ce_calc = ConsumptionCalculator(lecturas)
    ce_diario = ce_calc.calculate_daily_ce()

    # 3. Cálculo de desconexión verificada
    dis_calc = DisconnectionCalculator(ce_diario, mapeo)
    df_desconexion = dis_calc.calculate()

    # 4. Agregación mensual por agente
    aggregator = Aggregator(df_desconexion)
    resultado_final = aggregator.aggregate_monthly()

    print("\n Resultado final:")
    print(resultado_final)

    # 5. Exportar CSV
    Exporter.to_csv(resultado_final, "Desconexion_mes_agen.csv")


if __name__ == "__main__":
    main()
