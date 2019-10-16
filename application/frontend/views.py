import csv
import datetime
import io
import zipfile
import requests

from flask import (
    Blueprint,
    render_template,
    abort,
    request,
    current_app,
    make_response
)

from application.auth.utils import requires_auth
from application.extensions import db
from application.forms import UploadForm, SearchForm

from application.models import (
    CompulsoryPurchaseOrder,
    CompulsoryPurchaseOrderStatus,
    CompulsoryPurchaseOrderInvestigation
)

from application.data import legislation
from application.data import cpo_statuses
from application.data import LocalAuthorityMapping

from application.utils import (
    get_statuses,
    get_latest_statuses,
    get_year_counts,
    get_year_type_counts,
    get_LA_counts,
    counter_to_tuples,
    get_cpo_type_counts,
    has_investigation_counts,
    get_average_durations,
    get_search_result
)

frontend = Blueprint('frontend', __name__, template_folder='templates')


@frontend.route('/')
def index():
    return render_template('index.html')

def per_year_counts_to_data(per_year_counts):
    # access as list of tuples 
    values = [y[1]['total'] for y in per_year_counts]
    return {
            "counts":per_year_counts,
            "max": max(values),
            "min": min(values)
        }


@frontend.route('/dashboard')
@requires_auth
def dashboard():
    cpo_query = CompulsoryPurchaseOrder.query
    cpo_2019_query = CompulsoryPurchaseOrder.query.filter(CompulsoryPurchaseOrder.start_date >= '2019-01-01')

    if request.args and request.args.get('type') in ['housing', 'planning', 'GLA', 'development corporation']:
        cpo_query = cpo_query.filter_by(compulsory_purchase_order_type=request.args.get('type'))
        cpo_2019_query = cpo_2019_query.filter_by(compulsory_purchase_order_type=request.args.get('type'))

    cpos = cpo_query.order_by(CompulsoryPurchaseOrder.start_date.desc()).all()
    cpos_2019 = cpo_2019_query.order_by(CompulsoryPurchaseOrder.start_date.desc()).all()

    per_year_counts = counter_to_tuples(get_year_type_counts(cpos))
    # by_year_data = per_year_counts_to_data(per_year_counts)

   #TODO Colm not sure where you want these in page
    average_durations = {
        "all": get_average_durations(cpos),
        "current": get_average_durations(cpos_2019)
    }

    return render_template('cpo-dashboard.html',
        cpos=cpos,
        by_year=per_year_counts_to_data(per_year_counts[-5:]),
        recent_cpos=get_recent_cpos(cpos),
        cpos_2019=cpos_2019,
        top_orgs=get_LA_counts(cpos)[:5],
        top_orgs_2019=get_LA_counts(cpos_2019)[:5],
        average_durations=average_durations)


def year_date_string(year):
    return "{}-01-01".format(year)

def filter_by_year(year, cpo_query):
    # if matches this year
    if int(year) == datetime.datetime.now().year:
        filtered_query = cpo_query.filter(CompulsoryPurchaseOrder.start_date >= year_date_string(year))
    # else do between
    else:
        next_year = str(int(year) + 1)
        filtered_query = cpo_query.filter(CompulsoryPurchaseOrder.start_date.between(year_date_string(year), year_date_string(next_year)))

    return filtered_query


def filter_if_investigation(cpos):
    with_investigation = [cpo for cpo in cpos if len(cpo.investigations)]
    no_investigation = [cpo for cpo in cpos if not len(cpo.investigations)]
    return with_investigation, no_investigation


def determine_latest_status(cpo):
    if cpo.has_inquiry():
        return cpo.latest_investigation_status().status
    return cpo.latest_status().status


def filter_by_status(status, cpos, filtered_list = []):
    if isinstance(status, list) and len(status) > 0:
        filter_str = status.pop()
        filter_applied_list = [cpo for cpo in cpos if determine_latest_status(cpo) == filter_str]
        return filter_by_status(status, cpos, filtered_list + filter_applied_list)
    return filtered_list


def filter_by_not_status(not_status, cpos):
    return [cpo for cpo in cpos if cpo.latest_status().status != not_status]


def get_recent_cpos(cpos):
    return {
        "received": filter_by_status(['received'], cpos)[:5],
        "not_received": filter_by_not_status('received', cpos)[:5]
    }


@frontend.route('/compulsory-purchase-order')
@requires_auth
def cpo_list():
    la_mapping = LocalAuthorityMapping().order_by_name()
    cpo_query = CompulsoryPurchaseOrder.query

    # check if sorted by option
    if request.args and request.args.get('sort-by') is not None:
        if request.args.get('sort-by') == "date-oldest":
            cpo_query = cpo_query.order_by(CompulsoryPurchaseOrder.start_date.asc())
        else:
            cpo_query = cpo_query.order_by(CompulsoryPurchaseOrder.start_date.desc())
    else:
        cpo_query = cpo_query.order_by(CompulsoryPurchaseOrder.start_date.desc())

    # apply a year filter if exists
    if request.args and request.args.get('year') is not None and request.args.get('year') is not "":
        filtered_query = filter_by_year(request.args['year'], cpo_query)
    else:
        filtered_query = cpo_query

    # then apply org fitler if there is one
    if request.args and request.args.get('org') is not None:
        filtered_query = filtered_query.filter(CompulsoryPurchaseOrder.organisation.in_(request.args.getlist('org')))

    # then apply type filter if there is one
    if request.args and request.args.get('type') is not None:
        filtered_query = filtered_query.filter(CompulsoryPurchaseOrder.compulsory_purchase_order_type.in_(request.args.getlist('type')))

    cpos = filtered_query.all()

    # filter by any selected statuses
    if request.args and request.args.get('current_status') is not None:
        cpos = filter_by_status(request.args.getlist('current_status'), cpos)

    # filter CPOs based on whether still active or not
    if request.args and request.args.get('live') is not None:
        if request.args.get('live') in ['True', 'true', 't']:
            cpos = filter_by_status(['received', 'other'], cpos)
        elif request.args.get('live') in ['False', 'false', 'f']:
            closed_statuses = [status for status in cpo_statuses["final_states"] if status not in ['received', 'other']]
            cpos = filter_by_status(closed_statuses, cpos)

    # filter based on if CPO has associated inquiry
    if request.args and request.args.get('investigation') is not None:
        cpos_w, cpos_wo = filter_if_investigation(cpos)
        if request.args['investigation'] in ['True', 'true', 't', 'yes']:
            filtered_cpos = cpos_w
        elif request.args['investigation'] in ['False', 'false', 'f', 'no']:
            filtered_cpos = cpos_wo
        else:
            filtered_cpos = cpos
        return render_template('cpo-list.html', cpos=filtered_cpos, cpo_statuses=cpo_statuses, las=la_mapping)
    return render_template('cpo-list.html', cpos=cpos, cpo_statuses=cpo_statuses, las=la_mapping)


@frontend.route('/compulsory-purchase-order/<path:id>')
@requires_auth
def cpo(id):
    compulsory_purchase_order = CompulsoryPurchaseOrder.query.get(id)
    if compulsory_purchase_order is None:
        abort(404)
    return render_template('cpo.html', cpo=compulsory_purchase_order)


# ==============================
# Analysis of the data
# ==============================

@frontend.route('/data')
@requires_auth
def data_index():
    cpos = CompulsoryPurchaseOrder.query.all()
    return render_template('data/index.html')


@frontend.route('/data/statuses')
@requires_auth
def statuses():
    cpos = CompulsoryPurchaseOrder.query.all()
    return render_template('data/statuses.html',
                           statuses=get_statuses(cpos),
                           latest_statuses=get_latest_statuses(cpos)
                           )


@frontend.route('/data/years')
@requires_auth
def years():
    cpos = CompulsoryPurchaseOrder.query.all()
    return render_template('data/counts.html', count_type_title="By year", counts=get_year_counts(cpos))


@frontend.route('/data/acquiring_authorities')
@requires_auth
def by_organisation():
    cpos = CompulsoryPurchaseOrder.query.all()
    return render_template('data/counts.html', count_type_title="By acquiring authority", counts=get_LA_counts(cpos))


@frontend.route('/data/types')
@requires_auth
def types():
    cpos = CompulsoryPurchaseOrder.query.all()
    return render_template('data/types.html', count_type_title="By year", counts=get_cpo_type_counts(cpos))


@frontend.route('/data/investigations')
@requires_auth
def has_investigations():
    cpos = CompulsoryPurchaseOrder.query.all()
    print(has_investigation_counts(cpos))
    return render_template('data/investigations.html', count_type_title="By year", counts=has_investigation_counts(cpos))


@frontend.route('/compulsory-purchase-order/<filename>')
@requires_auth
def download_document(filename):
    headers = {'User-Agent': current_app.config['S3_USER_AGENT']}
    url = f"{current_app.config['S3_CPO_FILE_URL']}/{filename}"
    resp = requests.get(url, headers=headers)
    response = make_response(resp.content)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response


@frontend.route('/search', methods=['GET', 'POST'])
@requires_auth
def search():
    form = SearchForm()
    if form.validate_on_submit():
        headers = {'User-Agent': current_app.config['S3_USER_AGENT'], 'Content-Type': 'application/json'}
        url = current_app.config["SEARCH_URL"]
        result = get_search_result(url, form.query.data, headers)
        return render_template('search.html', form=SearchForm(), result=result)
    return render_template('search.html', form=form)


# TODO remove this route as soon as we no longer need
# to keep data out of public repo. it's just a convenience
# for loading data.
@frontend.route('/upload', methods=['GET', 'POST'])
@requires_auth
def upload():

    form = UploadForm()

    if form.validate_on_submit():
        filenames = ['compulsory-purchase-order.csv',
                     'compulsory-purchase-order-status.csv',
                     'compulsory-purchase-order-investigation.csv']

        try:
            with zipfile.ZipFile(form.cpo_zip_file.data) as z:
                for filename in filenames:
                    data = z.read(filename).decode('utf-8-sig')
                    content = csv.DictReader(io.StringIO(data))
                    if filename == 'compulsory-purchase-order.csv':
                        try:
                            cpos = set([])
                            for row in content:
                                cpo = CompulsoryPurchaseOrder.query.get(row['compulsory-purchase-order'])
                                if cpo is None:
                                    start_date = datetime.datetime.strptime(row['start-date'], "%d/%m/%Y").date()
                                    end_date = datetime.datetime.strptime(row['end-date'], "%d/%m/%Y").date() \
                                        if row['end-date'] else None
                                    l = row['legislation']
                                    l_name = legislation.get(l, {}).get('name')
                                    l_url =  legislation.get(l, {}).get('url')
                                    cpo = CompulsoryPurchaseOrder(
                                        compulsory_purchase_order=row['compulsory-purchase-order'],
                                        name=row['name'],
                                        organisation=row['organisation'],
                                        compulsory_purchase_order_type=row['compulsory-purchase-order-type'],
                                        description=row['description'],
                                        start_date=start_date,
                                        end_date=end_date,
                                        legislation=l,
                                        legislation_name=l_name,
                                        legislation_url=l_url
                                    )
                                    cpos.add(cpo)
                                else:
                                    print('CPO', row['compulsory-purchase-order'], 'already loaded')
                            db.session.bulk_save_objects(cpos)
                            db.session.commit()
                        except Exception as e:
                            print('Error loading', row)

                    if filename == 'compulsory-purchase-order-status.csv':
                        try:
                            cpos = set([])
                            for row in content:
                                status = CompulsoryPurchaseOrderStatus.query.get(row['compulsory-purchase-order-status'])
                                if status is None:
                                    start_date = datetime.datetime.strptime(row['start-date'], "%Y-%m-%d").date()
                                    end_date = datetime.datetime.strptime(row['end-date'], "%Y-%m-%d").date() \
                                        if row[ 'end-date'] else None
                                    status = CompulsoryPurchaseOrderStatus(
                                        compulsory_purchase_order_status = row['compulsory-purchase-order-status'],
                                        status = row['status'],
                                        document_url = row['document-url'],
                                        start_date=start_date,
                                        end_date=end_date
                                    )
                                    cpo = CompulsoryPurchaseOrder.query.get(row['compulsory-purchase-order'])
                                    cpo.statuses.append(status)
                                    cpos.add(cpo)
                            db.session.bulk_save_objects(cpos)
                            db.session.commit()
                        except Exception as e:
                            print('Error loading', row)

                    if filename == 'compulsory-purchase-order-investigation.csv':
                        try:
                            cpos = set([])
                            for row in content:
                                investigation = CompulsoryPurchaseOrderInvestigation.query.get(row['compulsory-purchase-order-investigation'])
                                if investigation is None:
                                    start_date = datetime.datetime.strptime(row['start-date'], "%Y-%m-%d").date()
                                    end_date = datetime.datetime.strptime(row['end-date'], "%Y-%m-%d").date() \
                                        if row['end-date'] else None
                                    investigation = CompulsoryPurchaseOrderInvestigation(
                                        compulsory_purchase_order_investigation=row['compulsory-purchase-order-investigation'],
                                        status=row['status'],
                                        inspector_report_url=row['inspector-report-url'],
                                        decision_url=row['decision-url'],
                                        start_date=start_date,
                                        end_date=end_date
                                    )
                                    cpo = CompulsoryPurchaseOrder.query.get(row['compulsory-purchase-order'])
                                    cpo.investigations.append(investigation)
                                    cpos.add(cpo)
                            db.session.bulk_save_objects(cpos)
                            db.session.commit()
                        except Exception as e:
                                print('Error loading', row)

        except Exception as e:
            print(e)

    return render_template('upload.html', form=form)


# set the assetPath variable for use in
# jinja templates
@frontend.context_processor
def asset_path_context_processor():
    return {'assetPath': '/static/govuk/assets'}


@frontend.context_processor
def now_context_processor():
    def current_year():
        return datetime.datetime.now().year
    return {'current_year': current_year }
