from flask import Flask, render_template, request, send_file
import pipecalculator

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/download", methods=["POST"])
def pipe_details():
    midinr = str((request.form['midinr']))
    cs = int(request.form['cs'])
    SA = float(request.form['SA'])
    HL = float(request.form['HL'])
    pipe = request.form['pipe']
    TU = float(request.form['TU'])
    SD = float(request.form['SD'])
    M = int(request.form['M'])
    F = float(request.form['F'])
    T = float(request.form['T'])

    try:
        var = list(map(int, midinr.split(',')))
        file_data = pipecalculator.GenerateOpenSCAD(var, cs, SA, HL, pipe, TU, SD, M, F, T)
        return send_file(file_data,
                        as_attachment=True,
                        mimetype="application/zip",
                        attachment_filename="openscadfile.zip")
    except ValueError:  
        error="Input error. Only use (comma separated) integers!"
        return render_template('index.html', error=error)

if __name__ == '__main__':
    app.run()
