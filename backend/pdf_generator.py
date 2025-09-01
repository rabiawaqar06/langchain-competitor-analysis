"""
PDF report generator for competitive analysis.
This module creates professional PDF reports with competitor comparison tables and analysis.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from typing import List, Dict
import datetime
import os


class PDFReportGenerator:
    """
    A class for generating professional PDF reports for competitive analysis.
    
    This class creates comprehensive reports with competitor data, analysis,
    and professional formatting.
    """
    
    def __init__(self):
        """Initialize the PDF generator with default styles."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles for the report."""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2C3E50')
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            spaceBefore=20,
            textColor=colors.HexColor('#34495E')
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            spaceBefore=15,
            textColor=colors.HexColor('#2980B9')
        )
        
        # Body text style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT
        )
    
    def generate_report(self, business_idea: str, location: str, 
                       competitors: List[Dict], analysis: str, 
                       output_path: str) -> str:
        """
        Generate a complete competitive analysis PDF report.
        
        Args:
            business_idea: The user's business idea
            location: The target location for the business
            competitors: List of competitor data dictionaries
            analysis: AI-generated analysis text
            output_path: Path where the PDF should be saved
            
        Returns:
            The path to the generated PDF file
        """
        # Create the PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build the story (content) for the PDF
        story = []
        
        # Add title page
        story.extend(self._create_title_page(business_idea, location))
        
        # Add executive summary
        story.extend(self._create_executive_summary(business_idea, len(competitors)))
        
        # Add major competitors section
        story.extend(self._create_major_competitors_section(competitors))
        
        # Add competitor overview table
        story.extend(self._create_competitor_table(competitors))
        
        # Add AI analysis
        story.extend(self._create_analysis_section(analysis))
        
        # Add recommendations
        story.extend(self._create_recommendations(business_idea, competitors))
        
        # Build the PDF
        doc.build(story)
        
        return output_path
    
    def _create_title_page(self, business_idea: str, location: str) -> List:
        """Create the title page content."""
        elements = []
        
        # Main title
        title = Paragraph("Competitive Analysis Report", self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 30))
        
        # Business idea
        business_para = Paragraph(
            f"<b>Business Idea:</b> {business_idea}", 
            self.subtitle_style
        )
        elements.append(business_para)
        elements.append(Spacer(1, 20))
        
        # Location
        location_para = Paragraph(
            f"<b>Target Location:</b> {location}", 
            self.subtitle_style
        )
        elements.append(location_para)
        elements.append(Spacer(1, 20))
        
        # Date
        date_para = Paragraph(
            f"<b>Report Generated:</b> {datetime.datetime.now().strftime('%B %d, %Y')}", 
            self.body_style
        )
        elements.append(date_para)
        elements.append(Spacer(1, 50))
        
        # Disclaimer
        disclaimer = Paragraph(
            "<i>This report was generated using AI-powered competitive analysis. "
            "Information should be verified and supplemented with additional research.</i>",
            self.body_style
        )
        elements.append(disclaimer)
        
        # Page break
        elements.append(PageBreak())
        
        return elements
    
    def _create_executive_summary(self, business_idea: str, competitor_count: int) -> List:
        """Create the executive summary section."""
        elements = []
        
        # Section header
        header = Paragraph("Executive Summary", self.section_style)
        elements.append(header)
        
        # Summary content with proper competitor count
        summary_text = f"""
        This competitive analysis report examines the competitive landscape for a {business_idea} business. 
        Our research identified <b>{competitor_count} key competitors</b> in the target market. 
        
        The analysis includes detailed competitor profiles, service offerings, pricing strategies, 
        and market positioning for each identified competitor. This information provides valuable 
        insights for strategic planning and competitive positioning.
        
        <b>Key Findings:</b>
        • {competitor_count} major competitors identified and analyzed
        • Comprehensive market assessment completed
        • Strategic recommendations provided
        • Market gaps and opportunities identified
        
        This report serves as a foundation for informed business decision-making and strategic planning.
        """
        
        summary_para = Paragraph(summary_text, self.body_style)
        elements.append(summary_para)
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _create_major_competitors_section(self, competitors: List[Dict]) -> List:
        """Create a bold section highlighting major competitors."""
        elements = []
        
        # Section header
        header = Paragraph("Major Competitors Identified", self.section_style)
        elements.append(header)
        
        if not competitors:
            no_competitors = Paragraph("No specific competitors identified in this analysis.", self.body_style)
            elements.append(no_competitors)
            elements.append(Spacer(1, 20))
            return elements
        
        # Introduction
        intro_text = f"Our analysis identified <b>{len(competitors)} key competitors</b> in your target market. Each represents a significant player that should be carefully studied and monitored:"
        intro_para = Paragraph(intro_text, self.body_style)
        elements.append(intro_para)
        elements.append(Spacer(1, 15))
        
        # List competitors prominently
        for i, competitor in enumerate(competitors, 1):
            name = competitor.get('business_name', f'Competitor {i}')
            location = competitor.get('location', 'Local market')
            
            # Bold competitor name with number
            competitor_text = f"<b>{i}. {name}</b> - Operating in {location}"
            competitor_para = Paragraph(competitor_text, self.body_style)
            elements.append(competitor_para)
            
            # Add brief description if available
            description = competitor.get('description', '')
            if description and description != f'{name} is a business operating in {location}.':
                desc_para = Paragraph(f"   {description}", self.body_style)
                elements.append(desc_para)
            
            elements.append(Spacer(1, 8))
        
        # Call to action
        cta_text = "<i>These competitors should be researched further for detailed market positioning, pricing strategies, and competitive advantages.</i>"
        cta_para = Paragraph(cta_text, self.body_style)
        elements.append(cta_para)
        elements.append(Spacer(1, 25))
        
        return elements
    
    def _create_competitor_table(self, competitors: List[Dict]) -> List:
        """Create a simple table with competitor names and websites."""
        elements = []
        
        # Section header
        header = Paragraph("Competitor Websites for Further Research", self.section_style)
        elements.append(header)
        
        if not competitors:
            no_competitors = Paragraph("No competitors identified for this analysis.", self.body_style)
            elements.append(no_competitors)
            elements.append(Spacer(1, 20))
            return elements
        
        # Introduction text
        intro_text = "Below are the websites of key competitors where you can research their services, pricing, and market positioning:"
        intro_para = Paragraph(intro_text, self.body_style)
        elements.append(intro_para)
        elements.append(Spacer(1, 15))
        
        # Prepare table data - just name and website
        table_data = [['Competitor Name', 'Website']]
        
        for comp in competitors:
            name = comp.get('business_name', 'Unknown')
            website = comp.get('url', 'N/A')
            table_data.append([name, website])
        
        # Create table with wider columns for better readability
        table = Table(table_data, colWidths=[3*inch, 4*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            
            # Body styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')])
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Add research suggestion
        research_text = "<i>Visit these websites to research their services, pricing strategies, customer reviews, and market positioning to inform your competitive strategy.</i>"
        research_para = Paragraph(research_text, self.body_style)
        elements.append(research_para)
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _create_competitor_profiles(self, competitors: List[Dict]) -> List:
        """Create detailed profiles for each competitor."""
        elements = []
        
        # Section header
        header = Paragraph("Detailed Competitor Profiles", self.section_style)
        elements.append(header)
        
        for i, comp in enumerate(competitors, 1):
            # Competitor name
            name = comp.get('business_name', f'Competitor {i}')
            comp_header = Paragraph(f"{i}. {name}", self.subtitle_style)
            elements.append(comp_header)
            
            # Website
            if comp.get('url'):
                website_para = Paragraph(f"<b>Website:</b> {comp['url']}", self.body_style)
                elements.append(website_para)
            
            # Description
            if comp.get('description') and comp['description'] != 'No description available':
                desc_para = Paragraph(f"<b>Description:</b> {comp['description']}", self.body_style)
                elements.append(desc_para)
            
            # Services
            if comp.get('services') and comp['services'] != 'Services not specified':
                services_para = Paragraph(f"<b>Services:</b> {comp['services']}", self.body_style)
                elements.append(services_para)
            
            # Contact Information
            if comp.get('contact_info') and comp['contact_info'] != 'Contact information not available':
                contact_para = Paragraph(f"<b>Contact:</b> {comp['contact_info']}", self.body_style)
                elements.append(contact_para)
            
            # Address
            if comp.get('address') and comp['address'] != 'Address not available':
                address_para = Paragraph(f"<b>Address:</b> {comp['address']}", self.body_style)
                elements.append(address_para)
            
            # Pricing
            if comp.get('pricing_info') and comp['pricing_info'] != 'Pricing information not available':
                pricing_para = Paragraph(f"<b>Pricing:</b> {comp['pricing_info']}", self.body_style)
                elements.append(pricing_para)
            
            # Add space between competitors
            elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_analysis_section(self, analysis: str) -> List:
        """Create the AI analysis section with proper formatting."""
        elements = []
        
        # Section header
        header = Paragraph("AI-Generated Market Analysis", self.section_style)
        elements.append(header)
        
        # Parse and format the analysis text
        formatted_analysis = self._format_analysis_text(analysis)
        
        for formatted_text in formatted_analysis:
            elements.append(formatted_text)
        
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _format_analysis_text(self, analysis: str) -> List:
        """Format analysis text with proper headings and paragraphs."""
        elements = []
        lines = analysis.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                elements.append(Spacer(1, 6))
                continue
            
            # Handle different types of content
            if line.startswith('# '):
                # Main heading
                heading_text = line[2:].strip()
                heading = Paragraph(f"<b>{heading_text}</b>", self.section_style)
                elements.append(heading)
                
            elif line.startswith('## '):
                # Sub heading
                subheading_text = line[3:].strip()
                subheading_style = ParagraphStyle(
                    'SubHeading',
                    parent=self.body_style,
                    fontSize=12,
                    spaceBefore=10,
                    spaceAfter=8,
                    textColor=colors.HexColor('#2980B9')
                )
                subheading = Paragraph(f"<b>{subheading_text}</b>", subheading_style)
                elements.append(subheading)
                
            elif line.startswith('- ') or line.startswith('• '):
                # Bullet point
                bullet_text = line[2:].strip()
                bullet_para = Paragraph(f"• {bullet_text}", self.body_style)
                elements.append(bullet_para)
                
            elif line.startswith('**') and line.endswith('**'):
                # Bold text (remove ** and make bold)
                bold_text = line[2:-2].strip()
                bold_para = Paragraph(f"<b>{bold_text}</b>", self.body_style)
                elements.append(bold_para)
                
            elif '**' in line:
                # Inline bold formatting
                formatted_line = line.replace('**', '')  # Remove markdown formatting
                para = Paragraph(formatted_line, self.body_style)
                elements.append(para)
                
            else:
                # Regular paragraph
                if len(line) > 10:  # Only add substantial content
                    para = Paragraph(line, self.body_style)
                    elements.append(para)
        
        return elements
    
    def _create_recommendations(self, business_idea: str, competitors: List[Dict]) -> List:
        """Create recommendations based on the competitive analysis."""
        elements = []
        
        # Section header
        header = Paragraph("Strategic Recommendations", self.section_style)
        elements.append(header)
        
        # Generate basic recommendations
        recommendations = [
            "Conduct detailed market research to validate demand in your specific target area.",
            "Analyze competitor pricing strategies to position your services competitively.",
            "Identify service gaps in the market that your business could fill.",
            "Develop a unique value proposition that differentiates you from competitors.",
            "Consider digital marketing strategies to compete with established businesses.",
            "Network with local business associations and potential customers.",
            "Monitor competitor activities and market changes regularly."
        ]
        
        # Add recommendations as a bulleted list
        for rec in recommendations:
            rec_para = Paragraph(f"• {rec}", self.body_style)
            elements.append(rec_para)
            elements.append(Spacer(1, 6))
        
        elements.append(Spacer(1, 20))
        
        # Add note about further research
        note = Paragraph(
            "<i>Note: This analysis provides a starting point for competitive research. "
            "Additional primary research, customer interviews, and market validation "
            "are recommended before making final business decisions.</i>",
            self.body_style
        )
        elements.append(note)
        
        return elements


def create_competitive_analysis_report(business_idea: str, location: str,
                                     competitors: List[Dict], analysis: str,
                                     output_dir: str = "reports") -> str:
    """
    Create a competitive analysis PDF report.
    
    Args:
        business_idea: The user's business idea
        location: Target location for the business
        competitors: List of competitor data
        analysis: AI-generated analysis
        output_dir: Directory to save the report
        
    Returns:
        Path to the generated PDF file
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"competitive_analysis_{timestamp}.pdf"
    output_path = os.path.join(output_dir, filename)
    
    # Generate the report
    generator = PDFReportGenerator()
    return generator.generate_report(business_idea, location, competitors, analysis, output_path)
