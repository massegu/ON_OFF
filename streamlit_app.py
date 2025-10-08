import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import time

st.set_page_config(layout="wide")
st.title("🧠 Simulación de campos receptivos ON y OFF")
st.markdown("Explora cómo diferentes tipos de células responden a bordes y contornos visuales.")

st.sidebar.header("🧠 Parámetros del estímulo")

estímulo = st.sidebar.selectbox("Selecciona el estímulo visual", [
    "Letra curva (C)",
    "Barra vertical",
    "Círculo",
    "Cuadrado",
    "Ruido aleatorio"
])

tipo_celda = st.sidebar.selectbox("Tipo de célula:", ["Centro ON / Periferia OFF", "Centro OFF / Periferia ON"])
visualizacion = st.sidebar.selectbox("Modo de visualización:", ["Mapa 2D", "Mapa 3D", "Animación paso a paso", "Comparación ON / OFF / Combinado", "Solo Bipolares"])
velocidad = st.sidebar.slider("Velocidad de animación (segundos por paso):", min_value=0.01, max_value=1.0, value=0.3, step=0.01) if visualizacion == "Animación paso a paso" else None

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
def generar_estímulo(nombre, tamaño=(20, 20)):
    img = np.zeros(tamaño)
    if nombre == "Letra curva (C)":
        img[5:15, 5] = 1
        img[5, 5:12] = 1
        img[15, 5:12] = 1
    elif nombre == "Barra vertical":
        img[:, tamaño[1]//2] = 1
    elif nombre == "Círculo":
        rr, cc = np.ogrid[:tamaño[0], :tamaño[1]]
        centro = (tamaño[0]//2, tamaño[1]//2)
        radio = 6
        mascara = (rr - centro[0])**2 + (cc - centro[1])**2 <= radio**2
        img[mascara] = 1
    elif nombre == "Cuadrado":
        img[6:14, 6:14] = 1
    elif nombre == "Ruido aleatorio":
        img = np.random.rand(*tamaño)
    return img

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

# Solo Bipolares
def procesamiento_bipolar(imagen):
    # Simulación: respuesta local sin antagonismo
    kernel = np.ones((5,5), np.float32) / 25
    salida = np.zeros_like(imagen)
    for fila in range(imagen.shape[0]-4):
        for col in range(imagen.shape[1]-4):
            sub = imagen[fila:fila+5, col:col+5]
            salida[fila+2, col+2] = np.sum(sub * kernel)
    return salida

def procesamiento_bipolar_off(imagen):
    # Simulación inversa: respuesta a decrementos de luz
    kernel = np.ones((5,5), np.float32) / 25
    salida = np.zeros_like(imagen)
    for fila in range(imagen.shape[0]-4):
        for col in range(imagen.shape[1]-4):
            sub = imagen[fila:fila+5, col:col+5]
            salida[fila+2, col+2] = -np.sum(sub * kernel)  # inversión de polaridad
    return salida

# Preparar datos
imagen = generar_estímulo(estímulo)
campo = construir_campo("ON" if tipo_celda.startswith("Centro ON") else "OFF")

if visualizacion == "Comparación ON / OFF / Combinado":
    campo_on = construir_campo("ON")
    campo_off = construir_campo("OFF")
else:
    activaciones = calcular_activaciones(imagen, campo)

# Visualización
if visualizacion == "Mapa 2D":
    fig, axs = plt.subplots(1, 3, figsize=(22,6))
    axs[0].imshow(imagen, cmap='gray')
    axs[0].set_title(f"Estímulo visual: {estímulo}")
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

    st.markdown("""
    <div style="padding: 1em; background-color: #f0f0f0; border-radius: 8px;">
    <b>🔍 Leyenda de colores:</b><br>
    🟩 <span style="color:green;"><b>Verde</b></span>: Activación de células <b>Centro ON / Periferia OFF</b>, que responden a incrementos de luz.<br>
    🟪 <span style="color:purple;"><b>Morado</b></span>: Activación de células <b>Centro OFF / Periferia ON</b>, que responden a decrementos de luz.<br>
    🔥 <span style="color:orange;"><b>Inferno</b></span>: Activación combinada ON + OFF, que representa la codificación completa del contorno.
    </div>
    """, unsafe_allow_html=True)

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

            for i in range(5):
                for j in range(5):
                    valor = campo[i, j]
                    if valor != 0:
                        color = 'green' if valor > 0 else 'purple'
                        alpha = abs(valor) / 6
                        rect = plt.Rectangle((col + j, fila + i), 1, 1, color=color, alpha=alpha)
                        ax.add_patch(rect)
                    ax.text(col + j + 0.5, fila + i + 0.5, f"{valor:.0f}", ha='center', va='center', fontsize=6, color='white')

            ax.add_patch(plt.Rectangle((col, fila), 5, 5, fill=False, edgecolor='blue', linewidth=2))
            ax.set_title(f"Campo en ({fila},{col})")
            ax.axis('off')
            plot_area.pyplot(fig_anim)
            act_area.metric(label="Activación", value=f"{act:.1f}")
            time.sleep(velocidad)

    st.markdown("""
    <div style="padding: 1em; background-color: #f9f9f9; border-radius: 8px;">
    <b>📊 Interpretación de los valores:</b><br>
    ✅ <b>Valores positivos</b>: indican que el campo receptivo está <span style="color:green;"><b>activado</b></span> en esa posición. Esto significa que la superposición entre el estímulo visual y la estructura del campo (centro/periferia) genera una respuesta excitatoria neta. La célula considera relevante esa región del estímulo.<br><br>
    ⚠️ <b>Valores negativos</b>: indican que el campo receptivo está <span style="color:red;"><b>inhibido</b></span> en esa posición. La superposición entre el estímulo y el campo genera una respuesta neta negativa, lo que sugiere que esa región del estímulo <b>reduce</b> la activación de la célula o no es significativa para ella.<br><br>
    🔁 Esta activación depende del tipo de célula (ON u OFF) y de cómo el campo receptivo se desplaza sobre el estímulo. El modo paso a paso permite observar cómo cambia la respuesta en cada posición del barrido.
    </div>
    """, unsafe_allow_html=True)

elif visualizacion == "Comparación ON / OFF / Combinado":
    # Construir campos
    campo_on = construir_campo("ON")
    campo_off = construir_campo("OFF")

    # Calcular activaciones
    activaciones_on = calcular_activaciones(imagen, campo_on)
    activaciones_off = calcular_activaciones(imagen, campo_off)

    # Normalizar cada mapa por separado
    norm_on = activaciones_on / np.max(activaciones_on) if np.max(activaciones_on) != 0 else activaciones_on
    norm_off = activaciones_off / np.max(activaciones_off) if np.max(activaciones_off) != 0 else activaciones_off

    # Combinación ponderada
    activaciones_comb = norm_on - norm_off  # contraste entre ON y OFF

    # Visualizar
    fig_comp, axs = plt.subplots(1, 3, figsize=(22,6))

    axs[0].imshow(norm_on, cmap='Greens')
    axs[0].set_title("🟩 Activación Centro ON / Periferia OFF")
    axs[0].axis('off')

    axs[1].imshow(norm_off, cmap='Purples')
    axs[1].set_title("🟪 Activación Centro OFF / Periferia ON")
    axs[1].axis('off')

    axs[2].imshow(activaciones_comb, cmap='bwr', vmin=-1, vmax=1)
    axs[2].set_title("🔀 Activación combinada ON - OFF")
    axs[2].axis('off')

    st.pyplot(fig_comp)

    st.markdown("""
    <div style="padding: 1em; background-color: #f0f0f0; border-radius: 8px;">
    <b>🔀 Interpretación del mapa combinado:</b><br>
    🔴 <b>Rojo</b>: activación neta positiva (predomina ON)<br>
    🔵 <b>Azul</b>: activación neta negativa (predomina OFF)<br>
    ⚪ <b>Blanco</b>: equilibrio entre ambas respuestas<br>
    Este mapa compara directamente la activación ON y OFF en cada región del estímulo, revelando zonas donde una domina sobre la otra.
    </div>
    """, unsafe_allow_html=True)

elif visualizacion == "Solo Bipolares":
    activacion_on = procesamiento_bipolar(imagen)
    activacion_off = procesamiento_bipolar_off(imagen)
    
    # Normalizar ON y OFF
    norm_on = activacion_on.copy()
    norm_off = activacion_off.copy()

    if np.max(np.abs(norm_on)) != 0:
            norm_on = norm_on / np.max(np.abs(norm_on))

    if np.max(np.abs(norm_off)) != 0:
            norm_off = norm_off / np.max(np.abs(norm_off))


    # Contraste bipolar
    contraste_bipolar = norm_on - norm_off

    fig_bip, axs = plt.subplots(1, 4, figsize=(28,6))

    axs[0].imshow(imagen, cmap='gray')
    axs[0].set_title(f"🎯 Estímulo visual: {estímulo}")
    axs[0].axis('off')

    axs[1].imshow(norm_on, cmap='Greens')
    axs[1].set_title("🟩 Bipolares ON (responden a luz)")
    axs[1].axis('off')

    axs[2].imshow(norm_off, cmap='Purples')
    axs[2].set_title("🟪 Bipolares OFF (responden a sombra)")
    axs[2].axis('off')

    axs[3].imshow(contraste_bipolar, cmap='bwr', vmin=-1, vmax=1)
    axs[3].set_title("🔀 Contraste bipolar ON - OFF")
    axs[3].axis('off')


    st.pyplot(fig_bip)

    st.markdown("""
    <div style="padding: 1em; background-color: #e8f4fc; border-radius: 8px;">
    <b>🧠 Comparativa de procesamiento bipolar:</b><br>
    - <span style="color:green;"><b>ON</b></span>: activadas por incrementos de luz, codifican zonas iluminadas.<br>
    - <span style="color:purple;"><b>OFF</b></span>: activadas por decrementos de luz, codifican zonas en sombra.<br>
    - <span style="color:red;"><b>Combinación ON + OFF</b></span>: permite detectar transiciones de luminancia, aunque sin el antagonismo espacial que aportan las ganglionares.<br><br>
    ⚠️ Esta codificación es más difusa que la de las ganglionares, pero ya introduce una polaridad funcional que prepara el terreno para el contraste espacial.

      <b>🧠 Procesamiento bipolar:</b><br>
    Las células bipolares responden de forma proporcional a la luminancia local, sin antagonismo espacial. Esta visualización muestra cómo se codifica la información visual si solo se procesara a nivel bipolar, sin la modulación centro ON / centro OFF de las ganglionares.<br><br>
    🔹 <b>Resultado:</b> Las células bipolares responden de forma proporcional a la luminancia local, es decir, transmiten la cantidad de luz que incide en cada punto de la retina sin realizar comparaciones con regiones vecinas.
    <br><br><b> En cambio, las células ganglionares introducen antagonismo espacial, una propiedad clave que permite detectar contrastes y bordes.</b> 
    <b>Este antagonismo se basa en comparar la luz que llega al centro del campo receptivo con la que llega a la periferia:</b>
    <br> Si el centro está iluminado y la periferia oscura (Centro ON), la célula se activa. 
     <br> Si el centro está oscuro y la periferia iluminada (Centro OFF), también se activa, pero con polaridad inversa.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="padding: 1em; background-color: #e8f4fc; border-radius: 8px;">
    <br><span style="color:red;"><b>Este mecanismo de antagonismo espacial no está presente en las bipolares, por lo que su respuesta es más difusa y menos selectiva.</span> </b>
       <br><br>
    <b>🔍 ¿Qué aporta el antagonismo espacial?</b>
    <br>
    * Permite detectar bordes, contornos y transiciones de luminancia.<br>
    * Mejora la eficiencia del sistema visual, reduciendo redundancia.<br>
    * Facilita la codificación de formas y objetos, incluso en condiciones de iluminación variable.<br>
    <br><b>En esta visualización, al mostrar solo el procesamiento bipolar, se observa una imagen suavizada, sin realce de bordes. Esto ilustra cómo las ganglionares enriquecen la percepción visual al añadir contraste espacial.</b>
    </div>
    """, unsafe_allow_html=True)
