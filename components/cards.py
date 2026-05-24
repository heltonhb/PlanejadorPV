"""Componentes de exibição de cartões e resultados."""

def render_campaign_result_card(nome, objetivo, publico, servico, orcamento, canais, datas):
    if not nome:
        nome = f"Campanha: {objetivo}"
    
    budget_str = f"R$ {orcamento:,.2f}" if orcamento > 0 else "Não informado"
    dates_str = datas if datas else "Não informada"
    
    channel_pills = []
    if canais:
        for c in canais:
            c_clean = c.lower()
            if "insta" in c_clean:
                class_name = "channel-instagram"
            elif "face" in c_clean:
                class_name = "channel-facebook"
            elif "email" in c_clean or "e-mail" in c_clean:
                class_name = "channel-email"
            elif "whats" in c_clean:
                class_name = "channel-whatsapp"
            elif "sms" in c_clean:
                class_name = "channel-sms"
            elif "ads" in c_clean:
                class_name = "channel-ads"
            else:
                class_name = "channel-impresso"
            channel_pills.append(f'<span class="channel-pill {class_name}">{c}</span>')
    else:
        channel_pills.append('<span class="channel-pill channel-whatsapp">WhatsApp</span>')
        channel_pills.append('<span class="channel-pill channel-instagram">Instagram</span>')
        channel_pills.append('<span class="channel-pill channel-impresso">Material Impresso</span>')
    
    channels_html = f'<div class="campaign-channel-pills">{"".join(channel_pills)}</div>'
    
    metrics_map = {
        "Atrair novos alunos": "15+ novas matrículas",
        "Reaquecer leads antigos": "50+ contatos retomados",
        "Fidelizar alunos atuais": "95%+ taxa de renovação",
        "Divulgar novo serviço ou curso": "30+ demonstrações agendadas",
        "Promover matrículas (ação sazonal)": "25+ matrículas no período",
        "Gerar indicação de alunos": "20+ indicações de pais"
    }
    expected_metric = metrics_map.get(objetivo, "15+ leads qualificados")
    
    timeline_steps = [
        {"week": "Semana 1", "label": "Planejamento", "desc": "Criação dos criativos e disparos iniciais WhatsApp."},
        {"week": "Semana 2", "label": "Captação", "desc": "Postagem regular, anúncios online e landing page ativa."},
        {"week": "Semana 3", "label": "Vendas", "desc": "Contato telefônico com leads, agendamento de testes."},
        {"week": "Semana 4", "label": "Matrículas", "desc": "Fechamento na unidade Tatuapé e acolhimento dos alunos."}
    ]
    
    steps_html = ""
    for idx, step in enumerate(timeline_steps):
        steps_html += f"""
        <div class="timeline-step">
            <div class="timeline-icon">{idx+1}</div>
            <div class="timeline-label">{step['week']} - {step['label']}</div>
            <div class="timeline-desc">{step['desc']}</div>
        </div>
        """
        
    styles = """
    <style>
        .campaign-result-card {
            background: var(--card-bg) !important;
            border: 1px solid var(--outline-variant) !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            margin-top: 1rem !important;
            margin-bottom: 1.5rem !important;
            box-shadow: var(--shadow-md) !important;
            text-align: left !important;
            color: var(--on-surface) !important;
        }
        .campaign-result-title {
            color: var(--primary) !important;
            font-weight: 800 !important;
            font-size: 1.4rem !important;
            margin-top: 0 !important;
            margin-bottom: 1rem !important;
            text-align: left !important;
        }
        .campaign-meta-grid {
            display: grid !important;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)) !important;
            gap: 1rem !important;
            margin-bottom: 1.5rem !important;
        }
        .campaign-meta-item {
            background: var(--surface-container) !important;
            padding: 0.75rem !important;
            border-radius: 8px !important;
            border: 1px solid var(--outline-variant) !important;
            text-align: left !important;
        }
        .campaign-meta-label {
            font-size: 0.72rem !important;
            color: var(--on-surface-variant) !important;
            text-transform: uppercase !important;
            font-weight: 600 !important;
        }
        .campaign-meta-value {
            font-size: 0.9rem !important;
            font-weight: 700 !important;
            color: var(--text-primary) !important;
            margin-top: 2px !important;
        }
        .campaign-channel-pills {
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 6px !important;
            margin-top: 6px !important;
        }
        .channel-pill {
            font-size: 0.72rem !important;
            font-weight: 700 !important;
            padding: 4px 12px !important;
            border-radius: 20px !important;
            color: white !important;
            display: inline-block !important;
        }
        .channel-instagram { background-color: #E84C3D !important; }
        .channel-facebook { background-color: #005CAA !important; }
        .channel-email { background-color: #F7B731 !important; color: #343A40 !important; }
        .channel-whatsapp { background-color: #00A859 !important; }
        .channel-sms { background-color: #6C757D !important; }
        .channel-ads { background-color: #E09E1A !important; }
        .channel-impresso { background-color: #8E44AD !important; }
        
        .timeline-container {
            margin-top: 1.5rem !important;
            border-top: 1px solid var(--outline-variant) !important;
            padding-top: 1.5rem !important;
            text-align: left !important;
        }
        .timeline-title {
            font-size: 1rem !important;
            font-weight: 700 !important;
            color: var(--primary) !important;
            margin-bottom: 1rem !important;
            text-align: left !important;
        }
        .timeline-steps {
            display: flex !important;
            justify-content: space-between !important;
            position: relative !important;
            margin-bottom: 1rem !important;
            flex-wrap: nowrap !important;
        }
        .timeline-steps::before {
            content: '' !important;
            position: absolute !important;
            top: 20px !important;
            left: 12.5% !important;
            right: 12.5% !important;
            height: 4px !important;
            background: var(--outline-variant) !important;
            z-index: 1 !important;
        }
        .timeline-step {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            width: 25% !important;
            position: relative !important;
            z-index: 2 !important;
        }
        .timeline-icon {
            width: 40px !important;
            height: 40px !important;
            border-radius: 50% !important;
            background: var(--primary) !important;
            border: 3px solid white !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-weight: 800 !important;
            font-size: 0.95rem !important;
            color: white !important;
            box-shadow: var(--shadow-sm) !important;
        }
        .timeline-label {
            font-size: 0.8rem !important;
            font-weight: 700 !important;
            margin-top: 8px !important;
            text-align: center !important;
            color: var(--text-primary) !important;
        }
        .timeline-desc {
            font-size: 0.72rem !important;
            color: var(--on-surface-variant) !important;
            text-align: center !important;
            margin-top: 4px !important;
            max-width: 90% !important;
            line-height: 1.3 !important;
        }
        
        @media (max-width: 640px) {
            .timeline-steps { flex-wrap: wrap !important; gap: 1rem !important; }
            .timeline-steps::before { display: none !important; }
            .timeline-step { width: 100% !important; flex-direction: row !important; align-items: flex-start !important; text-align: left !important; }
            .timeline-label { margin-top: 0 !important; margin-left: 10px !important; text-align: left !important; }
            .timeline-desc { text-align: left !important; margin-top: 2px !important; margin-left: 10px !important; max-width: 100% !important; }
        }
    </style>
    """
    
    card_html = f"""
    {styles}
    <div class="campaign-result-card">
        <div class="campaign-result-title">📢 {nome}</div>
        <div class="campaign-meta-grid">
            <div class="campaign-meta-item">
                <div class="campaign-meta-label">Objetivo Principal</div>
                <div class="campaign-meta-value">{objetivo}</div>
            </div>
            <div class="campaign-meta-item">
                <div class="campaign-meta-label">Público-Alvo</div>
                <div class="campaign-meta-value">{publico}</div>
            </div>
            <div class="campaign-meta-item">
                <div class="campaign-meta-label">Serviço em Foco</div>
                <div class="campaign-meta-value">{servico}</div>
            </div>
            <div class="campaign-meta-item">
                <div class="campaign-meta-label">Orçamento Estimado</div>
                <div class="campaign-meta-value">{budget_str}</div>
            </div>
            <div class="campaign-meta-item">
                <div class="campaign-meta-label">Período Planejado</div>
                <div class="campaign-meta-value">{dates_str}</div>
            </div>
            <div class="campaign-meta-item">
                <div class="campaign-meta-label">Métrica Estimada</div>
                <div class="campaign-meta-value" style="color: var(--primary);">{expected_metric}</div>
            </div>
        </div>
        
        <div style="margin-bottom: 1rem; text-align: left;">
            <div class="campaign-meta-label">Canais de Divulgação</div>
            {channels_html}
        </div>
        
        <div class="timeline-container">
            <div class="timeline-title">📍 Cronograma e Fluxo Visual</div>
            <div class="timeline-steps">
                {steps_html}
            </div>
        </div>
    </div>
    """
    return card_html
