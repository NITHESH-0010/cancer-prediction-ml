// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute("href"));
        if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
});

// Loading state for form
const form = document.getElementById("risk-form");
const submitBtn = document.getElementById("submit-btn");

if (form && submitBtn) {
    form.addEventListener("submit", () => {
        submitBtn.innerHTML = "Calculating...";
        submitBtn.style.opacity = "0.7";
        submitBtn.style.pointerEvents = "none";
    });
}

window.addEventListener("pageshow", () => {
    if (submitBtn) {
        submitBtn.innerHTML = "Calculate Risk Estimate";
        submitBtn.style.opacity = "1";
        submitBtn.style.pointerEvents = "auto";
    }
});

// BMI Color Hint
const bmiInput = document.getElementById('BMI');
if (bmiInput) {
    bmiInput.addEventListener("input", () => {
        const value = parseFloat(bmiInput.value);
        if (!value) {
            bmiInput.style.borderColor = "var(--border)";
            return;
        }
        if (value < 18.5) bmiInput.style.borderColor = "var(--risk-mod)";
        else if (value <= 24.9) bmiInput.style.borderColor = "var(--risk-low)";
        else if (value <= 29.9) bmiInput.style.borderColor = "var(--risk-mod)";
        else bmiInput.style.borderColor = "var(--risk-high)";
    });
}
