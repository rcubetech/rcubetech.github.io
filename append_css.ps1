$css = @'

/* CONTACT SECTION */
.contact-section {
    padding: var(--section-padding);
    background: radial-gradient(circle at 10% 90%, rgba(37, 99, 235, 0.05) 0%, transparent 50%);
    border-top: 1px solid var(--glass-border);
}

.contact-container {
    max-width: 600px;
    margin: 0 auto;
    background: var(--bg-card);
    border: 1px solid var(--glass-border);
    padding: 3rem;
    border-radius: 20px;
    backdrop-filter: blur(10px);
}

.contact-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    margin-top: 2rem;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.form-group label {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text-main);
}

.form-group input,
.form-group textarea {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--glass-border);
    padding: 12px 16px;
    border-radius: 10px;
    color: var(--text-main);
    font-family: inherit;
    font-size: 1rem;
    transition: all 0.2s;
}

.light-theme .form-group input,
.light-theme .form-group textarea {
    background: rgba(15, 23, 42, 0.03);
}

.form-group input:focus,
.form-group textarea:focus {
    outline: none;
    border-color: var(--primary);
    background: rgba(37, 99, 235, 0.05);
    box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
}

.form-group textarea {
    min-height: 120px;
    resize: vertical;
}

@media (max-width: 768px) {
    .contact-container {
        padding: 2rem 1.5rem;
    }
}
'@
Add-Content -Path "d:\MNY\rcubetech.github.io\style.css" -Value $css
