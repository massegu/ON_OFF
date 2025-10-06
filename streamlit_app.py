import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import time

st.set_page_config(layout="wide")
st.title("🧠 Simulación de campos receptivos ON y OFF")
st.markdown("Explora cómo diferentes tipos de células responden a bordes y contornos visuales.")

# Menú lateral
modo = st.sidebar.selectbox("Tipo de estímulo:", ["Borde horizontal", "Letra curva (C)"])
tipo_celda = st.sidebar.selectbox("Tipo de célula:", ["Centro ON / Periferia OFF", "Centro OFF / Periferia ON"])
visualizacion = st.sidebar.selectbox("Modo de visualización:", ["Mapa 2D", "Mapa 3D", "Animación paso a paso"])
velocidad = st.sidebar.slider("Velocidad de animación (segundos por paso):", 0.1, 1.0, 0.3) if visualizacion == "Animación paso a paso" else None

# Construcción de campos receptivos
def construir_campo(tipo="ON"):
    campo = np.zeros((5,5))
    for i in range(5):
        for j in range(5):
            distancia = np.sqrt((i-2)**2 + (j-2)**2)
            if distancia < 1.0:
                campo[i,j] = 6 if tipo=="ON" else -6
            elif distancia < 2.0:
                campo[i,j] = -1 if tipo=="ON" else 1
    return campo

# Estímulo visual
def construir_estimulo(modo):
    imagen = np.zeros((10,10))
    if modo == "Borde horizontal":
        imagen[5:] = 1
    else:
        imagen[2:8,2] = 1
        imagen[2,2:7] = 1
        imagen[7,2:7] = 1
    return imagen

# Aplicar campo en posición
def aplicar_en_posicion(imagen, campo, fila, col):
    subimagen = imagen[fila:fila+5, col:col+5]
    if subimagen.shape != (5,5):
        return None
    return np.sum(subimagen * campo)

# Activación completa
def calcular_activaciones(imagen, campo):
    activaciones = np.zeros_like(imagen)
    for fila in range(imagen.shape[0]-4):
        for col in range(imagen.shape[1]-4):
            act = aplicar_en_posicion(imagen, campo, fila, col)
            if act is not None:
                activaciones[fila+2, col+2] = act
    return activaciones

# Preparar datos
imagen = construir_estimulo(modo)
campo = construir_campo("ON" if tipo_celda.startswith("Centro ON") else "OFF")
activaciones = calcular_activaciones(imagen, campo)

# Visualización
if visualizacion == "Mapa 2D":
    fig, axs = plt.subplots(1, 3, figsize=(22,6))

    axs[0].imshow(imagen, cmap='gray')
    axs[0].set_title(f"Estímulo visual: {modo}")
    axs[0].axis('off')

    axs[1].imshow(campo, cmap='bwr', vmin=-6, vmax=6)
    axs[1].set_title(f"Campo receptivo: {tipo_celda}")
    for i in range(5):
        for j in range(5):
            val = campo[i,j]
            axs[1].text(j, i, f"{val:.0f}", ha='center', va='center', color='black', fontsize=8)
    circ = plt.Circle((2,2), 2.0, color='black', fill=False, linestyle='--', linewidth=1)
    axs[1].add_patch(circ)
    axs[1].grid(True)
    axs[1].axis('off')

    axs[2].imshow(activaciones, cmap='viridis')
    axs[2].set_title("Activación de múltiples células")
    axs[2].axis('off')

    st.pyplot(fig)

elif visualizacion == "Mapa 3D":
    x, y = np.meshgrid(np.arange(activaciones.shape[1]), np.arange(activaciones.shape[0]))
    fig3d = go.Figure(data=[go.Surface(z=activaciones, x=x, y=y, colorscale='Viridis')])
    fig3d.update_layout(title="🌄 Mapa 3D de activación", autosize=True,
                        margin=dict(l=20, r=20, t=40, b=20),
                        scene=dict(zaxis_title='Activación', xaxis_title='Columna', yaxis_title='Fila'))
    st.plotly_chart(fig3d, use_container_width=True)

elif visualizacion == "Animación paso a paso":
    col1, col2 = st.columns([2,1])
    with col1:
        fig_anim, ax = plt.subplots(figsize=(6,6))
        ax.imshow(imagen, cmap='gray')
        ax.set_title("Barrido del campo receptivo")
        ax.axis('off')
        plot_area = st.empty()

    with col2:
        st.markdown("### Activación en cada paso")
        act_area = st.empty()

    for fila in range(imagen.shape[0]-4):
        for col in range(imagen.shape[1]-4):
            act = aplicar_en_posicion(imagen, campo, fila, col)
            ax.clear()
            ax.imshow(imagen, cmap='gray')
            ax.add_patch(plt.Rectangle((col,fila),5,5,fill=False,edgecolor='blue',linewidth=2))
            ax.set_title(f"Campo en ({fila},{col})")
            ax.axis('off')
            plot_area.pyplot(fig_anim)
            act_area.metric(label="Activación", value=f"{act:.1f}")
            time.sleep(velocidad)


