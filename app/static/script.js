
document.documentElement.classList.add('js'); // for reveal animation

// NAVBAR BLUR EFFECT
window.addEventListener("scroll", () => {
    const navbar = document.querySelector(".navbar");
    if (window.scrollY > 60) {
        navbar.style.background = "rgba(2,6,23,0.88)";
        navbar.style.backdropFilter = "blur(24px)";
        navbar.style.boxShadow = "0 10px 35px rgba(0,0,0,0.35)";
    } else {
        navbar.style.background = "rgba(2,6,23,0.45)";
        navbar.style.boxShadow = "none";
    }
});

// SMOOTH SCROLL
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute("href"));
        if (target) {
            target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    });
});

// FADE-IN REVEAL ANIMATION
const revealElements = document.querySelectorAll(
    ".stat-card, .glass-card, .input-box, .info-card, .timeline-card, .prevention-card, .step-card, .result-container:not(.js-reveal-override)"
);
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("show-element");
        }
    });
}, { threshold: 0.15 });

revealElements.forEach(el => {
    el.classList.add("hidden-element");
    revealObserver.observe(el);
});

// INPUT GLOW EFFECT
const inputs = document.querySelectorAll("input, select");
inputs.forEach(input => {
    input.addEventListener("focus", () => {
        input.parentElement.style.transform = "translateY(-5px)";
        input.parentElement.style.boxShadow = "0 10px 35px rgba(56,189,248,0.18)";
    });
    input.addEventListener("blur", () => {
        input.parentElement.style.transform = "translateY(0px)";
        input.parentElement.style.boxShadow = "none";
    });
});

// BUTTON RIPPLE EFFECT
const buttons = document.querySelectorAll(".predict-btn, .primary-btn");
buttons.forEach(button => {
    button.addEventListener("mouseenter", () => {
        button.style.transform = "translateY(-4px) scale(1.01)";
    });
    button.addEventListener("mouseleave", () => {
        button.style.transform = "translateY(0px) scale(1)";
    });
});

// LIVE BMI COLOR INDICATOR
const bmiInput = document.querySelector('input[name="BMI"]');
if (bmiInput) {
    bmiInput.addEventListener("input", () => {
        const value = parseFloat(bmiInput.value);
        if (!value) return;
        if (value < 18.5) { bmiInput.style.border = "2px solid #facc15"; }
        else if (value >= 18.5 && value <= 24.9) { bmiInput.style.border = "2px solid #22c55e"; }
        else if (value >= 25 && value <= 29.9) { bmiInput.style.border = "2px solid #f97316"; }
        else { bmiInput.style.border = "2px solid #ef4444"; }
    });
}

// PREDICT BUTTON LOADING EFFECT
const form = document.querySelector(".prediction-form");
const predictBtn = document.querySelector(".predict-btn");
if (form && predictBtn) {
    form.addEventListener("submit", () => {
        predictBtn.innerHTML = "Analyzing Risk...";
        predictBtn.style.opacity = "0.85";
        predictBtn.style.pointerEvents = "none";
    });
}
window.addEventListener("pageshow", (e) => {
    if (predictBtn) {
        predictBtn.innerHTML = "Predict Cancer Risk";
        predictBtn.style.opacity = "1";
        predictBtn.style.pointerEvents = "auto";
    }
});

// ACTIVE NAVIGATION HIGHLIGHT
const sections = document.querySelectorAll("section");
const navLinks = document.querySelectorAll(".nav-links a");
window.addEventListener("scroll", () => {
    let current = "";
    sections.forEach(section => {
        const sectionTop = section.offsetTop - 150;
        if (pageYOffset >= sectionTop) { current = section.getAttribute("id"); }
    });
    navLinks.forEach(link => {
        link.classList.remove("active-nav");
        if (link.getAttribute("href") === `#${current}`) { link.classList.add("active-nav"); }
    });
});

// PARALLAX & MOUSE GLOW WITH RAF
const bg = document.querySelector(".background-wrapper img");
const glow = document.createElement("div");
glow.classList.add("mouse-glow");
document.body.appendChild(glow);

let tickingScroll = false;
let tickingMouse = false;
let mouseX = window.innerWidth / 2;
let mouseY = window.innerHeight / 2;
let scrollY = window.pageYOffset;

window.addEventListener("scroll", () => {
    scrollY = window.pageYOffset;
    if (!tickingScroll) {
        window.requestAnimationFrame(() => {
            if (bg) bg.style.transform = `translateY(${scrollY * 0.12}px) scale(1.05)`;
            tickingScroll = false;
        });
        tickingScroll = true;
    }
});

document.addEventListener("mousemove", (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    if (!tickingMouse) {
        window.requestAnimationFrame(() => {
            glow.style.left = mouseX + "px";
            glow.style.top = mouseY + "px";
            tickingMouse = false;
        });
        tickingMouse = true;
    }
});

window.addEventListener("load", () => {
    document.body.classList.add("loaded");
});

console.log("%cOncoVision ML Loaded Successfully", "color:#38bdf8; font-size:18px; font-weight:bold;");
