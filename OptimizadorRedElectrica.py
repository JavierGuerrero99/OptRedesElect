import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import defaultdict

class OptimizadorRedElectrica:
    def __init__(self):
        self.G = nx.Graph()  # Grafo para representar la red eléctrica
        self.resultados = defaultdict(dict)  # Almacenar resultados de optimización
        
    def cargar_datos(self, archivo_nodos, archivo_aristas):
        """Carga los datos de nodos y aristas desde archivos CSV"""
        try:
            # Cargar nodos (subestaciones y puntos de consumo)
            df_nodos = pd.read_csv(archivo_nodos)
            for _, row in df_nodos.iterrows():
                self.G.add_node(row['id'], tipo=row['tipo'], demanda=row['demanda'])
            
            # Cargar aristas (líneas de transmisión)
            df_aristas = pd.read_csv(archivo_aristas)
            for _, row in df_aristas.iterrows():
                self.G.add_edge(row['origen'], row['destino'], 
                              resistencia=row['resistencia'],
                              capacidad=row['capacidad'],
                              longitud=row['longitud'])
            
            print(f"Red cargada con {self.G.number_of_nodes()} nodos y {self.G.number_of_edges()} aristas")
            return True
        except Exception as e:
            print(f"Error al cargar datos: {str(e)}")
            return False
    
    def visualizar_red(self, titulo="Red de Distribución Eléctrica"):
        """Visualiza la red eléctrica usando Matplotlib"""
        plt.figure(figsize=(12, 8))
        
        # Posicionamiento de nodos
        pos = nx.spring_layout(self.G, seed=42)
        
        # Dibujar nodos por tipo
        tipos_nodos = set(nx.get_node_attributes(self.G, 'tipo').values())
        colores = {'subestacion': 'red', 'consumo': 'blue'}
        
        for tipo in tipos_nodos:
            nodos = [nodo for nodo in self.G.nodes() if self.G.nodes[nodo]['tipo'] == tipo]
            nx.draw_networkx_nodes(self.G, pos, nodelist=nodos, 
                                 node_color=colores[tipo], 
                                 node_size=300, label=tipo)
        
        # Dibujar aristas con grosor según capacidad
        aristas, capacidades = zip(*nx.get_edge_attributes(self.G, 'capacidad').items())
        capacidades_norm = [c/max(capacidades)*5 for c in capacidades]  # Normalizar para visualización
        
        nx.draw_networkx_edges(self.G, pos, edgelist=aristas, 
                             width=capacidades_norm, alpha=0.7)
        
        # Etiquetas
        nx.draw_networkx_labels(self.G, pos, font_size=8)
        edge_labels = {(u, v): f"{d['resistencia']}Ω" for u, v, d in self.G.edges(data=True)}
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_size=7)
        
        plt.title(titulo)
        plt.legend()
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    
    def calcular_arbol_expansion_minima(self, metodo='kruskal'):
        """Calcula el árbol de expansión mínima para reducir longitud de líneas"""
        try:
            # Usamos la longitud como peso para el MST
            mst = nx.minimum_spanning_tree(self.G, weight='longitud', algorithm=metodo)
            
            # Calcular métricas
            long_total_original = sum(d['longitud'] for _, _, d in self.G.edges(data=True))
            long_total_mst = sum(d['longitud'] for _, _, d in mst.edges(data=True))
            reduccion = (long_total_original - long_total_mst) / long_total_original * 100
            
            # Guardar resultados
            self.resultados['MST'] = {
                'grafo': mst,
                'longitud_original': long_total_original,
                'longitud_optimizada': long_total_mst,
                'reduccion_porcentual': reduccion
            }
            
            print(f"Árbol de Expansión Mínima ({metodo}):")
            print(f"- Longitud total original: {long_total_original:.2f} km")
            print(f"- Longitud total optimizada: {long_total_mst:.2f} km")
            print(f"- Reducción: {reduccion:.2f}%")
            
            return mst
        except Exception as e:
            print(f"Error al calcular MST: {str(e)}")
            return None
    
    def calcular_flujo_costo_minimo(self):
        # Crear un grafo dirigido para flujo de costo mínimo
        G = nx.DiGraph()

        # Agregar nodos con demanda
        total_demanda = 0
        for nodo, data in self.G.nodes(data=True):
            if data.get("tipo") == "cliente":
                G.add_node(nodo, demand=data.get("demanda", 0))
                total_demanda += data.get("demanda", 0)
            elif data.get("tipo") == "subestacion":
                G.add_node(nodo, demand=-data.get("potencia", 0))
                total_demanda -= data.get("potencia", 0)
            else:
                G.add_node(nodo, demand=0)

        # Verificar que la suma total de demandas sea cero
        if total_demanda != 0:
            print("❌ Error: La suma total de demandas no es cero.")
            print(f"Total demanda: {total_demanda}")
            return

        # Agregar aristas con capacidad y peso
        for u, v, data in self.G.edges(data=True):
            distancia = data.get("distancia", 1)
            G.add_edge(u, v, weight=distancia, capacity=100)
            G.add_edge(v, u, weight=distancia, capacity=100)

        # Crear una superfuente para alimentar todas las subestaciones si lo deseas
        # (opcional, dependiendo del modelo)

        try:
            flujo_costo, flujo_dict = nx.network_simplex(G)
            print("✅ Flujo de costo mínimo:", flujo_costo)
            for u in flujo_dict:
                for v in flujo_dict[u]:
                    if flujo_dict[u][v] > 0:
                        print(f"{u} → {v}: {flujo_dict[u][v]}")
        except nx.NetworkXUnfeasible:
            print("❌ Error: No hay un flujo que satisfaga todas las demandas (red insuficiente o desequilibrada).")




    
    def estimar_perdidas(self, grafo):
        """Estima pérdidas por efecto Joule en la red (simplificado)"""
        perdidas = 0
        for u, v, d in grafo.edges(data=True):
            # Asumimos corriente constante para simplificar (en realidad debería calcularse)
            I = 100  # Amperes (valor de ejemplo)
            R = d.get('resistencia', 0)
            perdidas += I**2 * R
        return perdidas
    
    def analizar_conectividad(self):
        """Analiza la conectividad y vulnerabilidad de la red"""
        resultados = {}
        
        # Conectividad
        resultados['es_conexo'] = nx.is_connected(self.G)
        resultados['componentes'] = nx.number_connected_components(self.G)
        
        # Nodos críticos (betweenness centrality)
        betweenness = nx.betweenness_centrality(self.G)
        resultados['nodo_mas_critico'] = max(betweenness, key=betweenness.get)
        
        # Robustez
        resultados['coeficiente_clustering'] = nx.average_clustering(self.G)
        resultados['grado_promedio'] = sum(dict(self.G.degree()).values()) / self.G.number_of_nodes()
        
        self.resultados['AnalisisConectividad'] = resultados
        return resultados
    
    def exportar_gephi(self, archivo_salida='red_electrica.gexf'):
        """Exporta el grafo a formato GEXF para visualización en Gephi"""
        nx.write_gexf(self.G, archivo_salida)
        print(f"Grafo exportado a {archivo_salida} para visualización en Gephi")


# Ejemplo de uso
if __name__ == "__main__":
    optimizador = OptimizadorRedElectrica()
    
    # Cargar datos de ejemplo (deberías reemplazar con tus archivos reales)
    optimizador.cargar_datos('nodos_ejemplo.csv', 'aristas_ejemplo.csv')
    
    # Visualizar red original
    optimizador.visualizar_red("Red de Distribución Original")
    
    # Aplicar algoritmos de optimización
    mst = optimizador.calcular_arbol_expansion_minima()
    flujo = optimizador.calcular_flujo_costo_minimo()
    
    # Analizar conectividad
    conectividad = optimizador.analizar_conectividad()
    print("\nAnálisis de Conectividad:")
    for k, v in conectividad.items():
        print(f"- {k}: {v}")
    
    # Exportar para visualización avanzada
    optimizador.exportar_gephi()
    
    # Visualizar red optimizada (MST)
    if mst:
        nx.draw(mst, with_labels=True, node_color='lightgreen')
        plt.title("Árbol de Expansión Mínima")
        plt.show()