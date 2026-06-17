setTimeout(() => {

    const text = document.body.innerText;

    function extract(pattern) {
        const match = text.match(pattern);
        return match ? match[1].trim() : "";
    }

    const data = {
        certificate_no: extract(/Certificate SL\. No\.?\s*:?\s*([A-Z0-9]+)/i),

        vehicle_no: extract(/Registration No\.?\s*:?\s*([A-Z0-9]+)/i),

        fuel: extract(/Fuel\s*:?\s*([A-Z]+)/i),

        fee: parseFloat(
            extract(/Fees\s*:?\s*Rs\.?([0-9.]+)/i)
        ),

        date: extract(/Date\s*:?\s*([0-9\/]+)/i),

        time: extract(/Time\s*:?\s*([0-9: AMP]+)/i),

        validity_upto: extract(
            /Validity upto[\s\S]*?([0-9]{2}\/[0-9]{2}\/[0-9]{4})/i
        )
    };

    console.log("PUCC Data:", data);

    if (data.certificate_no !== "") {

        fetch("http://127.0.0.1:5000/save", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(r => r.json())
        .then(console.log)
        .catch(console.error);
    }

}, 1500);