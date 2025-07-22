import simplejson as json

from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector


app = Flask(__name__)
app.secret_key = '123'

teste_id = 1
user_id = 0
#currentQuestion=""
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user=" ",
        password=" ",
        database="bancopp2",
        buffered=True  # <- não retirar
    )


@app.route('/areas')
def areas():
    db = get_db_connection()  # criando teste
    cursor = db.cursor()
    global user_id
    cursor.execute(f"SELECT AVG(alternativa.pesoExatas),AVG(alternativa.pesoHumanas), AVG(alternativa.pesoSaude) FROM teste JOIN teste_has_alternativa ON teste_has_alternativa.teste_id = teste.id JOIN alternativa ON alternativa.id = teste_has_alternativa.alternativa_id WHERE teste.usuario_id = {user_id} GROUP BY teste.id ORDER BY teste.id DESC")
    print("user_id = " + str(user_id))
    return render_template('areas.html', chart_data = json.dumps(cursor.fetchone(), use_decimal = True))



@app.route('/saude')
def saude():
    return render_template('saude.html')

@app.route('/exatas')
def exatas():
    return render_template('exatas.html')

@app.route('/humanas')
def humanas():
    return render_template('humanas.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/teste')
def test():
    questions = [
        {
            'id': 1,
            'pegunta': 'Como você costuma reagir diante de uma discussão?',
            'idResposta1': 1,
            'resposta1': 'Busca ouvir todos e/ou acalmar os ânimos. ',
            'idResposta2': 2,
            'resposta2': 'Gosta de argumentar e defender sua visão com fatos. ',
            'idResposta3': 3,
            'resposta3': 'Prefere resolver com objetividade, sem rodeios. ',

        },
        {
            'id': 1,
            'pegunta': 'Como você costuma reagir diante de uma discussão?',
            'idResposta1': 1,
            'resposta1': 'Busca ouvir todos e/ou acalmar os ânimos. ',
            'idResposta2': 2,
            'resposta2': 'Gosta de argumentar e defender sua visão com fatos. ',
            'idResposta3': 3,
            'resposta3': 'Prefere resolver com objetividade, sem rodeios. ',

        }

    ]


    db = get_db_connection()  # criando teste
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM pegunta")
    currentQuestion = "["
    for linhaPergunta in cursor.fetchall():
        if currentQuestion != "[":
            currentQuestion += ","
        currentQuestion += "{\"id\": "+str(linhaPergunta[0])+",\"pegunta\": \""+linhaPergunta[1]+"\""
        cursor.execute(f"SELECT * FROM alternativa WHERE pegunta_id={linhaPergunta[0]}")
        alternativaRow = 0
        for linhaAlternativa in cursor.fetchall():
            alternativaRow+=1
            currentQuestion += (",\"idResposta" + str(alternativaRow) + "\": " + str(linhaAlternativa[0])
                                + ",\"resposta" + str(alternativaRow) + "\": \"" + linhaAlternativa[2] + "\"")
            print(linhaAlternativa)
        currentQuestion += "}"

    currentQuestion += "]"
    return render_template('teste.html', html_questions = json.loads(currentQuestion))


@app.route('/responder', methods=['POST'])
def responder():
    db = get_db_connection() #criando teste
    cursor = db.cursor()
    #cursor.execute("INSERT INTO teste (usuario_id) VALUES (%d)", (1))
    global user_id
    cursor.execute(
        f"INSERT INTO teste (usuario_id) VALUES ('{user_id}');")
    db.commit()
    global teste_id
    teste_id = cursor.lastrowid
    cursor.close()
    db.close()
    for key, value in request.form.items():
        if key.startswith('question_'):
            print(teste_id)
            question_id = key.split('_')[1]
            print(f"Recebido = {value}")  # <-- aqui
            db = get_db_connection() #salva as alternativas
            cursor = db.cursor()
            #cursor.execute("INSERT INTO teste_has_alternativa (teste_id, alternativa_id ) VALUES (%d, %d)", (teste_id, value))
            cursor.execute(
                f"INSERT INTO teste_has_alternativa (teste_id, alternativa_id ) VALUES ('{teste_id}', '{value}');")
            db.commit()
            cursor.close()
            db.close()
    resultado()
    return redirect(url_for('resultado'))

@app.route('/resultado')
def resultado():
    db = get_db_connection()  # criando teste
    cursor = db.cursor()
    cursor.execute(f"SELECT AVG(alternativa.pesoExatas), AVG(alternativa.pesoHumanas), AVG(alternativa.pesoSaude) FROM teste_has_alternativa JOIN alternativa ON alternativa.id = teste_has_alternativa.alternativa_id WHERE teste_has_alternativa.teste_id = {teste_id}")
    txt_area = ''
    for linha in cursor.fetchall():
        if linha[0] > linha[1] and linha[0] > linha[2]:
            txt_area = 'exatas'
        elif linha[1] > linha[0] and linha[1] > linha[2]:
            txt_area = 'humanas'
        else:
            txt_area = 'saude'
        print(txt_area)
    return render_template('resultado.html', txt_area = txt_area )






@app.route('/areas')
def area():
   return render_template('areas.html')



@app.route('/inicio')
def inicio():
   return render_template('index.html')

# codigo de Otoniel

@app.route('/') # <-----------Primeira tela do site -
def home():
   return render_template('home.html')



@app.route('/criarconta')
def criarconta():
    return render_template('criarconta.html')




@app.route('/logar', methods=['POST'])
def logar():
    username = request.form.get('username')
    email = request.form.get('email')
    senha = request.form.get('senha')
    print("iniciando")
    if not username or not email or not senha:
        return render_template('criarconta.html', erro="preencha todos os campos.")


    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Verifica se nome ou email já existem
        cursor.execute("SELECT id FROM usuario WHERE nome = %s OR email = %s", (username, email))
        existente = cursor.fetchone()  # ← lê o resultado para evitar erro
        print("existente ="+ str(existente))
        #print(cursor.fetchone())

        if existente:
            cursor.close()
            db.close()
            return render_template('criarconta.html', erro="Nome de usuário ou e-mail já estão cadastrados.")

        # Cadastra novo usuário
        cursor.execute("INSERT INTO usuario (nome, email, senha) VALUES (%s, %s, %s)", (username, email, senha))
        db.commit()
        global user_id
        user_id = cursor.lastrowid

        cursor.close()
        db.close()
        return render_template('index.html')

    except mysql.connector.Error as err:
        return f"Erro no banco de dados: {err}"
    except Exception as e:
        return f"Erro inesperado: {e}"







@app.route('/entrar')
def entrar():
    return render_template('entrar.html')




# Login de usuário existente
@app.route('/entraruser', methods=['POST'])
def entrar_user():
    email = request.form.get('email')
    senha = request.form.get('senha')

    if not email or not senha:
        return render_template('entrar.html', erro="preencha todos os campos.")


    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT usuario.id FROM usuario WHERE email=%s AND senha=%s", (email, senha))
        usuario = cursor.fetchone()
        global user_id
        user_id = usuario[0]
        print("usuario =" + str(user_id))
        # print(cursor.fetchone())
        cursor.close()
        db.close()

        if usuario:
            return render_template('index.html')
        else:
            return render_template('entrar.html', erro="email ou senha incorretos.")

    except mysql.connector.Error as err:
        return f"Erro no banco de dados: {err}"









if __name__ == '__main__':
    app.run(debug=True)
