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


def generate_css(vars):
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

    body {{
        font-family: var(--brand-font-family);
        font-size: var(--brand-font-size);
        color: var(--brand-text-color);
        background-color: var(--brand-background-color);
        margin: 0;
        padding: 0;
    }}

    header {{
        background-color: var(--brand-primary-color);
        color: white;
        padding: var(--brand-spacing);
    }}

    footer {{
        background-color: var(--brand-secondary-color);
        color: white;
        padding: var(--brand-spacing);
    }}

    nav ul {{
        list-style-type: none;
        padding: 0;
    }}

    nav ul li {{
        display: inline;
        margin-right: var(--brand-spacing);
    }}

    nav ul li a {{
        color: white;
        text-decoration: none;
    }}

    .content-area {{
        padding: var(--brand-spacing);
    }}

    .sidebar {{
        background-color: var(--brand-secondary-color);
        color: white;
        padding: var(--brand-spacing);
    }}

    .hero-section {{
        background-color: var(--brand-primary-color);
        color: white;
        padding: var(--brand-spacing);
        text-align: center;
    }}

    .cta-button {{
        background-color: var(--brand-cta-color);
        color: white;
        padding: 0.5rem 1rem;
        text-decoration: none;
        border-radius: var(--brand-border-radius);
    }}

    .form-group {{
        margin-bottom: var(--brand-spacing);
    }}

    .form-group label {{
        display: block;
        margin-bottom: 0.5rem;
    }}

    .form-group input,
    .form-group textarea {{
        width: 100%;
        padding: 0.5rem;
        border: 1px solid var(--brand-input-border-color);
        border-radius: var(--brand-border-radius);
    }}

    .form-group input:focus,
    .form-group textarea:focus {{
        border-color: var(--brand-input-focus-border-color);
        outline: none;
    }}

    .btn {{
        background-color: var(--brand-button-color);
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: var(--brand-border-radius);
        cursor: pointer;
    }}

    .image-container {{
        text-align: center;
        margin: var(--brand-spacing) 0;
    }}

    .footer-links ul {{
        list-style-type: none;
        padding: 0;
    }}

    .footer-links ul li {{
        margin-bottom: 0.5rem;
    }}

    .footer-links ul li a {{
        color: white;
        text-decoration: none;
    }}

    .social-media-icons a {{
        margin-right: 0.5rem;
    }}

    .cta-block {{
        background-color: var(--brand-cta-color);
        color: white;
        padding: var(--brand-spacing);
        text-align: center;
    }}

    .search-bar {{
        display: flex;
        justify-content: center;
        padding: var(--brand-spacing);
    }}

    .search-bar input {{
        padding: 0.5rem;
        border: 1px solid var(--brand-input-border-color);
        border-radius: var(--brand-border-radius) 0 0 var(--brand-border-radius);
        flex: 1;
    }}

    .search-bar button {{
        padding: 0.5rem;
        border: none;
        background-color: var(--brand-primary-color);
        color: white;
        border-radius: 0 var(--brand-border-radius) var(--brand-border-radius) 0;
        cursor: pointer;
    }}

    .breadcrumbs ul {{
        list-style-type: none;
        padding: 0;
        display: flex;
    }}

    .breadcrumbs ul li {{
        margin-right: 0.5rem;
    }}

    .breadcrumbs ul li a {{
        text-decoration: none;
        color: var(--brand-primary-color);
    }}

    .breadcrumbs ul li::after {{
        content: "/";
        margin-left: 0.5rem;
    }}

    .breadcrumbs ul li:last-child::after {{
        content: "";
    }}
    """


html_structure = """
    # Header Template
    <header>
      <div class="header-content">
        <h1>Site Title</h1>
        <p>Site Tagline</p>
        <!-- Navigation Bar -->
        <nav>
          <ul>
            <!-- Placeholder for menu items -->
          </ul>
        </nav>
      </div>
    </header>
    
    # Footer Template
    <footer>
      <div class="footer-content">
        <p>&copy; 2024 Your Company. All rights reserved.</p>
        <!-- Footer Links -->
        <div class="footer-links">
          <ul>
            <!-- Placeholder for footer links -->
          </ul>
        </div>
        <!-- Social Media Icons -->
        <div class="social-media-icons">
          <a href="#"><img src="icon-facebook.png" alt="Facebook"></a>
          <a href="#"><img src="icon-twitter.png" alt="Twitter"></a>
          <a href="#"><img src="icon-instagram.png" alt="Instagram"></a>
        </div>
      </div>
    </footer>
    
    # Navigation Bar Template
    <nav>
      <ul>
        <!-- Placeholder for navigation items -->
      </ul>
    </nav>
    
    # Content Area Template
    <main>
      <section class="content-area">
        <h2>Content Heading</h2>
        <p>Placeholder text for the content area. More text here to fill the space.</p>
      </section>
    </main>
    
    # Sidebar Template
    <aside class="sidebar">
      <div class="sidebar-content">
        <h3>Sidebar Heading</h3>
        <p>Placeholder text for the sidebar content.</p>
      </div>
    </aside>
    
    # Hero Section Template
    <section class="hero-section">
      <div class="hero-content">
        <h1>Hero Section Heading</h1>
        <p>Subheading or description goes here.</p>
        <a href="#" class="cta-button">Call to Action</a>
      </div>
    </section>
    
    # Form Template
    <form>
      <div class="form-group">
        <label for="name">Name</label>
        <input type="text" id="name" name="name" placeholder="Enter your name">
      </div>
      <div class="form-group">
        <label for="email">Email</label>
        <input type="email" id="email" name="email" placeholder="Enter your email">
      </div>
      <div class="form-group">
        <button type="submit">Submit</button>
      </div>
    </form>
    
    # Button Template
    <button class="btn">Button Text</button>
    
    # Image Template
    <div class="image-container">
      <img src="placeholder-image.jpg" alt="Description of image">
    </div>
    
    # Footer Links Template
    <div class="footer-links">
      <ul>
        <!-- Placeholder for footer links -->
      </ul>
    </div>
    
    # Social Media Icons Template
    <div class="social-media-icons">
      <a href="#"><img src="icon-facebook.png" alt="Facebook"></a>
      <a href="#"><img src="icon-twitter.png" alt="Twitter"></a>
      <a href="#"><img src="icon-instagram.png" alt="Instagram"></a>
    </div>
    
    # Call-to-Action (CTA) Block Template
    <div class="cta-block">
      <h2>CTA Heading</h2>
      <p>CTA description text goes here.</p>
      <a href="#" class="cta-button">Call to Action</a>
    </div>
    
    # Search Bar Template
    <div class="search-bar">
      <input type="text" placeholder="Search...">
      <button type="submit">Search</button>
    </div>
    
    # Breadcrumbs Template
    <nav class="breadcrumbs">
      <ul>
        <!-- Placeholder for breadcrumb items -->
      </ul>
    </nav>
    
    # Contact Form Template
    <form class="contact-form">
      <div class="form-group">
        <label for="name">Name</label>
        <input type="text" id="name" name="name" placeholder="Enter your name">
      </div>
      <div class="form-group">
        <label for="email">Email</label>
        <input type="email" id="email" name="email" placeholder="Enter your email">
      </div>
      <div class="form-group">
        <label for="message">Message</label>
        <textarea id="message" name="message" placeholder="Enter your message"></textarea>
      </div>
      <div class="form-group">
        <button type="submit">Send Message</button>
      </div>
    </form>
"""
