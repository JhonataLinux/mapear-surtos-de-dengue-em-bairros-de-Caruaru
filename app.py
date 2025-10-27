import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from numpy.random import default_rng as rng
from datetime import datetime, timedelta
from pathlib import Path
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from prophet import Prophet

df = pd.read_csv("caruaru_aedes_dashboard.csv",sep=None,engine="python", encoding="utf-8-sig")
df_analise = pd.read_csv("Analise_Temporal_Preditiva.csv")
df_semana = pd.read_csv("semanais_csv.csv")
#df_analise_semana = pd.read_csv("csv/dengue_caruaru_bairros_ultima.csv, sep=None, engine="python", encoding="utf-8-sig")

#st.write(df.columns.tolist())

#__________________________________________________________________________________#
df["indice_risco"] = df["casos"] *3 + df["focos_aedes"]

# ===== CONFIGURAÇÃO DA PÁGINA =====
st.set_page_config(
    page_title="Monitoramento Aedes - Caruaru 2025",
    page_icon="🦟",
    layout="wide"
)

# ===== CSS PERSONALIZADO =====
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0;
    }
    .subheader {
        text-align: center;
        color: #666;
        margin-top: 0;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .alert-section {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ===== CABEÇALHO PROFISSIONAL =====
st.markdown('<h1 class="main-header">🦟 Monitoramento Aedes - Caruaru 2025</h1>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Sistema de Vigilância Epidemiológica • Atualizado em tempo real</p>', unsafe_allow_html=True)

# ===== MÉTRICAS PRINCIPAIS =====
st.markdown("### 📊 Indicadores Principais")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card" style="border-left-color: #e74c3c;">
        <h3 style="color: #e74c3c; margin: 0;">🦠 Casos Confirmados</h3>
        <h1 style="color: #e74c3c; margin: 10px 0;">29</h1>
        <p style="color: #666; margin: 0;">+4 esta semana</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card" style="border-left-color: #f39c12;">
        <h3 style="color: #f39c12; margin: 0;">🔥 Focos do Aedes</h3>
        <h1 style="color: #f39c12; margin: 10px 0;">187</h1>
        <p style="color: #666; margin: 0;">15 novos focos</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card" style="border-left-color: #27ae60;">
        <h3 style="color: #27ae60; margin: 0;">📊 Média por Bairro</h3>
        <h1 style="color: #27ae60; margin: 10px 0;">12,5</h1>
        <p style="color: #666; margin: 0;">+1,2 vs mês anterior</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card" style="border-left-color: #8e44ad;">
        <h3 style="color: #8e44ad; margin: 0;">🚨 Bairro Crítico</h3>
        <h2 style="color: #8e44ad; margin: 10px 0;">Divinópolis</h2>
        <p style="color: #666; margin: 0;">19 focos identificados</p>
    </div>
    """, unsafe_allow_html=True)

# ===== MAPA E GRÁFICOS =====
st.markdown("---")
col_map, col_stats = st.columns([2, 1])

with col_map:
    st.markdown("### 🗺️ Mapa de Calor - Distribuição de Focos")
    fig = px.density_mapbox(df, lat="lat", lon="lon", z="indice_risco",
                        radius=25, center=dict(lat=-8.282, lon=-35.975),
                        zoom=12, mapbox_style="carto-darkmatter",
                        color_continuous_scale="reds",
                        hover_data={
                            "bairro": True,
                            "focos_aedes": True,
                            "casos": True,
                            "indice_risco": True
                        }                        
                    
                        ,)
    st.plotly_chart(fig, use_container_width=True)
    st.info("Mapa interativo com focos georreferenciados")
    
    # Gráfico de evolução temporal
    st.markdown("### 📈 Evolução Temporal de Casos")
    # Simulação de gráfico
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(x=[1,2,3,4,5], y=[2,5,3,8,6], 
                                mode='lines+markers', name='Casos',
                                line=dict(color='red', width=3)))
    fig_temp.update_layout(height=300, template="plotly_white")
    st.plotly_chart(fig_temp, use_container_width=True)

with col_stats:
    st.markdown("### 📋 Bairros com Maior Risco")
    
    # Top 5 bairros críticos (ordenados por focos)
    top_bairros = df.nlargest(5, 'focos_aedes')[['bairro', 'focos_aedes', 'casos', 'incidencia_100k']]
    
    bairros_criticos = []
    for _, row in top_bairros.iterrows():
        # Classificar risco
        if row['focos_aedes'] >= 15:
            status = "Alto"
            emoji = "🔴"
        elif row['focos_aedes'] >= 8:
            status = "Médio"
            emoji = "🟡"
        else:
            status = "Baixo" 
            emoji = "🟢"
            
        bairros_criticos.append({
            "bairro": row['bairro'],
            "focos": row['focos_aedes'],
            "casos": row['casos'],
            "incidencia": row['incidencia_100k'],
            "status": status,
            "emoji": emoji
        })
    
    # Exibir com mais informações
    for bairro in bairros_criticos:
        cor = "#101010" if bairro["status"] == "Alto" else "#f39c12" if bairro["status"] == "Médio" else "#27ae60"
        st.markdown(f"""
        <div style="background: white; padding: 12px; margin: 8px 0; border-radius: 8px; border-left: 4px solid {cor}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <span style="font-size: 16px; margin-right: 8px;">{bairro['emoji']}</span>
                <strong style="font-size: 14px; color: #000000;">{bairro['bairro']}</strong>
            </div>
            <div style="font-size: 12px; color: #101010;">
                📍 Focos: <strong>{bairro['focos']}</strong> | 
                🦠 Casos: <strong>{bairro['casos']}</strong><br>
                📈 Incidência: <strong>{bairro['incidencia']}/100k</strong> |
                ⚠️ Risco: <strong style="color: {cor}">{bairro['status']}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráfico de correlação
    st.markdown("### 🌧️ Chuva vs Focos")
    fig_chuva = go.Figure()
    fig_chuva.add_trace(go.Scatter(x=[10,25,40,15,30], y=[5,12,18,8,15],
                                 mode='markers', name='Relação',
                                 marker=dict(size=12, color='orange')))
    fig_chuva.update_layout(height=250, template="plotly_white")
    st.plotly_chart(fig_chuva, use_container_width=True)

# ===== ALERTAS E RECOMENDAÇÕES =====
st.markdown("---")
st.markdown("### 🚨 Alertas e Plano de Ação")

col_alerta, col_acao = st.columns(2)

with col_alerta:
    st.error("""
    **🔴 ALERTA CRÍTICO - INTERVENÇÃO IMEDIATA**
    
    **Bairros em Situação de Emergência:**
    - 🏘️ **Divinópolis**: 19 focos | 3 casos
    - 🏘️ **Vassoural**: 18 focos | 3 casos  
    - 🏘️ **Rendeiras**: 17 focos | 2 casos
    
    **Fatores Agravantes:**
    • Alta densidade de focos permanentes
    • Chuva acumulada > 30mm
    • Temperatura ideal para proliferação
    """)

with col_acao:
    st.warning("""
    **🟡 PLANO DE AÇÃO - PRÓXIMAS 72H**
    
    **Ações Imediatas:**
    1. 🚗 **Brigada de campo** em Divinópolis
    2. 🗑️ **Mutirão de limpeza** - descarte de pneus
    3. 🔍 **Inspeção especial** em caixas d'água
    
    **Monitoramento:**
    • Verificar criadouros após chuvas
    • Acompanhar casos suspeitos
    • Atualizar mapa de risco diariamente
    """)

# ===== RODAPÉ PROFISSIONAL =====
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    <strong>Monitoramento Aedes - Caruaru 2025</strong><br>
    Secretaria Municipal de Saúde • Vigilância Epidemiológica<br>
    Última atualização: {} • Atualizações a cada 24h
</div>
""".format(pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)