import streamlit as st
import json
from datetime import datetime
import os
from typing import Dict, List, Optional

# ==================== CONFIGURACIÓN DE LA APLICACIÓN ====================
st.set_page_config(
    page_title="Sistema de Inventario - Joyería",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CONSTANTES Y CONFIGURACIÓN ====================
DATA_FILE = "inventario_joyeria.json"
CONFIG_FILE = "config_sistema.json"

# Tablas de configuración precargadas
CATEGORIAS = {
    "AN": "Anillo",
    "PU": "Pulsera",
    "AR": "Aretes",
    "SE": "Sets",
    "CA": "Cadenas"
}

MATERIALES = {
    "O18": "Oro 18K",
    "O14": "Oro 14K",
    "OB": "Oro Blanco",
    "OR": "Oro Rosa",
    "P92": "Plata 925",
    "PV": "Plata con Baño de Oro",
    "AC": "Acero Inoxidable",
    "PT": "Platino",
    "GF": "Laminado de Oro"
}

# Rango de tallas para anillos
TALLAS_ANILLO = [str(i) for i in range(4, 13)]  # 4, 5, 6, 7, 8, 9, 10, 11, 12

# ==================== ESTILOS CSS ====================
st.markdown("""
    <style>
    /* Estilos generales */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Tarjetas de producto */
    .producto-card {
        background: white;
        padding: 24px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin: 16px 0;
        border-left: 4px solid #2c3e50;
    }
    
    /* Tarjeta de calculadora */
    .calculadora-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin: 16px 0;
        color: white;
    }
    
    .calculadora-title {
        color: white;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    
    .calculadora-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 14px;
    }
    
    /* Encabezados */
    .producto-header {
        color: #2c3e50;
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .producto-sku {
        color: #7f8c8d;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 16px;
    }
    
    /* Etiquetas de tallas */
    .talla-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
    }
    
    .talla-badge {
        background-color: #ecf0f1;
        padding: 8px 16px;
        border-radius: 4px;
        border: 1px solid #bdc3c7;
        font-size: 14px;
        font-weight: 500;
    }
    
    .talla-badge-low {
        background-color: #fadbd8;
        border-color: #e74c3c;
        color: #c0392b;
    }
    
    .talla-badge-ok {
        background-color: #d5f4e6;
        border-color: #27ae60;
        color: #1e8449;
    }
    
    /* Métricas */
    .metric-container {
        background: white;
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }
    
    /* Resultado del cálculo */
    .resultado-precio {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .resultado-label {
        color: white;
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 8px;
    }
    
    .resultado-valor {
        color: white;
        font-size: 36px;
        font-weight: 700;
    }
    
    /* Desglose de cálculo */
    .desglose-item {
        background: #f8f9fa;
        padding: 12px;
        border-radius: 4px;
        margin: 8px 0;
        border-left: 3px solid #3498db;
    }
    
    /* Tablas */
    .dataframe {
        font-size: 14px;
    }
    
    /* Títulos de sección */
    .section-title {
        color: #2c3e50;
        font-size: 20px;
        font-weight: 600;
        margin: 24px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #3498db;
    }
    
    /* Botones personalizados */
    .stButton > button {
        border-radius: 4px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    /* Alertas */
    .alert-info {
        background-color: #d6eaf8;
        border-left: 4px solid #3498db;
        padding: 12px;
        border-radius: 4px;
        margin: 12px 0;
    }
    
    .alert-success {
        background-color: #d5f4e6;
        border-left: 4px solid #27ae60;
        padding: 12px;
        border-radius: 4px;
        margin: 12px 0;
    }
    
    .alert-warning {
        background-color: #fcf3cf;
        border-left: 4px solid #f39c12;
        padding: 12px;
        border-radius: 4px;
        margin: 12px 0;
    }
    
    .alert-error {
        background-color: #fadbd8;
        border-left: 4px solid #e74c3c;
        padding: 12px;
        border-radius: 4px;
        margin: 12px 0;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Espaciado */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== FUNCIONES DE DATOS ====================

def cargar_datos() -> Dict:
    """Carga los datos del inventario desde el archivo JSON"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error al cargar datos: {e}")
            return {}
    return {}

def guardar_datos(datos: Dict) -> bool:
    """Guarda los datos del inventario en el archivo JSON"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Error al guardar datos: {e}")
        return False

def cargar_configuracion() -> Dict:
    """Carga la configuración del sistema (correlativos)"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return inicializar_configuracion()
    return inicializar_configuracion()

def inicializar_configuracion() -> Dict:
    """Inicializa la configuración con correlativos en cero"""
    config = {
        "correlativos": {}
    }
    
    # Inicializar correlativos para cada combinación de categoría-material
    for cat_code in CATEGORIAS.keys():
        for mat_code in MATERIALES.keys():
            key = f"{cat_code}-{mat_code}"
            config["correlativos"][key] = 0
    
    guardar_configuracion(config)
    return config

def guardar_configuracion(config: Dict) -> bool:
    """Guarda la configuración del sistema"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def generar_sku(categoria_code: str, material_code: str) -> str:
    """Genera el siguiente SKU basado en la categoría y material"""
    config = cargar_configuracion()
    key = f"{categoria_code}-{material_code}"
    
    # Obtener el siguiente correlativo
    correlativo_actual = config["correlativos"].get(key, 0)
    nuevo_correlativo = correlativo_actual + 1
    
    # Actualizar configuración
    config["correlativos"][key] = nuevo_correlativo
    guardar_configuracion(config)
    
    # Generar SKU con formato: CATEGORIA-MATERIAL-CORRELATIVO (3 dígitos)
    sku = f"{categoria_code}-{material_code}-{nuevo_correlativo:03d}"
    return sku

def calcular_stock_total(producto: Dict) -> int:
    """Calcula el stock total de un producto"""
    if "tallas" in producto and producto["tallas"]:
        return sum(producto["tallas"].values())
    else:
        return producto.get("cantidad_total", 0)

def calcular_valor_inventario(inventario: Dict) -> float:
    """Calcula el valor total del inventario a precio de venta"""
    valor_total = 0
    for producto in inventario.values():
        stock = calcular_stock_total(producto)
        precio_venta = producto.get("precio_venta", 0)
        valor_total += stock * precio_venta
    return valor_total

def calcular_precio_sugerido(precio_compra: float, packaging: float, envio: float, 
                            marketing: float, comision_shopify: float) -> float:
    """
    Calcula el precio de venta sugerido usando la fórmula:
    (Precio Compra + Packaging + Envío + Marketing + Comisión Shopify) × 2
    """
    total_costos = precio_compra + packaging + envio + marketing + comision_shopify
    precio_sugerido = total_costos * 2
    return precio_sugerido

# ==================== INICIALIZACIÓN DE SESSION STATE ====================

if 'inventario' not in st.session_state:
    st.session_state.inventario = cargar_datos()

if 'tallas_temp' not in st.session_state:
    st.session_state.tallas_temp = {}

if 'categoria_seleccionada' not in st.session_state:
    st.session_state.categoria_seleccionada = None

if 'material_seleccionado' not in st.session_state:
    st.session_state.material_seleccionado = None

# ==================== ENCABEZADO DE LA APLICACIÓN ====================

st.title("Sistema de Inventario - Joyería")
st.markdown("---")

# ==================== PESTAÑAS PRINCIPALES ====================

tab1, tab2, tab3, tab4 = st.tabs([
    "Registrar Producto",
    "Buscar y Gestionar",
    "Calculadora de Margen",
    "Inventario General"
])

# ==================== PESTAÑA 1: REGISTRAR PRODUCTO ====================

with tab1:
    st.header("Registro de Nuevo Producto")
    
    # Sección 1: Selección de Categoría y Material
    st.markdown('<div class="section-title">Clasificación del Producto</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        categoria_options = [f"{code} - {nombre}" for code, nombre in CATEGORIAS.items()]
        categoria_sel = st.selectbox(
            "Categoría del Producto",
            options=categoria_options,
            key="categoria_select"
        )
        categoria_code = categoria_sel.split(" - ")[0]
        st.session_state.categoria_seleccionada = categoria_code
    
    with col2:
        material_options = [f"{code} - {nombre}" for code, nombre in MATERIALES.items()]
        material_sel = st.selectbox(
            "Material del Producto",
            options=material_options,
            key="material_select"
        )
        material_code = material_sel.split(" - ")[0]
        st.session_state.material_seleccionado = material_code
    
    # Generar y mostrar el SKU que se asignará
    if categoria_code and material_code:
        # Simular el siguiente SKU (sin incrementar el correlativo aún)
        config = cargar_configuracion()
        key = f"{categoria_code}-{material_code}"
        correlativo_siguiente = config["correlativos"].get(key, 0) + 1
        sku_preview = f"{categoria_code}-{material_code}-{correlativo_siguiente:03d}"
        
        st.info(f"Código SKU que se asignará: **{sku_preview}**")
    
    st.markdown("---")
    
    # Sección 2: Información del Producto
    st.markdown('<div class="section-title">Información del Producto</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        descripcion = st.text_input(
            "Descripción del Producto",
            placeholder="Ej: Anillo con Diamante Central",
            key="descripcion_input"
        )
        peso = st.number_input(
            "Peso (gramos)",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            key="peso_input"
        )
    
    with col2:
        precio_costo = st.number_input(
            "Precio de Compra ($)",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            key="costo_input"
        )
        precio_venta = st.number_input(
            "Precio de Venta ($)",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            key="venta_input"
        )
    
    st.markdown("---")
    
    # Sección 3: Gestión de Stock (Condicional según categoría)
    st.markdown('<div class="section-title">Gestión de Stock</div>', unsafe_allow_html=True)
    
    # LÓGICA CONDICIONAL: Si es ANILLO (AN), mostrar tallas; si no, mostrar cantidad total
    es_anillo = (categoria_code == "AN")
    
    if es_anillo:
        st.markdown("**Seleccione las tallas disponibles y sus cantidades:**")
        
        # Mostrar tallas ya agregadas
        if st.session_state.tallas_temp:
            st.markdown("**Tallas agregadas:**")
            cols = st.columns(4)
            for idx, (talla, cantidad) in enumerate(sorted(st.session_state.tallas_temp.items())):
                with cols[idx % 4]:
                    st.markdown(f"""
                        <div class="talla-badge">
                            Talla {talla}: {cantidad} unidades
                        </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("")
        
        # Formulario para agregar tallas
        col_t1, col_t2, col_t3 = st.columns([2, 2, 1])
        
        with col_t1:
            talla_seleccionada = st.selectbox(
                "Talla del Anillo",
                options=TALLAS_ANILLO,
                key="talla_select"
            )
        
        with col_t2:
            cantidad_talla = st.number_input(
                "Cantidad",
                min_value=1,
                value=1,
                key="cantidad_talla_input"
            )
        
        with col_t3:
            st.markdown("")
            st.markdown("")
            if st.button("Agregar Talla", type="secondary"):
                if talla_seleccionada in st.session_state.tallas_temp:
                    st.warning(f"La talla {talla_seleccionada} ya fue agregada. Puede eliminarla y agregarla nuevamente con la cantidad correcta.")
                else:
                    st.session_state.tallas_temp[talla_seleccionada] = cantidad_talla
                    st.rerun()
        
        # Botón para limpiar tallas
        if st.session_state.tallas_temp:
            if st.button("Limpiar Todas las Tallas", type="secondary"):
                st.session_state.tallas_temp = {}
                st.rerun()
    
    else:
        # Para productos que NO son anillos, mostrar solo cantidad total
        st.markdown("**Este producto no requiere tallas. Ingrese la cantidad total disponible:**")
        
        cantidad_total = st.number_input(
            "Cantidad Total en Stock",
            min_value=0,
            value=1,
            key="cantidad_total_input"
        )
    
    st.markdown("---")
    
    # Botones de acción
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    
    with col_btn1:
        if st.button("Guardar Producto", type="primary", use_container_width=True):
            # Validaciones
            if not descripcion:
                st.error("Debe ingresar una descripción del producto")
            elif peso <= 0:
                st.error("El peso debe ser mayor a cero")
            elif precio_costo <= 0 or precio_venta <= 0:
                st.error("Los precios deben ser mayores a cero")
            elif es_anillo and not st.session_state.tallas_temp:
                st.error("Debe agregar al menos una talla para los anillos")
            else:
                # Generar SKU definitivo
                sku_final = generar_sku(categoria_code, material_code)
                
                # Crear registro del producto
                nuevo_producto = {
                    "sku": sku_final,
                    "categoria_code": categoria_code,
                    "categoria_nombre": CATEGORIAS[categoria_code],
                    "material_code": material_code,
                    "material_nombre": MATERIALES[material_code],
                    "descripcion": descripcion,
                    "peso": peso,
                    "precio_costo": precio_costo,
                    "precio_venta": precio_venta,
                    "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Agregar tallas o cantidad total según corresponda
                if es_anillo:
                    nuevo_producto["tallas"] = st.session_state.tallas_temp.copy()
                else:
                    nuevo_producto["cantidad_total"] = cantidad_total
                
                # Guardar en inventario
                st.session_state.inventario[sku_final] = nuevo_producto
                guardar_datos(st.session_state.inventario)
                
                # Limpiar formulario
                st.session_state.tallas_temp = {}
                
                st.success(f"Producto registrado exitosamente con SKU: {sku_final}")
                st.rerun()
    
    with col_btn2:
        if st.button("Limpiar Formulario", use_container_width=True):
            st.session_state.tallas_temp = {}
            st.rerun()

# ==================== PESTAÑA 2: BUSCAR Y GESTIONAR ====================

with tab2:
    st.header("Búsqueda y Gestión de Productos")
    
    # Buscador
    busqueda = st.text_input(
        "Buscar producto por SKU",
        placeholder="Ingrese el código SKU (Ej: AN-O18-001)",
        key="buscar_input"
    )
    
    if busqueda:
        busqueda = busqueda.strip().upper()
        
        if busqueda in st.session_state.inventario:
            producto = st.session_state.inventario[busqueda]
            
            # Tarjeta de producto
            st.markdown(f"""
                <div class="producto-card">
                    <div class="producto-header">{producto['descripcion']}</div>
                    <div class="producto-sku">SKU: {producto['sku']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Información general en columnas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Categoría", producto['categoria_nombre'])
            with col2:
                st.metric("Material", producto['material_nombre'])
            with col3:
                st.metric("Peso", f"{producto['peso']:.2f} gr")
            with col4:
                stock_total = calcular_stock_total(producto)
                st.metric("Stock Total", f"{stock_total} unidades")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Precio de Costo", f"${producto['precio_costo']:,.2f}")
            with col2:
                st.metric("Precio de Venta", f"${producto['precio_venta']:,.2f}")
            
            st.markdown("---")
            
            # Gestión de stock según tipo de producto
            st.markdown('<div class="section-title">Gestión de Existencias</div>', unsafe_allow_html=True)
            
            if "tallas" in producto and producto["tallas"]:
                # Producto con tallas (Anillos)
                st.markdown("**Desglose por Talla:**")
                
                tallas_list = sorted(producto["tallas"].items())
                num_cols = min(3, len(tallas_list))
                
                if num_cols > 0:
                    cols = st.columns(num_cols)
                    
                    for idx, (talla, cantidad) in enumerate(tallas_list):
                        with cols[idx % num_cols]:
                            st.markdown(f"**Talla {talla}**")
                            
                            # Mostrar cantidad con color
                            if cantidad <= 2:
                                st.markdown(f'<div class="talla-badge-low">Stock: {cantidad} unidades</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="talla-badge-ok">Stock: {cantidad} unidades</div>', unsafe_allow_html=True)
                            
                            # Controles de ajuste
                            col_menos, col_mas, col_ajuste = st.columns([1, 1, 2])
                            
                            with col_menos:
                                if st.button("-", key=f"menos_{busqueda}_{talla}", use_container_width=True):
                                    if st.session_state.inventario[busqueda]['tallas'][talla] > 0:
                                        st.session_state.inventario[busqueda]['tallas'][talla] -= 1
                                        guardar_datos(st.session_state.inventario)
                                        st.rerun()
                            
                            with col_mas:
                                if st.button("+", key=f"mas_{busqueda}_{talla}", use_container_width=True):
                                    st.session_state.inventario[busqueda]['tallas'][talla] += 1
                                    guardar_datos(st.session_state.inventario)
                                    st.rerun()
                            
                            with col_ajuste:
                                nuevo_valor = st.number_input(
                                    "Ajustar",
                                    min_value=0,
                                    value=cantidad,
                                    key=f"ajuste_{busqueda}_{talla}",
                                    label_visibility="collapsed"
                                )
                                if nuevo_valor != cantidad:
                                    st.session_state.inventario[busqueda]['tallas'][talla] = nuevo_valor
                                    guardar_datos(st.session_state.inventario)
                                    st.rerun()
            
            else:
                # Producto sin tallas (unitalla)
                cantidad_actual = producto.get("cantidad_total", 0)
                
                st.markdown(f"**Cantidad en Stock:** {cantidad_actual} unidades")
                
                col1, col2, col3 = st.columns([1, 1, 3])
                
                with col1:
                    if st.button("-", key=f"menos_{busqueda}", use_container_width=True):
                        if st.session_state.inventario[busqueda]['cantidad_total'] > 0:
                            st.session_state.inventario[busqueda]['cantidad_total'] -= 1
                            guardar_datos(st.session_state.inventario)
                            st.rerun()
                
                with col2:
                    if st.button("+", key=f"mas_{busqueda}", use_container_width=True):
                        st.session_state.inventario[busqueda]['cantidad_total'] += 1
                        guardar_datos(st.session_state.inventario)
                        st.rerun()
                
                with col3:
                    nuevo_valor = st.number_input(
                        "Ajustar cantidad",
                        min_value=0,
                        value=cantidad_actual,
                        key=f"ajuste_{busqueda}"
                    )
                    if nuevo_valor != cantidad_actual:
                        st.session_state.inventario[busqueda]['cantidad_total'] = nuevo_valor
                        guardar_datos(st.session_state.inventario)
                        st.rerun()
            
            st.markdown("---")
            
            # Botón para eliminar producto
            if st.button(f"Eliminar Producto {busqueda}", type="secondary"):
                del st.session_state.inventario[busqueda]
                guardar_datos(st.session_state.inventario)
                st.success(f"Producto {busqueda} eliminado correctamente")
                st.rerun()
        
        else:
            st.warning(f"No se encontró ningún producto con el SKU: {busqueda}")
    
    else:
        st.info("Ingrese un código SKU en el campo de búsqueda para ver los detalles del producto")

# ==================== PESTAÑA 3: CALCULADORA DE MARGEN ====================

with tab3:
    st.header("Calculadora de Margen de Precio")
    
    # Tarjeta destacada de calculadora
    st.markdown("""
        <div class="calculadora-card">
            <div class="calculadora-title">Calculadora de Precio de Venta</div>
            <div class="calculadora-subtitle">
                Calcule el precio de venta óptimo considerando todos los costos asociados
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    if not st.session_state.inventario:
        st.warning("No hay productos registrados en el inventario. Primero debe registrar productos en la pestaña 'Registrar Producto'.")
    else:
        # Selector de producto
        st.markdown('<div class="section-title">Seleccionar Producto</div>', unsafe_allow_html=True)
        
        # Crear lista de opciones para el selector
        productos_opciones = [
            f"{sku} - {datos['descripcion']}" 
            for sku, datos in st.session_state.inventario.items()
        ]
        
        producto_seleccionado = st.selectbox(
            "Seleccione el producto para calcular precio",
            options=productos_opciones,
            key="calc_producto_select"
        )
        
        if producto_seleccionado:
            # Extraer SKU seleccionado
            sku_seleccionado = producto_seleccionado.split(" - ")[0]
            producto_data = st.session_state.inventario[sku_seleccionado]
            
            st.markdown("---")
            
            # Mostrar información del producto seleccionado
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("SKU", sku_seleccionado)
            with col2:
                st.metric("Categoría", producto_data['categoria_nombre'])
            with col3:
                st.metric("Material", producto_data['material_nombre'])
            
            st.markdown("---")
            
            # Sección de costos
            st.markdown('<div class="section-title">Costos del Producto</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Precio de compra (mostrar el actual, no editable aquí)
                precio_compra_actual = producto_data['precio_costo']
                st.metric("Precio de Compra Actual", f"${precio_compra_actual:,.2f}")
                
                st.markdown("")
                
                # Campos editables para costos adicionales
                precio_packaging = st.number_input(
                    "Precio de Packaging ($)",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                    key="calc_packaging"
                )
                
                precio_envio = st.number_input(
                    "Precio de Envío ($)",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                    key="calc_envio"
                )
            
            with col2:
                st.markdown("")
                st.markdown("")
                st.markdown("")
                
                gasto_marketing = st.number_input(
                    "Gasto de Marketing ($)",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                    key="calc_marketing"
                )
                
                comision_shopify = st.number_input(
                    "Comisión/Gasto de Shopify ($)",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                    key="calc_shopify"
                )
            
            st.markdown("---")
            
            # Calcular precio sugerido
            precio_sugerido = calcular_precio_sugerido(
                precio_compra_actual,
                precio_packaging,
                precio_envio,
                gasto_marketing,
                comision_shopify
            )
            
            # Mostrar desglose del cálculo
            st.markdown('<div class="section-title">Desglose del Cálculo</div>', unsafe_allow_html=True)
            
            total_costos = precio_compra_actual + precio_packaging + precio_envio + gasto_marketing + comision_shopify
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                    <div class="desglose-item">
                        <strong>Precio de Compra:</strong> ${precio_compra_actual:,.2f}
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="desglose-item">
                        <strong>Packaging:</strong> ${precio_packaging:,.2f}
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="desglose-item">
                        <strong>Envío:</strong> ${precio_envio:,.2f}
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="desglose-item">
                        <strong>Marketing:</strong> ${gasto_marketing:,.2f}
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="desglose-item">
                        <strong>Comisión Shopify:</strong> ${comision_shopify:,.2f}
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="desglose-item">
                        <strong>TOTAL COSTOS:</strong> ${total_costos:,.2f}
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("")
            
            # Mostrar fórmula
            st.info(f"Fórmula aplicada: (${total_costos:,.2f}) × 2 = ${precio_sugerido:,.2f}")
            
            # Resultado destacado
            st.markdown(f"""
                <div class="resultado-precio">
                    <div class="resultado-label">PRECIO DE VENTA SUGERIDO</div>
                    <div class="resultado-valor">${precio_sugerido:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Comparación con precio actual
            precio_venta_actual = producto_data['precio_venta']
            diferencia = precio_sugerido - precio_venta_actual
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Precio Venta Actual", f"${precio_venta_actual:,.2f}")
            with col2:
                st.metric("Precio Sugerido", f"${precio_sugerido:,.2f}")
            with col3:
                st.metric(
                    "Diferencia", 
                    f"${abs(diferencia):,.2f}",
                    delta=f"{diferencia:,.2f}"
                )
            
            st.markdown("---")
            
            # Botón para actualizar precio
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col2:
                if st.button("Actualizar Precio de Venta", type="primary", use_container_width=True):
                    # Actualizar el precio en el inventario
                    st.session_state.inventario[sku_seleccionado]['precio_venta'] = precio_sugerido
                    
                    # Guardar cambios
                    if guardar_datos(st.session_state.inventario):
                        st.success(f"Precio de venta actualizado exitosamente a ${precio_sugerido:,.2f}")
                        st.rerun()
                    else:
                        st.error("Error al guardar el nuevo precio")

# ==================== PESTAÑA 4: INVENTARIO GENERAL ====================

with tab4:
    st.header("Inventario General")
    
    if st.session_state.inventario:
        # Métricas generales
        total_productos = len(st.session_state.inventario)
        total_unidades = sum(calcular_stock_total(p) for p in st.session_state.inventario.values())
        valor_total = calcular_valor_inventario(st.session_state.inventario)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Productos", total_productos)
        with col2:
            st.metric("Total de Unidades", total_unidades)
        with col3:
            st.metric("Valor Total del Inventario", f"${valor_total:,.2f}")
        
        st.markdown("---")
        
        # Tabla de inventario
        st.markdown('<div class="section-title">Lista Completa de Productos</div>', unsafe_allow_html=True)
        
        # Preparar datos para la tabla
        tabla_datos = []
        
        for sku, producto in st.session_state.inventario.items():
            stock = calcular_stock_total(producto)
            valor_stock = stock * producto['precio_venta']
            
            tabla_datos.append({
                "SKU": sku,
                "Descripción": producto['descripcion'],
                "Categoría": producto['categoria_nombre'],
                "Material": producto['material_nombre'],
                "Peso (gr)": f"{producto['peso']:.2f}",
                "Precio Costo": f"${producto['precio_costo']:,.2f}",
                "Precio Venta": f"${producto['precio_venta']:,.2f}",
                "Stock": stock,
                "Valor en Stock": f"${valor_stock:,.2f}"
            })
        
        # Mostrar tabla
        if tabla_datos:
            import pandas as pd
            df = pd.DataFrame(tabla_datos)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Detalles expandibles por producto
        st.markdown('<div class="section-title">Detalles por Producto</div>', unsafe_allow_html=True)
        
        for sku, producto in sorted(st.session_state.inventario.items()):
            with st.expander(f"{sku} - {producto['descripcion']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Categoría:** {producto['categoria_nombre']}")
                    st.write(f"**Material:** {producto['material_nombre']}")
                    st.write(f"**Peso:** {producto['peso']:.2f} gr")
                    st.write(f"**Precio de Costo:** ${producto['precio_costo']:,.2f}")
                    st.write(f"**Precio de Venta:** ${producto['precio_venta']:,.2f}")
                
                with col2:
                    if "tallas" in producto and producto["tallas"]:
                        st.write("**Tallas disponibles:**")
                        for talla, cant in sorted(producto["tallas"].items()):
                            indicador = "BAJO" if cant <= 2 else "OK"
                            st.write(f"- Talla {talla}: {cant} unidades ({indicador})")
                    else:
                        cantidad = producto.get("cantidad_total", 0)
                        st.write(f"**Cantidad Total:** {cantidad} unidades")
    
    else:
        st.info("No hay productos registrados en el inventario. Vaya a la pestaña 'Registrar Producto' para comenzar.")

# ==================== PIE DE PÁGINA ====================

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #7f8c8d; padding: 20px;'>
        <p><strong>Sistema de Inventario para Joyería</strong> | Versión 2.0</p>
        <p>Desarrollado con Python y Streamlit | Incluye Calculadora de Margen</p>
    </div>
""", unsafe_allow_html=True)
