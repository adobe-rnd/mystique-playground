css_variables = {
    "brand_primary_color": "#3498db",
    "brand_secondary_color": "#2ecc71",
    "brand_font_family": "Arial, sans-serif",
    "brand_font_size": "16px",
    "brand_spacing": "1rem",
    "brand_border_radius": "5px",
    "brand_button_color": "#e74c3c",
    "brand_input_border_color": "#ccc",
    "brand_input_focus_border_color": "#2980b9",
    "brand_cta_color": "#f39c12",
    "brand_text_color": "#333",
    "brand_background_color": "#f5f5f5"
}

def generate_css_vars(vars):
    return f"""
    :root {{
        --brand-primary-color: {vars['brand_primary_color']};
        --brand-secondary-color: {vars['brand_secondary_color']};
        --brand-font-family: {vars['brand_font_family']};
        --brand-font-size: {vars['brand_font_size']};
        --brand-spacing: {vars['brand_spacing']};
        --brand-border-radius: {vars['brand_border_radius']};
        --brand-button-color: {vars['brand_button_color']};
        --brand-input-border-color: {vars['brand_input_border_color']};
        --brand-input-focus-border-color: {vars['brand_input_focus_border_color']};
        --brand-cta-color: {vars['brand_cta_color']};
        --brand-text-color: {vars['brand_text_color']};
        --brand-background-color: {vars['brand_background_color']};
    }}
    """
