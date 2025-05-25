# OptimizadorRedElectrica

Este script permite cargar, visualizar y optimizar una red eléctrica modelada como un grafo. Utiliza algoritmos clásicos de teoría de grafos para analizar y mejorar la red.

## Uso

Ejecuta el script principal para cargar los datos de ejemplo, visualizar la red, calcular el árbol de expansión mínima, el flujo de costo mínimo y analizar la conectividad:

```bash
python OptimizadorRedElectrica.py
```

## Funcionalidades

- Carga nodos y aristas desde archivos CSV.
- Visualiza la red eléctrica.
- Calcula el árbol de expansión mínima (MST).
- Calcula el flujo de costo mínimo entre una subestación y un punto de consumo.
- Analiza la conectividad y robustez de la red.
- Exporta el grafo a formato GEXF para Gephi.

## Requisitos

- Python 3.x
- networkx
- matplotlib
- pandas
- numpy

Instala las dependencias con:

```bash
pip install networkx matplotlib pandas numpy
```

## Archivos de ejemplo

- `nodos_ejemplo.csv`: Nodos de la red (subestaciones y consumos).
- `aristas_ejemplo.csv`: Aristas de la red (líneas de transmisión).

## Visualización avanzada

El grafo puede exportarse a Gephi usando el método `exportar_gephi`.

---

¡Modifica los archivos CSV para probar diferentes configuraciones de red!