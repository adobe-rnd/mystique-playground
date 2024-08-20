export default {
  "kind": "page",
  "header": {
    "kind": "header",
    "logo": {
      "kind": "image",
      "src": "./empty.png",
      "alt": "Company Logo"
    },
    "navigation": [
      {
        "text": "Home",
        "url": "/home"
      },
      {
        "text": "About",
        "url": "/about"
      },
      {
        "text": "Services",
        "url": "/services"
      },
      {
        "text": "Contact",
        "url": "/contact"
      }
    ],
    "alignment": "center"
  },
  "sections": [
    {
      "kind": "section",
      "children": [
        {
          "kind": "hero",
          "heading": "Welcome to Our Website",
          "subheading": "We provide the best services for you.",
          "image": {
            "kind": "image",
            "src": "./empty.png",
            "alt": "Hero Image",
            "appearance": {
              "position": "center",
              "overlay": false
            }
          },
          "buttons": [
            {
              "kind": "button",
              "text": "Learn More",
              "url": "/learn-more",
              "style": "primary",
              "isPrimary": true,
              "size": "large",
              "alignment": "center"
            }
          ],
          "alignment": "center",
          "layout": "stacked"
        }
      ],
      "spacing": "medium",
      "columns": 1
    },
    {
      "kind": "section",
      "children": [
        {
          "kind": "card",
          "image": {
            "kind": "image",
            "src": "./empty.png",
            "alt": "Card Image"
          },
          "title": "Our Services",
          "description": "We offer a wide range of services to meet your needs.",
          "buttons": [
            {
              "kind": "button",
              "text": "View Services",
              "url": "/services",
              "style": "secondary",
              "isPrimary": false,
              "size": "medium",
              "alignment": "center"
            }
          ],
          "layout": "stacked",
          "alignment": "center"
        },
        {
          "kind": "card",
          "image": {
            "kind": "image",
            "src": "./empty.png",
            "alt": "Card Image"
          },
          "title": "About Us",
          "description": "Learn more about our company and team.",
          "buttons": [
            {
              "kind": "button",
              "text": "Read More",
              "url": "/about",
              "style": "secondary",
              "isPrimary": false,
              "size": "medium",
              "alignment": "center"
            }
          ],
          "layout": "stacked",
          "alignment": "center"
        }
      ],
      "spacing": "large",
      "columns": 2
    }
  ],
  "footer": {
    "kind": "footer",
    "text": "© 2023 Company Name. All rights reserved.",
    "links": [
      {
        "text": "Privacy Policy",
        "url": "/privacy-policy"
      },
      {
        "text": "Terms of Service",
        "url": "/terms-of-service"
      }
    ],
    "layout": "inline",
    "alignment": "center"
  }
}