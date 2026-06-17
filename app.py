from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime



app = Flask(__name__)
CORS(app)

conn = sqlite3.connect("pucc.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS certificates(
    certificate_no TEXT PRIMARY KEY,
    vehicle_no TEXT,
    fuel TEXT,
    fee REAL,
    date TEXT,
    time TEXT,
    saved_at TEXT,
    validity_upto TEXT,
    actual_charge REAL
)
""")

conn.commit()
conn.close()
print("Database ready!")


@app.route('/save', methods=['POST'])
def save():

    data = request.json
    print("Received data:", data)

    conn = sqlite3.connect("pucc.db")
    cur = conn.cursor()

    try:

        fee = float(data.get('fee', 0))
        validity_upto = data.get('validity_upto', '')

        # Pricing Logic
        actual_charge = 0

        if fee == 60:
            actual_charge = 100

        elif fee == 100:
            actual_charge = 200

        elif fee == 110:
            actual_charge = 200

        elif fee == 150:
            try:
                from_date = datetime.strptime(
                    data['date'], "%d/%m/%Y"
                )

                to_date = datetime.strptime(
                    validity_upto, "%d/%m/%Y"
                )

                days = (to_date - from_date).days

                print("Date:", data['date'])
                print("Validity:", validity_upto)
                print("Days:", days)

                if days >= 300:
                    actual_charge = 250
                else:
                    actual_charge = 200

                print("Charge:", actual_charge)

            except Exception as e:
                print("Validity calculation error:", e)
                actual_charge = 200


        cur.execute("""
        INSERT INTO certificates
        (
            certificate_no,
            vehicle_no,
            fuel,
            fee,
            date,
            time,
            saved_at,
            validity_upto,
            actual_charge
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['certificate_no'],
            data['vehicle_no'],
            data['fuel'],
            fee,
            data['date'],
            data['time'],
            datetime.now().strftime("%Y-%m-%d"),
            validity_upto,
            actual_charge
        ))

        conn.commit()
        print("Saved successfully!")

    except sqlite3.IntegrityError:
        print(f"Duplicate certificate ignored: "f"{data['certificate_no']}")

    except Exception as e:
        print("Error:", e)

    conn.close()

    return jsonify({"success": True})


@app.route('/today')
def today():

    conn = sqlite3.connect("pucc.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*), SUM(actual_charge)
        FROM certificates
        WHERE saved_at = ?
    """, (datetime.now().strftime("%Y-%m-%d"),))

    result = cur.fetchone()

    conn.close()

    return jsonify({
        "vehicles": result[0],
        "total": result[1] or 0
    })

@app.route('/report')
def report():

    selected_date = request.args.get(
        'date',
        datetime.now().strftime("%Y-%m-%d")
    )
    sort = request.args.get('sort', 'rowid')
    order = request.args.get('order', 'DESC')
    next_order = 'ASC' if order == 'DESC' else 'DESC'

    conn = sqlite3.connect("pucc.db")
    cur = conn.cursor()

    allowed_sort = ['rowid', 'fuel', 'time']

    if sort not in allowed_sort:
        sort = 'rowid'

    if order not in ['ASC', 'DESC']:
        order = 'DESC'

    query = f"""
        SELECT certificate_no, vehicle_no,
               fuel, actual_charge, time
        FROM certificates
        WHERE saved_at = ?
        ORDER BY {sort} {order}
    """

    cur.execute(query, (selected_date,))

    rows = cur.fetchall()

    cur.execute("""
        SELECT COUNT(*), SUM(actual_charge)
        FROM certificates
        WHERE saved_at = ?
    """, (selected_date,))

    summary = cur.fetchone()

    conn.close()

    html = f"""
    <html>
    <head>
        <title>PUCC Daily Report</title>

        <style>
            body {{
                font-family: Arial;
                margin: 30px;
            }}

            table {{
                border-collapse: collapse;
                width: 100%;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
            }}

            th {{
                background: #4CAF50;
                color: white;
            }}

            .btn {{
                background: green;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
            }}
        </style>
    </head>

    <body>
    <script>
    setInterval(() => {{
    const selected = document.querySelector(
        'input[name="date"]'
    ).value;

    const today = new Date()
        .toISOString()
        .split('T')[0];

    if (selected === today) {{
        window.location.reload();
    }}
}}, 5000);
    </script>

        <h1>PUCC Report - {selected_date}</h1>

        <form method="GET">
        <input type="date"
        name="date"
        value="{selected_date}">
        <button type="submit">
        View
        </button>
        </form>

        <br>

        <h2>Total Vehicles: {summary[0]}</h2>
        <h2>Total Collection: ₹{summary[1] or 0}</h2>
        <br><br>
 
        <table>
            <tr>
                <th>Vehicle Number</th>
                <th>
                <a href="/report?date={selected_date}&sort=fuel&order={next_order}">
                Fuel ⇅
                </a>
                </th>
                <th>Charge</th>
                <th>
                <a href="/report?date={selected_date}&sort=time&order={next_order}">
                Time ⇅
                </a>
                </th>
                <th>Edit</th>
                <th>Delete</th>
            </tr>
    """

    for row in rows:
        html += f"""
        <tr>
            <td>{row[1]}</td>
            <td>{row[2]}</td>
            <td>₹{row[3]}</td>
            <td>{row[4]}</td>
            <td>
            <button onclick="editCharge('{row[0]}')">
            Edit
            </button>
            </td>
            <td>
            <button onclick="deleteEntry('{row[0]}')">
            Delete
            </button>
            </td>
        </tr>
        """

    html += """
        </table>

<script>

function editCharge(certificate) {

    let amount = prompt("Enter new charge:");

    if (amount == null)
        return;

    fetch("/update_charge", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            certificate_no: certificate,
            amount: amount
        })
    })
    .then(r => r.json())
    .then(() => location.reload());
}

function deleteEntry(certificate) {

    if (!confirm("Delete this entry?"))
        return;

    fetch("/delete_entry", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            certificate_no: certificate
        })
    })
    .then(r => r.json())
    .then(() => location.reload());
}

</script>

    </body>
    </html>
    """

    return html

@app.route('/update_charge', methods=['POST'])
def update_charge():

    data = request.json

    conn = sqlite3.connect("pucc.db")
    cur = conn.cursor()

    cur.execute("""
        UPDATE certificates
        SET actual_charge = ?
        WHERE certificate_no = ?
    """, (
        float(data['amount']),
        data['certificate_no']
    ))

    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route('/delete_entry', methods=['POST'])
def delete_entry():

    data = request.json

    conn = sqlite3.connect("pucc.db")
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM certificates
        WHERE certificate_no = ?
    """, (data['certificate_no'],))

    conn.commit()
    conn.close()

    return jsonify({"success": True})


if __name__ == '__main__':
    app.run(port=5000, threaded=True)