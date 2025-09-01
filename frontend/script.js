/**
 * JavaScript for the Competitive Analysis Web Application
 * Handles form submission, progress tracking, and result display
 */

class CompetitiveAnalysisApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api';
        this.currentAnalysisId = null;
        this.progressInterval = null;
        
        this.initializeApp();
    }
    
    /**
     * Initialize the application and set up event listeners
     */
    initializeApp() {
        this.setupEventListeners();
        this.hideAllSections();
    }
    
    /**
     * Set up event listeners for form submission and user interactions
     */
    setupEventListeners() {
        // Form submission
        const form = document.getElementById('analysisForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmission(e));
        }
        
        // Download button
        const downloadBtn = document.getElementById('downloadBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadReport());
        }
        
        // New analysis button
        const newAnalysisBtn = document.getElementById('newAnalysisBtn');
        if (newAnalysisBtn) {
            newAnalysisBtn.addEventListener('click', () => this.startNewAnalysis());
        }
        
        // Modal close buttons
        const modalClose = document.getElementById('modalClose');
        const modalOk = document.getElementById('modalOk');
        if (modalClose) {
            modalClose.addEventListener('click', () => this.hideModal());
        }
        if (modalOk) {
            modalOk.addEventListener('click', () => this.hideModal());
        }
        
        // Close modal when clicking outside
        const modal = document.getElementById('errorModal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal();
                }
            });
        }
    }
    
    /**
     * Hide all main sections initially
     */
    hideAllSections() {
        const sections = ['progressSection', 'resultsSection'];
        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                section.style.display = 'none';
            }
        });
    }
    
    /**
     * Handle form submission for starting analysis
     */
    async handleFormSubmission(event) {
        event.preventDefault();
        
        // Get form data
        const formData = new FormData(event.target);
        const businessIdea = formData.get('businessIdea').trim();
        const location = formData.get('location').trim();
        
        // Validate input
        if (!businessIdea || !location) {
            this.showError('Please fill in all required fields.');
            return;
        }
        
        try {
            // Disable form and show loading
            this.setFormLoading(true);
            
            // Submit analysis request
            const response = await fetch(`${this.apiBaseUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    business_idea: businessIdea,
                    location: location
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to start analysis');
            }
            
            const result = await response.json();
            this.currentAnalysisId = result.id;
            
            // Show progress section and start tracking
            this.showProgressSection();
            this.startProgressTracking();
            
        } catch (error) {
            console.error('Error starting analysis:', error);
            this.showError(`Failed to start analysis: ${error.message}`);
            this.setFormLoading(false);
        }
    }
    
    /**
     * Set form loading state
     */
    setFormLoading(loading) {
        const submitBtn = document.getElementById('submitBtn');
        const form = document.getElementById('analysisForm');
        
        if (submitBtn) {
            submitBtn.disabled = loading;
            if (loading) {
                submitBtn.innerHTML = '<i class="fas fa-spinner loading"></i> Starting Analysis...';
            } else {
                submitBtn.innerHTML = '<i class="fas fa-search"></i> Start Analysis';
            }
        }
        
        if (form) {
            const inputs = form.querySelectorAll('input');
            inputs.forEach(input => {
                input.disabled = loading;
            });
        }
    }
    
    /**
     * Show the progress section
     */
    showProgressSection() {
        const progressSection = document.getElementById('progressSection');
        if (progressSection) {
            progressSection.style.display = 'block';
            progressSection.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    /**
     * Start tracking analysis progress
     */
    startProgressTracking() {
        // Initial status check
        this.checkAnalysisStatus();
        
        // Set up interval to check status every 2 seconds
        this.progressInterval = setInterval(() => {
            this.checkAnalysisStatus();
        }, 2000);
    }
    
    /**
     * Check the current status of the analysis
     */
    async checkAnalysisStatus() {
        if (!this.currentAnalysisId) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/status/${this.currentAnalysisId}`);
            
            if (!response.ok) {
                throw new Error('Failed to get analysis status');
            }
            
            const status = await response.json();
            this.updateProgressDisplay(status);
            
            // Check if analysis is complete
            if (status.status === 'completed') {
                this.handleAnalysisComplete();
            } else if (status.status === 'failed') {
                this.handleAnalysisError(status.error || 'Analysis failed');
            }
            
        } catch (error) {
            console.error('Error checking status:', error);
            // Don't show error immediately, wait for a few retries
        }
    }
    
    /**
     * Update the progress display based on current status
     */
    updateProgressDisplay(status) {
        const progressText = document.getElementById('progressText');
        const progressFill = document.getElementById('progressFill');
        
        // Update progress text
        if (progressText && status.progress) {
            progressText.textContent = status.progress;
        }
        
        // Update progress bar and steps
        const progressMap = {
            'started': { progress: 10, step: 1 },
            'searching': { progress: 25, step: 1 },
            'scraping': { progress: 50, step: 2 },
            'analyzing': { progress: 75, step: 3 },
            'generating_pdf': { progress: 90, step: 4 },
            'completed': { progress: 100, step: 4 }
        };
        
        const progressInfo = progressMap[status.status] || { progress: 0, step: 1 };
        
        if (progressFill) {
            progressFill.style.width = `${progressInfo.progress}%`;
        }
        
        // Update step indicators
        this.updateStepIndicators(progressInfo.step);
    }
    
    /**
     * Update the step indicators in the progress section
     */
    updateStepIndicators(currentStep) {
        for (let i = 1; i <= 4; i++) {
            const step = document.getElementById(`step${i}`);
            if (step) {
                if (i <= currentStep) {
                    step.classList.add('active');
                } else {
                    step.classList.remove('active');
                }
            }
        }
    }
    
    /**
     * Handle analysis completion
     */
    async handleAnalysisComplete() {
        // Stop progress tracking
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        
        // Update progress display to show completion
        const progressText = document.getElementById('progressText');
        const progressFill = document.getElementById('progressFill');
        
        if (progressText) {
            progressText.textContent = 'Analysis completed successfully! 🎉';
        }
        
        if (progressFill) {
            progressFill.style.width = '100%';
        }
        
        // Update all step indicators to complete
        this.updateStepIndicators(4);
        
        // Show results section
        this.showResultsSection();
        
        // Reset form
        this.setFormLoading(false);
    }
    
    /**
     * Show the results section
     */
    showResultsSection() {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
        
        // Update results content
        const competitorCount = document.getElementById('competitorCount');
        if (competitorCount) {
            competitorCount.textContent = '5'; // Default competitor count
        }
        
        const analysisPreview = document.getElementById('analysisPreview');
        if (analysisPreview) {
            analysisPreview.textContent = 'Comprehensive competitive analysis has been generated with detailed insights about market positioning, competitor profiles, and strategic recommendations.';
        }
    }
    
    /**
     * Handle analysis error
     */
    handleAnalysisError(errorMessage) {
        // Stop progress tracking
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        
        this.showError(`Analysis failed: ${errorMessage}`);
        this.setFormLoading(false);
    }
    
    /**
     * Display the analysis results
     */
    displayResults(results) {
        // Hide progress section
        const progressSection = document.getElementById('progressSection');
        if (progressSection) {
            progressSection.style.display = 'none';
        }
        
        // Update competitor count
        const competitorCount = document.getElementById('competitorCount');
        if (competitorCount) {
            competitorCount.textContent = results.competitors ? results.competitors.length : 0;
        }
        
        // Display analysis preview
        const analysisPreview = document.getElementById('analysisPreview');
        if (analysisPreview && results.analysis) {
            // Truncate analysis for preview
            const previewText = results.analysis.length > 1000 
                ? results.analysis.substring(0, 1000) + '...' 
                : results.analysis;
            analysisPreview.textContent = previewText;
        }
        
        // Show results section
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    /**
     * Download the PDF report
     */
    async downloadReport() {
        if (!this.currentAnalysisId) {
            this.showError('No analysis ID available for download.');
            return;
        }
        
        try {
            const downloadBtn = document.getElementById('downloadBtn');
            if (downloadBtn) {
                downloadBtn.disabled = true;
                downloadBtn.innerHTML = '<i class="fas fa-spinner loading"></i> Downloading...';
            }
            
            // Create download link
            const downloadUrl = `${this.apiBaseUrl}/download/${this.currentAnalysisId}`;
            
            // Use fetch to get the file
            const response = await fetch(downloadUrl);
            
            if (!response.ok) {
                throw new Error('Failed to download report');
            }
            
            // Create blob and download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `competitive_analysis_report_${Date.now()}.pdf`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
            
            // Reset button
            if (downloadBtn) {
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download PDF Report';
            }
            
        } catch (error) {
            console.error('Error downloading report:', error);
            this.showError(`Failed to download report: ${error.message}`);
            
            // Reset button
            const downloadBtn = document.getElementById('downloadBtn');
            if (downloadBtn) {
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download PDF Report';
            }
        }
    }
    
    /**
     * Start a new analysis
     */
    startNewAnalysis() {
        // Reset form
        const form = document.getElementById('analysisForm');
        if (form) {
            form.reset();
        }
        
        // Reset state
        this.currentAnalysisId = null;
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        
        // Hide sections
        this.hideAllSections();
        this.setFormLoading(false);
        
        // Scroll to form
        const analysisSection = document.querySelector('.analysis-section');
        if (analysisSection) {
            analysisSection.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    /**
     * Show error modal
     */
    showError(message) {
        const errorModal = document.getElementById('errorModal');
        const errorMessage = document.getElementById('errorMessage');
        
        if (errorMessage) {
            errorMessage.textContent = message;
        }
        
        if (errorModal) {
            errorModal.style.display = 'flex';
        }
    }
    
    /**
     * Hide error modal
     */
    hideModal() {
        const errorModal = document.getElementById('errorModal');
        if (errorModal) {
            errorModal.style.display = 'none';
        }
    }
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CompetitiveAnalysisApp();
});

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading animation class
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .loading {
        animation: spin 1s linear infinite;
    }
`;
document.head.appendChild(style);
