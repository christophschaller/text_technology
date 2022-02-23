from flask import Blueprint, render_template
from werkzeug.utils import redirect

from app.models import CastGroup, CastRole, Act, Scene, Speech, Line, Token

bp = Blueprint('query', __name__, url_prefix='/query')


@bp.route('/cast_group')
def cast_group():
    cast_group = CastGroup.query.all()
    return render_template('/queries/cast_group.html', cast_group=cast_group)

@bp.route('/cast_role')
def cast_role():
    cast_role = CastRole.query.all()
    return render_template('/queries/cast_role.html', cast_role=cast_role)


@bp.route('/act')
def act():
    act = Act.query.all()
    return render_template('/queries/act.html', act=act)

@bp.route('/scene')
def scene():
    scene = Scene.query.all()
    return render_template('/queries/scene.html', scene=scene)

@bp.route('/speech')
def speech():
    speech = Speech.query.all()
    return render_template('/queries/speech.html', speech=speech)

@bp.route('/line')
def line():
    line = Line.query.all()
    return render_template('/queries/line.html', line=line)

@bp.route('/token')
def token():
    token = Token.query.all()
    return render_template('/queries/token.html', token=token)