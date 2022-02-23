from flask import Blueprint, render_template, url_for, request
from werkzeug.utils import redirect

from app.models import CastGroup, CastRole, Act, Scene, Speech, Line, Token

bp = Blueprint('result', __name__, url_prefix='/result')


@bp.route('/cast_group', methods=["POST"])
def cast_group2():
    query = request.form.get("query")
    cast_group = CastGroup.query.filter(CastGroup.id.like('%{}%'.format(query))).all()
    return render_template('/results/cast_group.html', cast_group=cast_group)

@bp.route('/cast_role', methods=["POST"])
def cast_role2():
    query = request.form.get("query")
    cast_role = CastRole.query.filter(CastRole.cast_item_id.like('%{}%'.format(query))).all()
    return render_template('/results/cast_role.html', cast_role=cast_role)


@bp.route('/act', methods=["POST"])
def act2():
    query = request.form.get("query")
    act = Act.query.filter(Act.content.like('%{}%'.format(query))).all()
    return render_template('/results/act.html', act=act)

@bp.route('/scene', methods=["POST"])
def scene2():
    query = request.form.get("query")
    scene = Scene.query.filter(Scene.content.like('%{}%'.format(query))).all()
    return render_template('/results/scene.html', scene=scene)

@bp.route('/speech', methods=["POST"])
def speech2():
    query = request.form.get("query")
    speech = Speech.query.filter(Speech.cast_item_id.like('%{}%'.format(query))).all()
    return render_template('/results/speech.html', speech=speech)

@bp.route('/line', methods=["POST"])
def line2():
    query = request.form.get("query")
    line = Line.query.filter(Line.speech_id.like('%{}%'.format(query))).all()
    return render_template('/results/line.html', line=line)

@bp.route('/token', methods=["POST"])
def token2():
    query = request.form.get("query")
    token = Token.query.filter(Token.content.like('%{}%'.format(query))).all()
    return render_template('/results/token.html', token=token)