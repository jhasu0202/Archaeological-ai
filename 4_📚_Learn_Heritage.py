import streamlit as st
from PIL import Image
import io
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Page configuration
st.set_page_config(
    page_title="Learn Heritage - HeritageLens AI",
    page_icon="📚",
    layout="wide"
)

# Apply custom CSS
from utils.ui_utils import apply_custom_css
apply_custom_css()

st.markdown("""
<div class="main-header">
    <h1>📚 Learn About Heritage</h1>
    <p>Discover the cultural significance and characteristics of heritage objects</p>
</div>
""", unsafe_allow_html=True)

# Introduction
st.markdown("""
<div class="info-card">
    <h3>🏛️ Understanding Heritage Through AI</h3>
    <p>HeritageLens AI is designed to recognize and classify different types of cultural heritage and 
    archaeological elements. Each class represents a distinct category of heritage objects with unique 
    characteristics, historical significance, and cultural value. Understanding these classifications 
    helps us appreciate the diversity and richness of our cultural heritage.</p>
</div>
""", unsafe_allow_html=True)

# Heritage classes information
heritage_classes = [
    {
        "id": 0,
        "name": "Stones / Stone Pillars / Stone Structures",
        "icon": "🗿",
        "description": "Ancient stone constructions and architectural elements",
        "characteristics": [
            "Carved or shaped stone blocks",
            "Ancient construction techniques",
            "Weathering and erosion patterns",
            "Geometric or decorative patterns",
            "Structural integrity indicators"
        ],
        "cultural_significance": """
        Stone structures represent some of humanity's earliest and most enduring architectural achievements. 
        From ancient megaliths to intricate temple carvings, these structures tell stories of civilizations 
        that mastered the art of working with stone. They often served as religious centers, defensive 
        structures, or markers of territorial boundaries. The techniques used in their construction, 
        the materials chosen, and their placement in the landscape all provide valuable insights into 
        the technological capabilities and cultural values of past societies.
        """,
        "examples": [
            "Ancient megaliths and standing stones",
            "Temple pillars and columns",
            "Stone walls and fortifications",
            "Carved stone monuments",
            "Ancient stone foundations"
        ],
        "preservation_tips": [
            "Document structural condition regularly",
            "Monitor for erosion and weathering",
            "Protect from vandalism and theft",
            "Maintain proper drainage around structures",
            "Use non-invasive conservation methods"
        ]
    },
    {
        "id": 1,
        "name": "Crops / Farmland",
        "icon": "🌾",
        "description": "Agricultural landscapes and farming areas",
        "characteristics": [
            "Cultivated fields and terraces",
            "Irrigation systems and channels",
            "Agricultural tools and equipment",
            "Seasonal planting patterns",
            "Traditional farming methods"
        ],
        "cultural_significance": """
        Agricultural landscapes represent humanity's relationship with the land and the development of 
        sustainable food production systems. These areas often contain evidence of ancient farming 
        techniques, irrigation systems, and land management practices that sustained civilizations for 
        millennia. Traditional agricultural practices, crop varieties, and farming methods passed down 
        through generations represent intangible cultural heritage that is increasingly at risk in our 
        modern world.
        """,
        "examples": [
            "Ancient terraced fields",
            "Traditional irrigation systems",
            "Historic agricultural tools",
            "Ancient crop storage facilities",
            "Traditional farming villages"
        ],
        "preservation_tips": [
            "Maintain traditional farming practices",
            "Preserve native crop varieties",
            "Document traditional knowledge",
            "Protect agricultural landscapes from development",
            "Support sustainable farming communities"
        ]
    },
    {
        "id": 2,
        "name": "Non-archaeological (deserts, water, mountains, etc.)",
        "icon": "🏔️",
        "description": "Natural landscapes and geographical features",
        "characteristics": [
            "Natural geological formations",
            "Water bodies and hydrological features",
            "Desert landscapes and sand dunes",
            "Mountain ranges and valleys",
            "Natural vegetation patterns"
        ],
        "cultural_significance": """
        While not archaeological in nature, these natural landscapes often serve as the backdrop for 
        human activity and cultural development. They provide context for understanding how ancient 
        civilizations adapted to their environments, chose settlement locations, and developed 
        transportation and trade routes. Natural features often influenced religious beliefs, 
        architectural styles, and cultural practices of the people who lived in these areas.
        """,
        "examples": [
            "Sacred mountains and hills",
            "Ancient trade route landscapes",
            "Natural water sources for settlements",
            "Desert oases and caravan routes",
            "Coastal areas with historical significance"
        ],
        "preservation_tips": [
            "Protect natural landscapes from pollution",
            "Maintain ecological balance",
            "Preserve traditional land use practices",
            "Document cultural associations with natural features",
            "Support sustainable tourism practices"
        ]
    },
    {
        "id": 3,
        "name": "Heritage Sites (temples, palaces, forts, museums)",
        "icon": "🏛️",
        "description": "Major cultural and historical monuments",
        "characteristics": [
            "Architectural complexity and design",
            "Historical and cultural significance",
            "Artistic and decorative elements",
            "Structural engineering achievements",
            "Cultural and religious importance"
        ],
        "cultural_significance": """
        Heritage sites represent the pinnacle of human cultural achievement and serve as tangible 
        connections to our past. These structures often served multiple functions - as centers of 
        worship, seats of power, defensive structures, or repositories of knowledge and art. They 
        reflect the technological capabilities, artistic sensibilities, and cultural values of the 
        societies that created them. Many of these sites continue to serve as active centers of 
        cultural and religious life, making their preservation crucial for maintaining cultural 
        continuity.
        """,
        "examples": [
            "Ancient temples and religious complexes",
            "Royal palaces and administrative buildings",
            "Fortresses and defensive structures",
            "Museums and cultural institutions",
            "Archaeological sites and ruins"
        ],
        "preservation_tips": [
            "Implement comprehensive conservation plans",
            "Monitor structural stability regularly",
            "Control visitor impact and access",
            "Maintain appropriate environmental conditions",
            "Document and preserve associated intangible heritage"
        ]
    }
]

def display_heritage_class(class_info):
    """Display information about a specific heritage class"""
    
    st.markdown(f"## {class_info['icon']} {class_info['name']}")
    
    # Main description
    st.markdown(f"""
    <div class="info-card">
        <h4>📖 Overview</h4>
        <p>{class_info['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different aspects
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Characteristics", "🏛️ Cultural Significance", "📋 Examples", "🛡️ Preservation"])
    
    with tab1:
        st.markdown("### Key Characteristics")
        for characteristic in class_info['characteristics']:
            st.markdown(f"• {characteristic}")
    
    with tab2:
        st.markdown("### Cultural Significance")
        st.markdown(class_info['cultural_significance'])
    
    with tab3:
        st.markdown("### Common Examples")
        for example in class_info['examples']:
            st.markdown(f"• {example}")
    
    with tab4:
        st.markdown("### Preservation Tips")
        for tip in class_info['preservation_tips']:
            st.markdown(f"• {tip}")
    
    st.markdown("---")

def show_additional_educational_content():
    """Show additional educational content and resources"""
    
    st.markdown("## 🎓 Additional Learning Resources")
    
    # AI and Heritage section
    st.markdown("""
    <div class="info-card">
        <h3>🤖 AI in Heritage Preservation</h3>
        <p>Artificial Intelligence is revolutionizing the field of heritage preservation and archaeology. 
        Technologies like HeritageLens AI enable:</p>
        <ul>
            <li><strong>Automated Detection:</strong> Quickly identify heritage objects in large datasets</li>
            <li><strong>Documentation:</strong> Create comprehensive records of archaeological sites</li>
            <li><strong>Monitoring:</strong> Track changes and deterioration over time</li>
            <li><strong>Accessibility:</strong> Make heritage discovery accessible to everyone</li>
            <li><strong>Research:</strong> Support academic and professional research</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Best practices section
    st.markdown("""
    <div class="info-card">
        <h3>📋 Best Practices for Heritage Documentation</h3>
        <p>When using HeritageLens AI or any heritage documentation tool:</p>
        <ol>
            <li><strong>Respect Local Regulations:</strong> Always obtain proper permissions before documenting heritage sites</li>
            <li><strong>Follow Ethical Guidelines:</strong> Respect cultural sensitivities and local communities</li>
            <li><strong>Document Context:</strong> Record not just objects but their environmental and cultural context</li>
            <li><strong>Share Knowledge:</strong> Contribute findings to academic and preservation communities</li>
            <li><strong>Support Conservation:</strong> Use documentation to support preservation efforts</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Technology section
    st.markdown("""
    <div class="info-card">
        <h3>🔬 Understanding the Technology</h3>
        <p>HeritageLens AI uses advanced deep learning technology:</p>
        <ul>
            <li><strong>YOLOv11 Model:</strong> State-of-the-art object detection algorithm</li>
            <li><strong>Custom Training:</strong> Specifically trained on heritage and archaeological data</li>
            <li><strong>Real-time Processing:</strong> Fast analysis of images and videos</li>
            <li><strong>High Accuracy:</strong> Reliable detection of heritage objects</li>
            <li><strong>Continuous Learning:</strong> Model improves with more data</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Call to action
    st.markdown("""
    <div class="info-card">
        <h3>🌟 Get Involved</h3>
        <p>Heritage preservation is a collective responsibility. You can contribute by:</p>
        <ul>
            <li>Using HeritageLens AI to document local heritage sites</li>
            <li>Sharing your discoveries with heritage organizations</li>
            <li>Supporting local preservation efforts</li>
            <li>Educating others about the importance of heritage conservation</li>
            <li>Participating in citizen science projects</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>📚 Knowledge is the foundation of preservation</p>
        <p>Learn, document, and protect our shared heritage</p>
    </div>
    """, unsafe_allow_html=True)

# Main execution code
# Display each heritage class
for class_info in heritage_classes:
    display_heritage_class(class_info)

# Additional educational content
show_additional_educational_content()