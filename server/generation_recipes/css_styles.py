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

css_styles = """
    body {
        font-family: var(--brand-font-family);
        font-size: var(--brand-font-size);
        color: var(--brand-text-color);
        background-color: var(--brand-background-color);
        padding: 0;
        line-height: 1.6;
        width: 70%;
        margin: 0 auto;
    }

    header {
        background-color: var(--brand-primary-color);
        color: #fff;
        padding: var(--brand-spacing);
        text-align: center;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }

    footer {
        background-color: var(--brand-secondary-color);
        color: #fff;
        padding: var(--brand-spacing);
        text-align: center;
        font-size: 0.875rem;
    }

    nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        justify-content: center;
        background-color: var(--brand-primary-color);
    }

    nav ul {
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        justify-content: center;
        gap: var(--brand-spacing);
    }

    nav ul li a {
        color: #fff;
        text-decoration: none;
        padding: 0.5rem 1rem;
        border-radius: var(--brand-border-radius);
        transition: background-color 0.3s ease;
    }

    nav ul li a:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }

    .hero-section {
        background-color: var(--brand-primary-color);
        color: #fff;
        padding: 2rem var(--brand-spacing);
        text-align: center;
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
    }

    .hero-section img {
      margin: 10px;
      border: 1px solid white;
      width: 40%;        
    }

    .cta-button {
        background-color: var(--brand-cta-color);
        color: #fff;
        padding: 0.75rem 1.5rem;
        text-decoration: none;
        border-radius: var(--brand-border-radius);
        font-weight: bold;
        transition: background-color 0.3s ease;
    }

    .cta-button:hover {
        background-color: darken(var(--brand-cta-color), 10%);
    }

    .form-group {
        margin-bottom: 1.5rem;
    }

    .form-group label {
        font-weight: bold;
        margin-bottom: 0.5rem;
        display: block;
    }

    .form-group input,
    .form-group textarea {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid var(--brand-input-border-color);
        border-radius: var(--brand-border-radius);
        font-family: var(--brand-font-family);
        font-size: var(--brand-font-size);
    }

    .form-group input:focus,
    .form-group textarea:focus {
        border-color: var(--brand-input-focus-border-color);
        box-shadow: 0 0 5px rgba(41, 128, 185, 0.3);
        outline: none;
    }

    .btn {
        background-color: var(--brand-button-color);
        color: #fff;
        padding: 0.75rem 1.5rem;
        border: none;
        border-radius: var(--brand-border-radius);
        cursor: pointer;
        font-weight: bold;
        transition: background-color 0.3s ease;
    }

    .btn:hover {
        background-color: darken(var(--brand-button-color), 10%);
    }

    .image-container {
        text-align: center;
        margin: var(--brand-spacing) 0;
    }

    .footer-links ul {
        list-style-type: none;
        padding: 0;
        margin: 0;
        display: flex;
        justify-content: center;
        gap: var(--brand-spacing);
    }

    .footer-links ul li a {
        color: #fff;
        text-decoration: none;
    }

    .social-media-icons a {
        margin-right: 0.75rem;
    }

    .footer-links img {
        width: 30px;
        height: 30px;
    }

    .cta-block {
        background-color: var(--brand-cta-color);
        color: #fff;
        padding: 2rem var(--brand-spacing);
        text-align: center;
        border-radius: var(--brand-border-radius);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }

    .search-bar {
        display: flex;
        padding: var(--brand-spacing);
        max-width: 600px;
        margin: 0 auto;
        gap: 0.5rem;
    }

    .search-bar input {
        flex: 1;
        padding: 0.75rem;
        border: 1px solid var(--brand-input-border-color);
        border-radius: var(--brand-border-radius) 0 0 var(--brand-border-radius);
    }

    .search-bar button {
        padding: 0.75rem 1.5rem;
        background-color: var(--brand-primary-color);
        color: #fff;
        border: none;
        border-radius: 0 var(--brand-border-radius) var(--brand-border-radius) 0;
        cursor: pointer;
    }

    .breadcrumbs ul {
        list-style: none;
        padding: 0;
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }

    .breadcrumbs ul li {
        font-size: 0.875rem;
    }

    .breadcrumbs ul li a {
        color: var(--brand-primary-color);
        text-decoration: none;
    }

    .breadcrumbs ul li::after {
        content: "/";
        margin-left: 0.5rem;
        color: var(--brand-text-color);
    }

    .breadcrumbs ul li:last-child::after {
        content: "";
    }
    
    .card-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: var(--brand-spacing);
    }   
    
    .card {
        background-color: #fff;
        padding: var(--brand-spacing);
        border-radius: var(--brand-border-radius);
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    .card img {
        width: 100%;
        border: 1px solid #f5f5f5;
        border-radius: var(--brand-border-radius);
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    .card h2 {
        margin-top: 0;
    }
    
    .card p {
        margin-bottom: 0;
    }
    
    .card .cta-button {
        margin-top: var(--brand-spacing);
    }
    """
