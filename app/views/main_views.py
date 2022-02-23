from flask import Blueprint, render_template
from werkzeug.utils import redirect

from app.models import CastGroup, CastRole, Act, Scene, Speech, Line, Token

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def base():
    cast_group = CastGroup.query.all()
    cast_role = CastRole.query.all()
    act = Act.query.all()
    scene = Scene.query.all()
    speech = Speech.query.all()
    line = Line.query.all()
    token = Token.query.all()
    return render_template('start.html', cast_group=cast_group, cast_role=cast_role, act=act,
                            scene=scene, speech=speech, line=line, token=token)

