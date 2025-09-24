import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Estímulo visual: borde horizontal
imagen = np.zeros((10,10))
imagen[5:] = 1  # mitad inferior brillante

# Campo receptivo circular ON con centro fuerte
def construir_campo_circular():
    campo = np.zeros((5,5))
    for i in range(5):
        for j in range(5):
            distancia = np.sqrt((i-2)**2 + (j-2)**2)
            if distancia < 1.0:
                campo[i,j] = 6  # centro activador
            elif distancia < 2.0:
                campo[i,j] = -1  # periferia inhibidora
    return campo

campo = construir_campo_circular()

# Aplicar campo en posición (fila, col)
def aplicar_en_posicion(imagen, campo, fila, col):
    subimagen = imagen[fila:fila+5, col:col+5]
    producto = subimagen * campo
    activacion = np.sum(producto)
    return subimagen, producto, activacion

# Interfaz Streamlit
st.title("🧠 Campo receptivo ON sobre borde visual")
st.markdown("Este ejercicio simula cómo un campo receptivo circular responde al desplazamiento vertical sobre un borde horizontal.")

# Slider para controlar la posición vertical
fila = st.slider("Desplazamiento vertical del campo:", min_value=0, max_value=5, step=1)
col = 2  # posición horizontal fija

subimg, producto, act = aplicar_en_posicion(imagen, campo, fila, col)

fig, axs = plt.subplots(1, 3, figsize=(20,6))

# Panel 1: Estímulo con borde marcado
axs[0].imshow(imagen, cmap='gray')
axs[0].axhline(4.5, color='red', linestyle='--', linewidth=2)
axs[0].add_patch(plt.Rectangle((col,fila),5,5,fill=False,edgecolor='blue',linewidth=2))
axs[0].set_title(f"Estímulo visual\nCampo en ({fila},{col})")
axs[0].axis('off')

# Panel 2: Campo receptivo circular
axs[1].imshow(campo, cmap='bwr', vmin=-6, vmax=6)
axs[1].set_title("Campo receptivo circular")
for i in range(5):
    for j in range(5):
        val = campo[i,j]
        axs[1].text(j, i, f"{val:.0f}", ha='center', va='center', color='black', fontsize=8)
circ = plt.Circle((2,2), 2.0, color='black', fill=False, linestyle='--', linewidth=1)
axs[1].add_patch(circ)
axs[1].grid(True)
axs[1].set_xticks(np.arange(-0.5, 5, 1))
axs[1].set_yticks(np.arange(-0.5, 5, 1))
axs[1].set_xticklabels([])
axs[1].set_yticklabels([])
axs[1].set_xlim(-0.5, 4.5)
axs[1].set_ylim(-0.5, 4.5)

# Panel 3: Activación con línea base
axs[2].bar([0], [act], color='limegreen')
axs[2].axhline(0, color='black', linestyle='--')
axs[2].set_ylim(act - 10, act + 10)
axs[2].set_title(f"Activación total: {act:.1f}")
axs[2].set_xticks([])
axs[2].grid(True)

plt.tight_layout()
st.pyplot(fig)
