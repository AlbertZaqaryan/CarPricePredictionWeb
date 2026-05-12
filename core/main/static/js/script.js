(function () {
    const form = document.getElementById("predict-form");
    const submitBtn = form.querySelector("button[type='submit']");
    const resultBox = document.getElementById("result");
    const resultValue = document.getElementById("result-value");
    const errorBox = document.getElementById("error");

    function getCookie(name) {
        const value = "; " + document.cookie;
        const parts = value.split("; " + name + "=");
        if (parts.length === 2) return parts.pop().split(";").shift();
        return "";
    }

    function getCsrfToken() {
        const input = form.querySelector("input[name=csrfmiddlewaretoken]");
        if (input && input.value) return input.value;
        return getCookie("csrftoken");
    }

    function formatMoney(n) {
        return Number(n).toLocaleString("en-US", {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        });
    }

    function animateNumber(el, from, to, duration) {
        const start = performance.now();
        const delta = to - from;

        function frame(now) {
            const t = Math.min(1, (now - start) / duration);
            const eased = 1 - Math.pow(1 - t, 3);
            const current = from + delta * eased;
            el.textContent = formatMoney(current);
            if (t < 1) requestAnimationFrame(frame);
        }
        requestAnimationFrame(frame);
    }

    function showError(msg) {
        errorBox.textContent = msg;
        errorBox.classList.remove("hidden");
        resultBox.classList.add("hidden");
        resultBox.classList.remove("visible");
    }

    function hideError() {
        errorBox.classList.add("hidden");
        errorBox.textContent = "";
    }

    function buildPayload() {
        const data = new FormData(form);
        return {
            model: data.get("model"),
            year: data.get("year"),
            motor_type: data.get("motor_type"),
            motor_volume: data.get("motor_volume"),
            running: data.get("running"),
            running_unit: data.get("running_unit") || "km",
            type: data.get("type"),
            color: data.get("color"),
            status: data.get("status"),
        };
    }

    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        hideError();

        if (!form.reportValidity()) return;

        submitBtn.classList.add("loading");
        submitBtn.disabled = true;

        try {
            const res = await fetch("/predict/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
                body: JSON.stringify(buildPayload()),
            });

            const data = await res.json();

            if (!data.ok) {
                throw new Error(data.error || "Prediction failed.");
            }

            const prev = Number(resultValue.textContent.replace(/[^0-9.-]+/g, "")) || 0;
            resultBox.classList.remove("hidden");
            requestAnimationFrame(() => resultBox.classList.add("visible"));
            animateNumber(resultValue, prev, data.price, 900);
            resultBox.scrollIntoView({ behavior: "smooth", block: "center" });
        } catch (err) {
            showError(err.message || "Something went wrong.");
        } finally {
            submitBtn.classList.remove("loading");
            submitBtn.disabled = false;
        }
    });

    form.addEventListener("reset", function () {
        hideError();
        resultBox.classList.add("hidden");
        resultBox.classList.remove("visible");
        resultValue.textContent = "0";
    });
})();
