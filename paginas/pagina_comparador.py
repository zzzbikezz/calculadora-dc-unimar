"""Página 6 (innovación): comparador de materiales y curva Rc vs sección."""
import pandas as pd
import streamlit as st

from calculadora.calculos import barrido_secciones, comparar_materiales
from calculadora.excepciones import ErrorDeValidacion
from calculadora.materiales import listar_materiales
from calculadora.validaciones import validar_numero, validar_seccion


def mostrar():
    st.title("🔬 Comparador de materiales")
    st.caption("Extra didáctico: mismo circuito con todos los materiales. No se guarda en el historial.")
    c1, c2, c3, c4 = st.columns(4)
    v = c1.text_input("Tensión (V)", "12")
    r = c2.text_input("Rcarga (Ω)", "10")
    l = c3.text_input("Longitud de ida (m)", "5")
    a = c4.text_input("Sección (mm²)", "2,5")
    try:
        tension = validar_numero(v, "Tensión (V)")
        carga = validar_numero(r, "Resistencia de carga (Ω)")
        longitud = validar_numero(l, "Longitud de ida (m)")
        seccion = validar_seccion(a)
    except ErrorDeValidacion as error:
        st.error(f"⚠️ Revise **{error.campo}**: {error.mensaje}")
        return

    filas = comparar_materiales(tension, carga, longitud, seccion)
    tabla = pd.DataFrame([{
        "Material": f["material"], "Rc (Ω)": round(f["rc_ohm"], 4), "I (A)": round(f["corriente_a"], 4),
        "Vc (V)": round(f["caida_tension_v"], 4), "Pc (W)": round(f["potencia_cable_w"], 4),
        "Caída (%)": round(f["caida_porcentaje"], 3)} for f in filas])
    st.subheader("Materiales ordenados de menor a mayor Rc")
    st.dataframe(tabla, hide_index=True)
    st.bar_chart(tabla.set_index("Material")["Pc (W)"])

    st.subheader("Rc según la sección")
    material = st.selectbox("Material", listar_materiales())
    secciones = [0.5, 0.75, 1, 1.5, 2.5, 4, 6, 10, 16]
    puntos = barrido_secciones(tension, carga, material, longitud, secciones)
    curva = pd.DataFrame(puntos).set_index("seccion_mm2")[["rc_ohm"]]
    curva.columns = ["Rc (Ω)"]
    st.line_chart(curva)
    st.caption("A mayor sección, menor resistencia del cable.")
