css_variables = {
    "brand_primary_color": "#3498db",
    "brand_secondary_color": "#2ecc71",
    "brand_accent_color_1": "#b35732",
    "brand_accent_color_2": "#231c18",
    "brand_accent_color_3": "#ec9f23",
    "brand_background_color": "#f5f5f5",
    "brand_neutral_background": "#f6f5f4",
    "brand_soft_background": "#c8b6a6",
    "brand_dark_accent": "#5e473b",
    "brand_button_color": "#e74c3c",
    "brand_cta_color": "#f39c12",
    "brand_input_border_color": "#ccc",
    "brand_input_focus_border_color": "#2980b9",
    "brand_text_color": "#333",
    "brand_heading_color": "#222",
    "brand_muted_text_color": "#777",
    "brand_error_color": "#e74c3c",
    "brand_success_color": "#2ecc71",
    "brand_warning_color": "#f39c12",
    "brand_font_family": "Arial, sans-serif",
    "brand_heading_font_family": "Arial Black, sans-serif",
    "brand_font_size": "16px",
    "brand_heading_font_size": "32px",
    "brand_small_font_size": "12px",
    "brand_large_font_size": "24px",
    "brand_line_height": "1.5",
    "brand_letter_spacing": "0.02em",
    "brand_heading_letter_spacing": "0.05em",
    "brand_paragraph_margin": "1rem 0",
    "brand_spacing_small": "0.5rem",
    "brand_spacing_medium": "1rem",
    "brand_spacing_large": "2rem",
    "brand_padding_small": "0.5rem",
    "brand_padding_medium": "1rem",
    "brand_padding_large": "2rem",
    "brand_margin_small": "0.5rem",
    "brand_margin_medium": "1rem",
    "brand_margin_large": "2rem",
    "brand_border_radius": "5px",
    "brand_border_radius_small": "3px",
    "brand_border_radius_large": "10px",
    "brand_border_color": "#ccc",
    "brand_border_thickness": "1px",
    "brand_border_style": "solid",
    "brand_box_shadow_small": "0 1px 3px rgba(0, 0, 0, 0.1)",
    "brand_box_shadow_medium": "0 3px 6px rgba(0, 0, 0, 0.15)",
    "brand_box_shadow_large": "0 10px 20px rgba(0, 0, 0, 0.2)",
    "brand_button_padding": "0.75rem 1.5rem",
    "brand_button_font_weight": "bold",
    "brand_button_border_radius": "5px",
    "brand_button_hover_color": "#e67e22",
    "brand_button_active_color": "#d35400",
    "brand_input_padding": "0.5rem",
    "brand_input_border_radius": "5px",
    "brand_input_background_color": "#fff",
    "brand_input_text_color": "#333",
    "brand_input_placeholder_color": "#aaa",
    "brand_link_color": "#3498db",
    "brand_link_hover_color": "#2980b9",
    "brand_link_visited_color": "#9b59b6",
}

def generate_css_vars(vars):
    return f"""
    :root {{
        --brand-primary-color: {vars['brand_primary_color']};
        --brand-secondary-color: {vars['brand_secondary_color']};
        --brand-accent-color-1: {vars['brand_accent_color_1']};
        --brand-accent-color-2: {vars['brand_accent_color_2']};
        --brand-accent-color-3: {vars['brand_accent_color_3']};
        --brand-background-color: {vars['brand_background_color']};
        --brand-neutral-background: {vars['brand_neutral_background']};
        --brand-soft-background: {vars['brand_soft_background']};
        --brand-dark-accent: {vars['brand_dark_accent']};
        --brand-button-color: {vars['brand_button_color']};
        --brand-cta-color: {vars['brand_cta_color']};
        --brand-input-border-color: {vars['brand_input_border_color']};
        --brand-input-focus-border-color: {vars['brand_input_focus_border_color']};
        --brand-text-color: {vars['brand_text_color']};
        --brand-heading-color: {vars['brand_heading_color']};
        --brand-muted-text-color: {vars['brand_muted_text_color']};
        --brand-error-color: {vars['brand_error_color']};
        --brand-success-color: {vars['brand_success_color']};
        --brand-warning-color: {vars['brand_warning_color']};
        --brand-font-family: {vars['brand_font_family']};
        --brand-heading-font-family: {vars['brand_heading_font_family']};
        --brand-font-size: {vars['brand_font_size']};
        --brand-heading-font-size: {vars['brand_heading_font_size']};
        --brand-small-font-size: {vars['brand_small_font_size']};
        --brand-large-font-size: {vars['brand_large_font_size']};
        --brand-line-height: {vars['brand_line_height']};
        --brand-letter-spacing: {vars['brand_letter_spacing']};
        --brand-heading-letter-spacing: {vars['brand_heading_letter_spacing']};
        --brand-paragraph-margin: {vars['brand_paragraph_margin']};
        --brand-spacing-small: {vars['brand_spacing_small']};
        --brand-spacing-medium: {vars['brand_spacing_medium']};
        --brand-spacing-large: {vars['brand_spacing_large']};
        --brand-padding-small: {vars['brand_padding_small']};
        --brand-padding-medium: {vars['brand_padding_medium']};
        --brand-padding-large: {vars['brand_padding_large']};
        --brand-margin-small: {vars['brand_margin_small']};
        --brand-margin-medium: {vars['brand_margin_medium']};
        --brand-margin-large: {vars['brand_margin_large']};
        --brand-border-radius: {vars['brand_border_radius']};
        --brand-border-radius-small: {vars['brand_border_radius_small']};
        --brand-border-radius-large: {vars['brand_border_radius_large']};
        --brand-border-color: {vars['brand_border_color']};
        --brand-border-thickness: {vars['brand_border_thickness']};
        --brand-border-style: {vars['brand_border_style']};
        --brand-box-shadow-small: {vars['brand_box_shadow_small']};
        --brand-box-shadow-medium: {vars['brand_box_shadow_medium']};
        --brand-box-shadow-large: {vars['brand_box_shadow_large']};
        --brand-button-padding: {vars['brand_button_padding']};
        --brand-button-font-weight: {vars['brand_button_font_weight']};
        --brand-button-border-radius: {vars['brand_button_border_radius']};
        --brand-button-hover-color: {vars['brand_button_hover_color']};
        --brand-button-active-color: {vars['brand_button_active_color']};
        --brand-input-padding: {vars['brand_input_padding']};
        --brand-input-border-radius: {vars['brand_input_border_radius']};
        --brand-input-background-color: {vars['brand_input_background_color']};
        --brand-input-text-color: {vars['brand_input_text_color']};
        --brand-input-placeholder-color: {vars['brand_input_placeholder_color']};
        --brand-link-color: {vars['brand_link_color']};
        --brand-link-hover-color: {vars['brand_link_hover_color']};
        --brand-link-visited-color: {vars['brand_link_visited_color']};
    }}
    """
