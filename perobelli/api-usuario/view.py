from flask import Flask, jsonify, request
from main import app, con
from flask_bcrypt import generate_password_hash, check_password_hash
from funcao import valida_senha

@app.route('/listar_usuario', methods=['GET'])
def listar_usuario():
    try:
        cur = con.cursor()
        cur.execute('select id_usuario, nome, email, senha from usuario')
        usuarios = cur.fetchall()

        usuarios_lista = []
        for usuario in usuarios:
            usuarios_lista.append({
                'id_usuario': usuario[0],
                'nome': usuario[1],
                'email': usuario[2],
                'senha': usuario[3]
            })

        return jsonify(mensagem='Lista de usuarios', usuarios =usuarios_lista)

    except Exception as e:
        return jsonify({"message": "Erro ao consultar banco de dados"})
    finally:
        cur.close()


@app.route('/criar_usuario', methods=['POST'])
def criar_usuario():
    try:
        dados = request.get_json()

        nome = dados.get('nome')
        email = dados.get('email')
        senha = dados.get('senha')
        certo = valida_senha(senha)
        print(certo)
        cur = con.cursor()
        if certo == True:
            senha_cripto = generate_password_hash(senha)
            cur.execute('select 1 from usuario where nome =?', (nome,))
            if cur.fetchone():
                return jsonify({"error":"Usuário já cadastrado"}), 400

            cur.execute("""insert into usuario(nome, email, senha)
                              values(?,?,?)""", (nome, email, senha_cripto))
            con.commit()
            return jsonify({
                "message": "Usuário cadastrado com sucesso",
                'usuario':{
                    "nome": nome,
                    "email": email,
                    "senha": senha
                }
            }),201
        return jsonify({"error": "Senha Fraca"}), 400
    except Exception as e:
        return jsonify({"message": "Erro ao cadastrar"})
    finally:
        cur.close()


@app.route('/editar_usuario/<int:id>', methods=['PUT'])
def editar_usuario(id):
    cur = con.cursor()
    cur.execute("""select id_usuario, nome, email, senha from usuario where id_usuario =? """, (id,))
    tem_usuario = cur.fetchone()
    if not tem_usuario:
        cur.close()
        return jsonify({"error": "Usuário não encontrado"}), 404

    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')

    cur.execute(""" update usuario set nome = ?, email = ?, senha =? where id_usuario = ? """, (nome, email, senha, id))
    con.commit()
    cur.close()

    return jsonify({
        "message": "Usuário atualizado com sucesso",
        'usuario': {
            "nome": nome,
            "email": email,
            "senha": senha
        }
    })

@app.route ('/deletar_usuario/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    cur = con.cursor()
    cur.execute("""select 1 from usuario where id_usuario =? """, (id,))
    if not cur.fetchone():
        cur.close()
        return jsonify({"error": "Usuário não encontrado"}), 404
    cur.execute('delete from usuario where id_usuario = ?', (id,))
    con.commit()
    cur.close()
    return  jsonify({"message": "Usuario deletado com sucesso", 'id_usuario':id})




@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()

    email = dados.get('email')
    senha = dados.get('senha')

    cur = con.cursor()
    cur.execute("SELECT u.EMAIL , u.SENHA  FROM USUARIO u WHERE u.EMAIL = 	?", (email,))
    usuario = cur.fetchone()
    if usuario:
        if check_password_hash(usuario[1], senha):
            return jsonify({"message": "Usuário logado com sucesso!"}), 200
        return jsonify({"error": "Dados Incorretos!"}), 400
    return jsonify({"error": "Dados Incorretos!"}), 400


