from flask import Flask, render_template, request, session,redirect,url_for, make_response
from flask_sqlalchemy import SQLAlchemy
import requests
from .views import views
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'zalfa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)
info={'chanson':[]}

app.register_blueprint(views, url_prefix='/')

class Equipe(db.Model):
    __tablename__ = 'equipe'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    
    nom_equipe = db.Column(db.String(100))
    nom_chanson = db.Column(db.String(100))
    score = db.Column(db.Integer)


@app.route('/equipes', methods=['GET', 'POST'])
def equipes():
    if request.method == 'POST':
        nombre_equipes = request.form.get('nombre-equipes', default=0, type=int)
        noms_equipes = {}
        if nombre_equipes:
            for i in range(nombre_equipes):
                nom_equipe = request.form.get(f'equipe {i+1}')
                if nom_equipe:
                    print(f'nom_equipe= {nom_equipe}')
                    noms_equipes[f'Equipe {i+1}'] = nom_equipe
                    print(request.form)
                    
            session['noms_equipes'] = noms_equipes
            return render_template('equipes.html', noms_equipes=noms_equipes, nombre_equipes=nombre_equipes)
        else:
            return render_template('equipes.html')
    else:
        return render_template('equipes.html') 



@app.route('/score', methods=['GET','POST'])
def score():
    noms_equipes = session.get('noms_equipes', {})
    score = session.get('score', 0)
    select_chanson = session.get('chanson_choix')
    select_equipe = session.get('equipe_choix')
    select_score = session.get('score_choix')
    equipe_record = Equipe(nom_equipe=select_equipe,nom_chanson=select_chanson,score=select_score)
    db.session.add(equipe_record)
    db.session.commit()
    select_score = int(select_score) if select_score is not None else 0

    info = session.get('info', {})
    info.setdefault('chanson', [])
    new_data = (str(select_equipe), str(select_chanson), str(select_score))
    if new_data not in info['chanson']:
        info['chanson'].append(new_data)
        
    scores = get_scores()

    session['info'] = info
    session['scores'] = scores
    
    # joker_checkbox = request.form.get('joker_checkbox')
    # print(joker_checkbox)
    # if joker_checkbox:
    #     response = make_response(render_template('score.html', noms_equipes=noms_equipes, score=score, info=info, scores=scores, checkbox_state=True))
    #     response.set_cookie('joker_checkbox', 'checked', max_age=600)
    #     return response
    # else:
    #     response = make_response(render_template('score.html', noms_equipes=noms_equipes, score=score, info=info, scores=scores, checkbox_state=False))
    #     response.set_cookie('joker_checkbox', '', max_age=0)
    #     return response
    return render_template('score.html', noms_equipes=noms_equipes, score=score, info=info, scores=scores)


def scores():
    scores = get_scores()  
    
    return render_template('score.html', scores=scores)

def get_scores():
    scores = {}
    info = session.get('info', {})
    print("info:", info)
    if 'chanson' in info:
        for value in info['chanson']:
            equipe_id = value[0]
            score = int(value[2])
            if equipe_id not in scores:
                scores[equipe_id] = score
            else:
                scores[equipe_id] += score
    print("scores:", scores)
    return scores

@app.route('/song')
def song():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'la_corrida':'la_corrida.mp4', 'lie': 'lie.mp4'}
    selected_song='la_corrida'
    return render_template('song.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song=selected_song)
    
@app.route('/number-selected', methods=['POST'])
def number_selected():
    selected_number = request.form['score_choix']
    try:
        selected_number = int(selected_number)
    except ValueError:
        # Handle the case where the value is not a valid integer
        return "Error: Invalid input"

    score = session.get('score', 0)
    score += selected_number
    session['score'] = score
    return redirect(url_for('song'))

@app.route('/reset-score')
def reset_score():
    session.pop('info', None)
    session['info'] = {'chanson': []}    
    session.pop('chanson_choix',None)  
    session.pop('equipe_choix',None)  
    session.pop('score_choix',None)
    return redirect(url_for('score'))


@app.route('/get_result')
def get_result():
    noms_equipes = session.get('noms_equipes', {})
    result = ''
    response = requests.post('http://127.0.0.1:5000/equipes', data=noms_equipes)
    result = response.text
    return result

@app.route("/select",methods=['GET','POST'])
def select():
    if request.method == 'POST':
        select_chanson = request.form.get('chanson_choix')
        select_equipe = request.form.get('equipe_choix')
        select_score = request.form.get('score_choix')
        session['chanson_choix'] = select_chanson
        session['equipe_choix'] = select_equipe
        session['score_choix'] = select_score
        return redirect(url_for('score'))
    else:
        return render_template('song.html', noms_equipes=session.get('noms_equipes', {}),select_score =select_score ,select_equipe =select_equipe ,select_chanson=select_chanson)




@app.route('/six_s')
def six_s():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/60\'s/Paint_it_black.mp4', 'song2': 'NOPLP/60\'s/say_a_little_prayer_for_you.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('six_s.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/seven_s')
def seven_s():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/70\'s/American_Pie.mp4', 'song2': 'NOPLP/70\'s/Hotel_California.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('seven_s.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/eight_s')
def eight_s():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/80\'s/Girls_just_wanna_have_fun.mp4', 'song2': 'NOPLP/80\'s/I_wanna_dance_with_somebody.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('eight_s.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)

@app.route('/nine_s')
def nine_s():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/90\'s/creep.mp4', 'song2': 'NOPLP/90\'s/wonderwall.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('nine_s.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/francais_eight_s')
def francais_eight_s():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Francais 80\'s/Les_sunlight_des_tropiques.mp4', 'song2': 'NOPLP/Francais 80\'s/Un_autre_monde.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('francais_eight_s.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/francais_2000')
def francais_2000():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Francais 2000/La_lettre.mp4', 'song2': 'NOPLP/Francais 2000/Parle_à_ma_main.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('francais_2000.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)

@app.route('/francais_nouveau')
def francais_nouveau():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Francais nouveau/Balance_ton_quoi.mp4', 'song2': 'NOPLP/Francais nouveau/J_me_tire.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('francais_nouveau.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/the_beattles')
def the_beattles():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/The beattles/here_comes_the_sun.mp4', 'song2': 'NOPLP/The beattles/let_it_be.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('the_beattles.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/francis_cabrel')
def francis_cabrel():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Francis Cabrel/Encore_et_encore.mp4', 'song2': 'NOPLP/Francis Cabrel/La_corrida.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('francis_cabrel.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)

@app.route('/arabe')
def arabe():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Arabe/3_daqat.mp4', 'song2': 'NOPLP/Arabe/Kelna_Mnenjar.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('arabe.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/rihanna')
def rihanna():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Rihanna/love_the_way_you_lie.mp4', 'song2': 'NOPLP/Rihanna/Umbrella.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('rihanna.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/beyonce')
def beyonce():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Beyonce/All_the_single_ladies.mp4', 'song2': 'NOPLP/Beyonce/if_I_were_a_boy.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('beyonce.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)

@app.route('/cat_stevens')
def cat_stevens():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Cat Stevens/Lady_d\'Arbanville.mp4', 'song2': 'NOPLP/Cat Stevens/Wild_world.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('cat_stevens.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/jacques_brel')
def jacques_brel():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Jacques Brel/Ces_gens_la.mp4', 'song2': 'NOPLP/Jacques Brel/Le_port_d\'Amsterdam.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('jacques_brel.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/taylor_swift')
def taylor_swift():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Taylor Swift/Love_Story.mp4', 'song2': 'NOPLP/Taylor Swift/shake_it_off.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('taylor_swift.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)

@app.route('/michael_jakson')
def michael_jakson():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Michael Jakson/Beat_It.mp4', 'song2': 'NOPLP/Michael Jakson/Earth_song.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('michael_jakson.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/santana')
def santana():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Santana/Maria_maria.mp4', 'song2': 'NOPLP/Santana/Smooth.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('santana.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/ed_sheeran')
def ed_sheeran():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Ed Sheeran/Photograph.mp4', 'song2': 'NOPLP/Ed Sheeran/Shape_of_you.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('ed_sheeran.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)

@app.route('/onerepublic')
def onerepublic():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/OneRepublic/Counting_Stars.mp4', 'song2': 'NOPLP/OneRepublic/I_lived.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('onerepublic.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/pop')
def pop():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/POP/The_man_who_can\'t_be_moved.mp4', 'song2': 'NOPLP/POP/Toxic.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('pop.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/love')
def love():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Love/How_deep_is_youre_love.mp4', 'song2': 'NOPLP/Love/This_love.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('love.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)

@app.route('/aznavour')
def aznavour():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Aznavour/Comme_ils_disent.mp4', 'song2': 'NOPLP/Aznavour/Emmenez-moi.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('aznavour.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/claude_francois')
def claude_francois():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/claude francois/Alexandrie_Alexandra.mp4', 'song2': 'NOPLP/claude francois/Cette_année_là.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('claude_francois.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/tom_jones')
def tom_jones():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Tom jones/it\'s_not_unusual.mp4', 'song2': 'NOPLP/Tom jones/Sex_bomb.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('tom_jones.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)

@app.route('/lebnan')
def lebnan():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Lebnan/L7a2_ma_bi_mout.mp4', 'song2': 'NOPLP/Lebnan/Lebnani.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('lebnan.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/break_up')
def break_up():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Break up/Don\'t_speak.mp4', 'song2': 'NOPLP/Break up/Torn.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('break_up.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/backstreet_boys')
def backstreet_boys():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Backstreet Boys/As_long_as_you_love me.mp4', 'song2': 'NOPLP/Backstreet Boys/I_want_it_that_way.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('backstreet_boys.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)

@app.route('/royalty')
def royalty():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Royalty/Bohemian_Rhapsody.mp4', 'song2': 'NOPLP/Royalty/Kiss.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('royalty.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/abba')
def abba():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/ABBA/Dancing_queen.mp4', 'song2': 'NOPLP/ABBA/Money_money_money.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('abba.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/l_yourself')
def l_yourself():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/L Yourself/lose_yourself.mp4', 'song2': 'NOPLP/L Yourself/Love_yourself.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('l_yourself.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)

@app.route('/enfance')
def enfance():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Enfance/aarabiyon_ana.mp4', 'song2': 'NOPLP/Enfance/mon_enfance.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('enfance.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/madonna')
def madonna():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Madonna/Hung_up.mp4', 'song2': 'NOPLP/Madonna/Like_a_virgin.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('madonna.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/country')
def country():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Country/jolene.mp4', 'song2': 'NOPLP/Country/somebody_like_you.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('country.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)

@app.route('/hell')
def hell():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Hell/Highway_to_hell.mp4', 'song2': 'NOPLP/Hell/Le_diable_s\'habille_plus_en_prada.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('hell.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/cheating')
def cheating():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Cheating/confessions_nocturnes.mp4', 'song2': 'NOPLP/Cheating/I_kissed_a_girl.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('cheating.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/nostalgie')
def nostalgie():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Nostalgie/coup_de_vieux.mp4', 'song2': 'NOPLP/Nostalgie/Hier_encore.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('nostalgie.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)

@app.route('/rose')
def rose():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Rose/La_liste.mp4', 'song2': 'NOPLP/Rose/U_and_Ur_Hand.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('rose.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/mad_future')
def mad_future():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Mad future/Mad_world.mp4', 'song2': 'NOPLP/Mad future/The_future.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('mad_future.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)
@app.route('/paradis')
def paradis():
    noms_equipes = session.get('noms_equipes', {})
    my_list = {'song1':'NOPLP/Paradis/Another_day_in_paradise.mp4', 'song2': 'NOPLP/Paradis/Il_y_a.mp4'}
    selected_song1='song1'
    selected_song2='song2'
    return render_template('paradis.html',noms_equipes=noms_equipes ,my_list=my_list, selected_song1=selected_song1, selected_song2=selected_song2)