import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import logging
from typing import Tuple, Optional

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Funcion: get_rolling_returns
#     Descarga datos históricos y calcula la rentabilidad rodante.
# Recibe:
#     ticker: str    Nombre del ticker en Yahoo Finance que se busca descargar
#     years: int     Anhos para los que se busca analizar el retorno
#     period: str    Constante de 20 anhos porque quiero analizar una ventana masomenos actual
# Devuelve:
#      Tuple[Optional[pd.Series], float]: 
#                     Una tupla con la serie de retornos calculados (o None si falla) 
#                     y el porcentaje final de exito (win rate).
def get_rolling_returns(ticker: str, years: int, period: str = "20y") -> Tuple[Optional[pd.Series], float]:
    """
    """
    logging.info(f"Descargando datos para {ticker}...")
    try:
        # Descarga de datos
        # auto_adjust en False para que no salga warning
        data = yf.download(ticker, period=period, auto_adjust=False)['Close']
        
        # Si yfinance devuelve un DataFrame (tabla) por las nuevas actualizaciones, 
        # lo aplanamos a una Series (columna única) con squeeze() para evitar los warnings de pandas.
        if isinstance(data, pd.DataFrame):
            data = data.squeeze()
            
        if data.empty:
            raise ValueError("No se obtuvieron datos de Yahoo Finance.")
    except Exception as e:
        logging.error(f"Error al descargar datos: {e}")
        return None, 0.0

    trading_days = int(years * 252)
    rolling_return = ((data / data.shift(trading_days)) - 1) * 100
    
    # Limpiar NaNs para las estadísticas
    valid_returns = rolling_return.dropna()
    
    if valid_returns.empty:
        logging.warning("El periodo seleccionado es demasiado corto para los años de inversión.")
        return None, 0.0

    positive_periods = (valid_returns > 0).sum()
    total_periods = len(valid_returns)
    win_rate = (positive_periods / total_periods) * 100

    return rolling_return, float(win_rate)

# Funcion: plot_rolling_returns
#      Genera y muestra la grafica con los resultados.
# Recibe:
#      rolling_return: pd.Series  La serie temporal con los porcentajes ya calculados
#      win_rate: float            El porcentaje de exito final para decidir el color de la linea
#      years: int                 Los anhos de inversion para ponerlos en los titulos y guardar el archivo
# Devuelve:
#      Ninguno (None). Solo genera el grafico en pantalla y lo guarda como imagen PNG.
# Nota: Meto una logica para cambiar el color a verde si el win rate es alto, asi visualmente impacta mas.
def plot_rolling_returns(rolling_return: pd.Series, win_rate: float, years: int):
    plt.figure(figsize=(15, 7))
    
    # Lógica de color: Verde si win_rate > 80%, azul si no.
    line_color = '#2ecc71' if win_rate > 80 else '#3498db'
    
    plt.plot(rolling_return, label=f'Rentabilidad a {years} año(s)', color=line_color)
    plt.axhline(0, color='red', linestyle='--', linewidth=1) 

    plt.title(f'S&P 500: Rentabilidad Rodante a {years} Año(s)\nProbabilidad de éxito: {win_rate:.2f}%', fontsize=16)
    plt.ylabel('Rentabilidad (%)')
    plt.xlabel('Fecha de Venta')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    # Guarda la imagen
    plt.savefig(f'sp500_rolling_{years}y.png', dpi=300)
    logging.info(f"Gráfico guardado como sp500_rolling_{years}y.png")
    plt.show()

# Funcion: print_statistics
#      Muestra en la consola el resumen limpio de los datos analizados.
# Recibe:
#      rolling_return: pd.Series  Los retornos rodantes de donde saco los maximos y minimos
#      win_rate: float            La probabilidad de ganar dinero que calculamos antes
#      years: int                 El horizonte temporal para el encabezado
# Devuelve:
#      Ninguno (None). Su funcion es solo imprimir el bloque de texto con el resumen en la terminal.
# Nota: Uso dropna() aqui tambien para asegurarme de que los extremos (peor y mejor) se calculen sobre datos reales.
def print_statistics(rolling_return: pd.Series, win_rate: float, years: int):
    valid_returns = rolling_return.dropna()
    print(f"\n--- Análisis para un horizonte de {years} años ---")
    print(f"Total de periodos analizados: {len(valid_returns)}")
    print(f"Periodos con retorno positivo: {(valid_returns > 0).sum()}")
    print(f"Probabilidad histórica de ganancia: {win_rate:.2f}%")
    print(f"Peor retorno histórico: {float(valid_returns.min()):.2f}%")
    print(f"Mejor retorno histórico: {float(valid_returns.max()):.2f}%")
    print("-" * 45)

# Código principal
if __name__ == "__main__":
    TICKER = "^GSPC" # Codigo que representa el activo en Yahoo Finance
    YEARS_TO_HOLD = 5 # Numero de anhos que se mantendra el activo
    
    returns_data, success_rate = get_rolling_returns(ticker=TICKER, years=YEARS_TO_HOLD)
    
    if returns_data is not None:
        print_statistics(returns_data, success_rate, YEARS_TO_HOLD)
        plot_rolling_returns(returns_data, success_rate, YEARS_TO_HOLD)
