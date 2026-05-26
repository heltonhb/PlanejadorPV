"""Componentes de visualização do Instagram (mockup)."""

def parse_instagram_options(markdown_content):
    import re
    header_indices = [m.start() for m in re.finditer(r'##\s*(?:Opção|opcao)\s*\d+', markdown_content, re.IGNORECASE)]
    
    options = []
    if len(header_indices) >= 2:
        for idx in range(len(header_indices)):
            start = header_indices[idx]
            end = header_indices[idx+1] if idx + 1 < len(header_indices) else len(markdown_content)
            options.append(markdown_content[start:end].strip())
    else:
        parts = markdown_content.split('---')
        for p in parts:
            p_clean = p.strip()
            if p_clean:
                options.append(p_clean)
                
    options = [o for o in options if o]
    return options if options else [markdown_content]


def render_instagram_mockup(index, title, content_markdown, img_base64_str):
    lines = content_markdown.strip().split('\n')
    body_lines = []
    hashtags = ""
    
    for line in lines:
        if line.strip().lower().startswith("##"):
            continue
        if "hashtags:" in line.lower() or "#" in line:
            if "#" in line:
                hashtags += " " + line.replace("**Hashtags:**", "").replace("Hashtags:", "").strip()
        else:
            body_lines.append(line)
            
    body_text = "\n".join(body_lines).strip()
    
    if not hashtags:
        import re
        all_tags = re.findall(r'#\w+', content_markdown)
        if all_tags:
            hashtags = " ".join(all_tags)
            for tag in all_tags:
                body_text = body_text.replace(tag, "")
            body_text = body_text.strip()
            
    if not body_text:
        body_text = content_markdown
        
    caption_id = f"insta-caption-{index}"
    btn_id = f"insta-btn-{index}"
    
    if img_base64_str:
        image_html = f'<img src="{img_base64_str}" class="instagram-image" />'
    else:
        image_html = f"""
        <div style="width:100% !important; height:250px !important; background: linear-gradient(135deg, #00A859, #005CAA) !important; display:flex !important; flex-direction:column !important; align-items:center !important; justify-content:center !important; color:white !important; padding: 20px !important; text-align:center !important;">
            <span style="font-size: 3rem !important;">📸</span>
            <span style="font-size: 0.95rem !important; font-weight:700 !important; margin-top:10px !important; color: white !important;">Ensina Mais Turma da Mônica</span>
            <span style="font-size: 0.8rem !important; opacity:0.8 !important; margin-top:4px !important; color: white !important;">Unidade Tatuapé</span>
        </div>
        """
        
    styles = """
    <style>
        .instagram-card {
            background: var(--card-bg) !important;
            border: 1px solid var(--outline-variant) !important;
            border-radius: 12px !important;
            max-width: 470px !important;
            margin: 1.5rem auto !important;
            box-shadow: var(--shadow-md) !important;
            overflow: hidden !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
            color: var(--on-surface) !important;
            text-align: left !important;
        }
        .instagram-header {
            display: flex !important;
            align-items: center !important;
            padding: 12px 16px !important;
            border-bottom: 1px solid var(--outline-variant) !important;
        }
        .instagram-avatar {
            width: 32px !important;
            height: 32px !important;
            border-radius: 50% !important;
            background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%) !important;
            padding: 2px !important;
            margin-right: 10px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        .instagram-avatar-inner {
            width: 100% !important;
            height: 100% !important;
            border-radius: 50% !important;
            background: #00A859 !important;
            color: white !important;
            font-weight: bold !important;
            font-size: 10px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            border: 2px solid white !important;
        }
        .instagram-userinfo {
            display: flex !important;
            flex-direction: column !important;
        }
        .instagram-username {
            font-weight: 600 !important;
            font-size: 13px !important;
            color: var(--on-surface) !important;
            line-height: 1.2 !important;
        }
        .instagram-location {
            font-size: 11px !important;
            color: var(--on-surface-variant) !important;
        }
        .instagram-image-container {
            width: 100% !important;
            max-height: 470px !important;
            overflow: hidden !important;
            background: var(--card-bg) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        .instagram-image {
            width: 100% !important;
            height: auto !important;
            display: block !important;
            object-fit: cover !important;
        }
        .instagram-actions {
            display: flex !important;
            justify-content: space-between !important;
            padding: 12px 16px 8px 16px !important;
            font-size: 1.3rem !important;
            cursor: pointer !important;
        }
        .instagram-actions-left {
            display: flex !important;
            gap: 16px !important;
        }
        .instagram-likes {
            padding: 0 16px 8px 16px !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            color: var(--on-surface) !important;
        }
        .instagram-caption-container {
            padding: 0 16px 16px 16px !important;
            font-size: 13px !important;
            line-height: 1.5 !important;
            color: var(--on-surface) !important;
        }
        .instagram-caption-text {
            word-break: break-word !important;
            white-space: pre-wrap !important;
            color: var(--on-surface) !important;
        }
        .instagram-caption-text strong {
            color: var(--primary) !important;
            margin-right: 6px !important;
        }
        .instagram-hashtags {
            color: var(--secondary) !important;
            margin-top: 8px !important;
            font-weight: 500 !important;
            word-break: break-word !important;
        }
        .instagram-copy-btn {
            display: block !important;
            width: 100% !important;
            margin-top: 14px !important;
            padding: 8px 12px !important;
            background-color: var(--primary) !important;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            text-align: center !important;
            box-shadow: 0px 2px 4px rgba(0, 168, 89, 0.1) !important;
        }
        .instagram-copy-btn:hover {
            background: linear-gradient(135deg, var(--primary-dark), #005a30) !important;
            box-shadow: 0px 4px 8px rgba(0, 168, 89, 0.2) !important;
            transform: translateY(-1px) !important;
        }
    </style>
    """

    script_html = """
    <script>
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('.instagram-copy-btn');
        if (!btn) return;
        var captionId = btn.getAttribute('data-caption-id');
        var btnId = btn.id;
        if (!captionId || !btnId) return;
            const captionEl = document.getElementById(captionId);
            if (!captionEl) return;
            const bodyEl = captionEl.querySelector('.caption-body');
            const tagsEl = captionEl.nextElementSibling;
            
            let textToCopy = '';
            if (bodyEl) {
                textToCopy += bodyEl.innerText.trim();
            } else {
                textToCopy += captionEl.innerText.replace('ensinamais.tatuape', '').trim();
            }
            
            if (tagsEl && tagsEl.classList.contains('instagram-hashtags')) {
                textToCopy += '\\n\\n' + tagsEl.innerText.trim();
            }
            
            function showSuccess(bId) {
                const btn = document.getElementById(bId);
                if (!btn) return;
                const originalText = btn.innerHTML;
                btn.innerHTML = "✅ Copiado!";
                btn.style.backgroundColor = "#00A859";
                btn.style.color = "white";
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.style.backgroundColor = "";
                    btn.style.color = "";
                }, 2000);
            }
            
            function fallbackCopy(text, bId) {
                const textArea = document.createElement("textarea");
                textArea.value = text;
                textArea.style.position = "fixed";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {
                    document.execCommand('copy');
                    showSuccess(bId);
                } catch (err) {
                    console.error('Fallback copy failed', err);
                    alert('Não foi possível copiar a legenda automaticamente.');
                }
                document.body.removeChild(textArea);
            }
            
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    showSuccess(btnId);
                }).catch(err => {
                    fallbackCopy(textToCopy, btnId);
                });
            } else {
                fallbackCopy(textToCopy, btnId);
            }
        });
    </script>
    """
        
    html = f"""
    {styles}
    {script_html}
    <div class="instagram-card">
        <div class="instagram-header">
            <div class="instagram-avatar">
                <div class="instagram-avatar-inner">EM</div>
            </div>
            <div class="instagram-userinfo">
                <span class="instagram-username">ensinamais.tatuape</span>
                <span class="instagram-location">Tatuapé, São Paulo</span>
            </div>
        </div>
        <div class="instagram-image-container">
            {image_html}
        </div>
        <div class="instagram-actions">
            <div class="instagram-actions-left">
                <span>❤️</span>
                <span>💬</span>
                <span>✈️</span>
            </div>
            <div>
                <span>🔖</span>
            </div>
        </div>
        <div class="instagram-likes">
            Curtido por <strong>ensinamais.tatuape</strong> e outras pessoas
        </div>
        <div class="instagram-caption-container">
            <div class="instagram-caption-text" id="{caption_id}"><strong>ensinamais.tatuape</strong> <span class="caption-body">{body_text}</span></div>
            <div class="instagram-hashtags">{hashtags}</div>
            <button class="instagram-copy-btn" id="{btn_id}" data-caption-id="{caption_id}">
                📋 Copiar Legenda
            </button>
        </div>
    </div>
    """
    return html
