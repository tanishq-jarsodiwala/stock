import streamlit as st
import requests
import json
import re
from typing import Dict, Any, List

# Hugging Face Configuration i m using this thing because openai api key has some free credits that why
API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"

HUGGINGFACE_API_KEY = "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"
headers = {"Authorization": f"Bearer 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"}

# i have very few amount of time that why i used ai tools to make this dataset ... can use random for making random dataset for temp basis
PRODUCT_DATABASE = {
    "smartphones": {
        "Samsung Galaxy S23": {
            "specs": "6.1\" Dynamic AMOLED, Snapdragon 8 Gen 2, 8GB RAM, 128GB Storage, 50MP Camera",
            "price": "$799",
            "availability": "In Stock",
            "features": ["5G", "Wireless Charging", "Water Resistant", "Face Recognition"],
            "category": "smartphone"
        },
        "iPhone 14": {
            "specs": "6.1\" Super Retina XDR OLED, A15 Bionic, 6GB RAM, 128GB Storage, 12MP Camera",
            "price": "$899",
            "availability": "Limited Stock",
            "features": ["5G", "MagSafe", "Face ID", "iOS 16"],
            "category": "smartphone"
        },
        "OnePlus 11": {
            "specs": "6.7\" AMOLED, Snapdragon 8 Gen 2, 12GB RAM, 256GB Storage, 50MP Camera",
            "price": "$699",
            "availability": "In Stock",
            "features": ["5G", "Fast Charging", "OxygenOS", "Gaming Mode"],
            "category": "smartphone"
        }
    },
    "laptops": {
        "Dell XPS 13": {
            "specs": "13.4\" FHD+ InfinityEdge, Intel i7-1250U, 16GB RAM, 512GB SSD",
            "price": "$1099",
            "availability": "In Stock",
            "features": ["Ultraportable", "Windows 11", "Backlit Keyboard", "Thunderbolt 4"],
            "category": "laptop"
        },
        "MacBook Air M2": {
            "specs": "13.6\" Liquid Retina, Apple M2 Chip, 8GB RAM, 256GB SSD",
            "price": "$1199",
            "availability": "In Stock",
            "features": ["macOS", "Touch ID", "Magic Keyboard", "All-day Battery"],
            "category": "laptop"
        },
        "HP Pavilion 15": {
            "specs": "15.6\" FHD, AMD Ryzen 5, 8GB RAM, 512GB SSD",
            "price": "$649",
            "availability": "In Stock",
            "features": ["Windows 11", "Numeric Keypad", "HD Webcam", "Fast Charge"],
            "category": "laptop"
        }
    },
    "home_appliances": {
        "LG Smart Refrigerator": {
            "specs": "Double Door, 260L Capacity, Smart Inverter Compressor, Wi-Fi Enabled",
            "price": "$899",
            "availability": "In Stock",
            "features": ["Smart Diagnosis", "Energy Efficient", "Multi Air Flow", "Door Cooling+"],
            "category": "home appliance"
        },
        "Samsung Washing Machine": {
            "specs": "Front Load, 8kg Capacity, EcoBubble Technology, Digital Inverter",
            "price": "$549",
            "availability": "In Stock",
            "features": ["Quick Wash", "Steam Wash", "Smart Control", "Self Clean"],
            "category": "home appliance"
        },
        "Sony 55 4K TV": {
            "specs": "55\" 4K Ultra HD, HDR, Android TV, X1 Processor",
            "price": "$799",
            "availability": "Limited Stock",
            "features": ["Google Assistant", "Chromecast", "Dolby Vision", "Game Mode"],
            "category": "home appliance"
        }
    }
}

# main projects start from here
GREETING_MESSAGES = [
    "Welcome to our Electronic Showroom! 🛍️ I'm here to help you find the perfect electronic products.",
    "How can I assist you today? Are you looking for smartphones, laptops, or home appliances?",
    "Feel free to ask me about product specifications, prices, or availability!"
]

PRODUCT_CATEGORIES = ["smartphones", "laptops", "home appliances", "home_appliances"]

# exception handling if user put any wrong data
class ElectronicsSalesAssistant:
    def __init__(self):
        self.context_memory = []
    
    def query_huggingface(self, prompt: str) -> str:
        """Query Hugging Face API with error handling"""
        try:
            # Create a more structured prompt for better responses
            context_prompt = f"""You are a helpful electronics sales assistant. 
            Customer query: {prompt}
            Please provide a helpful, friendly response about electronic products."""
            
            payload = {
                "inputs": context_prompt,
                "parameters": {
                    "max_length": 150,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    # Clean up the response
                    if 'Customer query:' in generated_text:
                        generated_text = generated_text.split('Customer query:')[-1]
                    return generated_text.strip()
                else:
                    return "I'm here to help! Could you please tell me more about what you're looking for?"
            else:
                return "I'm having trouble processing your request right now. How can I help you with our electronic products?"
                
        except Exception as e:
            return "I'm here to assist you with our electronic products. What would you like to know?"
    
    def search_products(self, query: str) -> Dict[str, Any]:
        """Search for products based on user query"""
        query_lower = query.lower()
        found_products = {}
        
        # Search by product name
        for category, products in PRODUCT_DATABASE.items():
            for product_name, details in products.items():
                if any(word in product_name.lower() for word in query_lower.split()):
                    found_products[product_name] = details
        
        # Search by category
        for category in PRODUCT_CATEGORIES:
            if category.replace('_', ' ') in query_lower or category in query_lower:
                if category == "home_appliances":
                    category = "home_appliances"
                found_products.update(PRODUCT_DATABASE.get(category, {}))
        
        # Search by features or specs
        if not found_products:
            for category, products in PRODUCT_DATABASE.items():
                for product_name, details in products.items():
                    specs_text = details['specs'].lower()
                    features_text = ' '.join(details['features']).lower()
                    if any(word in specs_text or word in features_text for word in query_lower.split()):
                        found_products[product_name] = details
        
        return found_products
    
    def format_product_info(self, products: Dict[str, Any]) -> str:
        """Format product information for display"""
        if not products:
            return None
        
        response = "Here are the products I found for you:\n\n"
        
        for product_name, details in products.items():
            response += f"**🔹 {product_name}**\n"
            response += f"**Specifications:** {details['specs']}\n"
            response += f"**Price:** {details['price']}\n"
            response += f"**Availability:** {details['availability']}\n"
            response += f"**Key Features:** {', '.join(details['features'])}\n"
            response += "---\n"
        
        response += "\nWould you like more details about any specific product or have other questions?"
        return response
    
    def handle_common_questions(self, query: str) -> str:
        """Handle common customer questions"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['warranty', 'guarantee']):
            return "All our products come with manufacturer warranty. Smartphones and laptops have 1-year warranty, while home appliances have 2-year warranty. Extended warranty options are available!"
        
        elif any(word in query_lower for word in ['delivery', 'shipping']):
            return "We offer free delivery within the city for orders above $500. Standard delivery takes 2-3 business days. Express delivery (next day) is available for an additional fee."
        
        elif any(word in query_lower for word in ['payment', 'financing']):
            return "We accept all major credit cards, debit cards, and cash. We also offer 0% interest financing options for purchases above $600 with approved credit."
        
        elif any(word in query_lower for word in ['return', 'exchange']):
            return "We have a 30-day return policy for all products in original condition. Exchanges are available within 15 days of purchase."
        
        elif any(word in query_lower for word in ['compare', 'comparison', 'vs', 'versus']):
            return "I'd be happy to help you compare products! Please tell me which specific products you'd like to compare, and I'll provide detailed comparisons."
        
        return None
    
    def process_query(self, user_input: str) -> str:
        """Main function to process user queries"""
        # Check for common questions first
        common_response = self.handle_common_questions(user_input)
        if common_response:
            return common_response
        
        # Search for products
        products = self.search_products(user_input)
        
        if products:
            return self.format_product_info(products)
        else:
            # Use Hugging Face for general conversation
            ai_response = self.query_huggingface(user_input)
            return ai_response


# Streamlit App Configuration
st.set_page_config(
    page_title="Electronic Showroom Assistant made by Tanishq", 
    layout="centered"
)


# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        padding: 20px 0;
    }
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 8px;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<h1 class="main-header">🛍️ Electronic Showroom Sales Assistant</h1>', unsafe_allow_html=True)
st.markdown("**Welcome to our Electronics Store! I'm here to help you find the perfect products.**")

# Initialize the chatbot
if "assistant" not in st.session_state:
    st.session_state.assistant = ElectronicsSalesAssistant()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Welcome to our Electronic Showroom! I'm here to help you find the perfect electronic products. Are you looking for smartphones, laptops, or home appliances today?"}
    ]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What are you looking for today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Let me help you find what you're looking for..."):
            response = st.session_state.assistant.process_query(prompt)
            st.markdown(response)
    
    
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar with additional information
with st.sidebar:
    st.header("🏪 Store Information")
    st.info("""
    **Store Hours:**
    - Monday-Friday: 9 AM - 8 PM
    - Saturday: 10 AM - 6 PM
    - Sunday: 12 PM - 5 PM
    
    **Contact:**
    - Phone: (555) 123-4567
    - Email: info@electronicsstore.com
    """)
    
    st.header("🔍 Quick Categories")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📱 Smartphones"):
            st.session_state.messages.append({"role": "user", "content": "Show me smartphones"})
            st.rerun()
    
    with col2:
        if st.button("💻 Laptops"):
            st.session_state.messages.append({"role": "user", "content": "Show me laptops"})
            st.rerun()
    
    with col3:
        if st.button("🏠 Appliances"):
            st.session_state.messages.append({"role": "user", "content": "Show me home appliances"})
            st.rerun()

# here is basic informtion of my our store
    st.header("💡 Ask me about:")
    st.markdown("""
    - Product specifications
    - Pricing and availability
    - Product comparisons
    - Warranty information
    - Delivery options
    - Payment methods
    - Return policy
    """)

# if user want to clear their chat history 
    if st.button("🔄 Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! Welcome to our Electronic Showroom! 🛍️ How can I help you today?"}
        ]
        st.rerun()

# if user not getting any kind of idea regarding my assitant then this footer shows them how to ask or manage things 
st.markdown("---")
st.markdown("**💡 Tip:** Try asking me specific questions like 'Show me smartphones under $800' or 'Compare iPhone 14 vs Samsung Galaxy S23'")