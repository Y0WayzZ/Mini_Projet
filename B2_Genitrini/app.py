from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

import pymysql.cursors

# (interface de serveur web python)
# comportements et méthodes d'un serveur web
app = Flask(__name__)    # instance de classe Flask (en paramètre le nom du module)
app.secret_key = 'secreeet'

def get_db():
    #mysql --user=jgenitri --password=1511 --host=serveurmysql --database=BDD_jgenitri < sql_projet.sql
    #python app.py
    if 'db' not in g:
        g.db = pymysql.connect(
            host="serveurmysql",                 # à modifier
            user="jgenitri",                     # à modifier
            password="1511",                # à modifier
            database="BDD_jgenitri",        # à modifier
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_layout():
    return render_template('layout.html')

@app.route('/type-reparation/show')
def show_type_reparation():
    mycursor = get_db().cursor()
    sql = '''
    SELECT 
    id_type AS id,
    libelle_type AS libelle
    FROM type_reparation;
    '''
    mycursor.execute(sql)
    type_reparation = mycursor.fetchall()
    print(type_reparation)
    return render_template('/type-reparation/show_type_reparation.html', type_reparation=type_reparation)



@app.route('/variete/etat_show')
def show_etat_variete():
    mycursor = get_db().cursor()
    sql = '''
    SELECT 
    culture.libelle_culture AS nom,
    SUM(variete.stock) AS stock,
    SUM(variete.prix_kg*variete.stock) AS prix
    FROM variete
    LEFT JOIN culture ON variete.culture = culture.id_culture
    GROUP BY culture.id_culture
    ORDER BY culture.id_culture;
    '''
    mycursor.execute(sql)
    stock = mycursor.fetchall()

    sql ='''
    SELECT  culture.libelle_culture AS culture
    FROM culture
    LEFT JOIN variete ON culture.id_culture = variete.culture
    GROUP BY culture.id_culture
    ORDER BY culture.id_culture;
    '''
    mycursor.execute(sql)
    variete = mycursor.fetchall()

    labels = [str(row['culture']) for row in variete]
    return render_template('variete/etat_variete.html', stock=stock, variete=variete,
                           labels=labels)


@app.route('/variete/add', methods=['GET'])
def add_variete():
    mycursor = get_db().cursor()
    sql='''
    SELECT culture.id_culture AS id_culture, culture.libelle_culture AS nom FROM culture;
    '''
    mycursor.execute(sql)
    culture = mycursor.fetchall()
    sql = '''
    SELECT saison.saison AS saison FROM saison;
    '''
    mycursor.execute(sql)
    saison = mycursor.fetchall()
    return render_template('variete/add_variete.html', culture=culture, saison=saison)


@app.route('/variete/add', methods=['POST'])
def valid_add_variete():
    mycursor = get_db().cursor()

    libelle_variete = request.form.get('libelle_variete', '')
    saison = request.form.get('saison', '')
    culture = request.form.get('culture', '')
    prix_kg = request.form.get('prix_kg', '')
    stock = request.form.get('stock', '')
    tuple_insert = (libelle_variete, saison, culture, prix_kg, stock)

    sql = '''
    INSERT INTO variete(libelle_variete, saison, culture, prix_kg, stock)
    VALUES (%s, %s, %s, %s);
    '''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()

    message = u'Nouvelle variété , nom : '+libelle_variete + ' | saison : ' + saison + \
              ' | culture : ' + culture+ '| prix/kg : '+ prix_kg + ' | stock : ' + stock
    flash(message, 'alert-success')
    return redirect('/variete/show')


@app.route('/variete/delete', methods=['GET'])
def delete_variete():
    mycursor = get_db().cursor()
    id_variete = request.args.get('id', '')
    tuple_delete = (id_variete)
    sql = '''
    DELETE FROM variete WHERE id_variete = %s;
    '''
    mycursor.execute(sql, tuple_delete)
    get_db().commit()
    message=u'une variété supprimée, id : ' + id_variete
    flash(message, 'alert-warning')
    return redirect('/variete/show')

@app.route('/variete/edit', methods=['GET'])
def edit_variete():
    mycursor = get_db().cursor()

    sql = '''
            SELECT culture.id_culture AS id_culture, culture.libelle_culture AS nom FROM culture;
            '''
    mycursor.execute(sql)
    culture = mycursor.fetchall()

    sql = '''
        SELECT saison.saison AS saison FROM saison;
        '''
    mycursor.execute(sql)
    saison = mycursor.fetchall()

    id = request.args.get('id', '')
    sql = '''
        SELECT variete.id_variete AS id,
        variete.libelle_variete AS nom,
        variete.saison AS saison,
        variete.culture AS culture,
        variete.prix_kg AS prix,
        variete.stock AS stock
        FROM variete, culture
        WHERE variete.id_variete=%s AND culture.id_culture = variete.culture;
        '''
    mycursor.execute(sql, (id))
    variete = mycursor.fetchone()
    return render_template('variete/edit_variete.html', variete=variete, culture=culture, saison=saison)

@app.route('/variete/edit', methods=['POST'])
def valid_edit_variete():
    mycursor = get_db().cursor()
    id = request.form.get('id', '')
    nom = request.form.get('nom', '')
    saison = request.form.get('saison', '')
    culture = request.form.get('culture', '')
    prix = request.form.get('prix_kg', '')
    stock = request.form.get('stock', '')
    tuple_update = (nom, saison, culture, prix, stock, id)
    sql = '''
    UPDATE variete SET libelle_variete = %s, saison = %s, culture = %s,
     prix_kg = %s, stock = %s WHERE id_variete = %s;'''
    mycursor.execute(sql, tuple_update)
    get_db().commit()
    message = u'Une variété modifiée, id : '+ id + ' | nom : '+ nom + \
              ' | saison : '+ saison + ' | type_culture : '+ culture + \
              ' | prix : ' + prix  + ' | stock : ' + stock
    flash(message, 'alert-success')
    return redirect('/variete/show')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
