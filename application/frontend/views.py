import csv
import datetime
import io
import zipfile

from flask import (
    Blueprint,
    render_template,
    abort,
    request
)

from application.auth.utils import requires_auth
from application.extensions import db
from application.forms import UploadForm

from application.models import (
    CompulsoryPurchaseOrder,
    CompulsoryPurchaseOrderStatus,
    CompulsoryPurchaseOrderInvestigation
)

from application.data.legislation import data as legislation

from application.utils import (
    getStatuses,
    getYearCounts,
    get_LA_counts,
    counter_to_tuples
)

frontend = Blueprint('frontend', __name__, template_folder='templates')


@frontend.route('/')
def index():
    return render_template('index.html')


def per_year_counts_to_data(per_year_counts):
    values = [v for k,v in per_year_counts]
    return {
            "counts":per_year_counts,
            "max": max(values),
            "min": min(values)
        }


@frontend.route('/dashboard')
@requires_auth
def dashboard():
    cpos = CompulsoryPurchaseOrder.query.all()
    per_year_counts = counter_to_tuples(getYearCounts(cpos))
    # by_year_data = per_year_counts_to_data(per_year_counts)
    # print(by_year_data)
    return render_template('cpo-dashboard.html',
        cpos=cpos,
        by_year=per_year_counts_to_data(per_year_counts[-5:]),
        recent_cpos=CompulsoryPurchaseOrder.query.order_by(CompulsoryPurchaseOrder.start_date.desc()).limit(5).all(),
        cpos_2019=CompulsoryPurchaseOrder.query.filter(CompulsoryPurchaseOrder.start_date >= '2019-01-01').all())


def year_date_string(year):
    return "{}-01-01".format(year)

def filter_by_year(year):
    # if matches this year
    if int(year) == datetime.datetime.now().year:
        cpos = CompulsoryPurchaseOrder.query.filter(CompulsoryPurchaseOrder.start_date >= year_date_string(year)).order_by(CompulsoryPurchaseOrder.start_date.desc()).all()
    # else do between
    else:
        next_year = str(int(year) + 1)
        cpos = CompulsoryPurchaseOrder.query.filter(CompulsoryPurchaseOrder.start_date.between(year_date_string(year), year_date_string(next_year))).all()

    return cpos


@frontend.route('/compulsory-purchase-order')
@requires_auth
def cpo_list():
    if request.args and request.args['year'] is not None:
        cpos = filter_by_year(request.args['year'])
    else:
        cpos = CompulsoryPurchaseOrder.query.order_by(CompulsoryPurchaseOrder.start_date.desc()).all()
    return render_template('cpo-list.html', cpos=cpos)


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
    return render_template('data/statuses.html', statuses=getStatuses(cpos))


@frontend.route('/data/years')
@requires_auth
def years():
    cpos = CompulsoryPurchaseOrder.query.all()
    return render_template('data/counts.html', count_type_title="By year", counts=getYearCounts(cpos))


@frontend.route('/data/local_authorities')
@requires_auth
def by_organisation():
    cpos = CompulsoryPurchaseOrder.query.all()
    return render_template('data/counts.html', count_type_title="By organisation", counts=get_LA_counts(cpos))


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
                        for row in content:
                            try:
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
                                    db.session.add(cpo)
                                    db.session.commit()
                                else:
                                    print('CPO', row['compulsory-purchase-order'], 'already loaded')
                            except Exception as e:
                                print('Error loading', row)

                    if filename == 'compulsory-purchase-order-status.csv':
                        for row in content:
                            try:
                                status = CompulsoryPurchaseOrderStatus.query.get(row['compulsory-purchase-order-status'])
                                if status is None:
                                    start_date = datetime.datetime.strptime(row['start-date'], "%d/%m/%Y").date()
                                    end_date = datetime.datetime.strptime(row['end-date'], "%d/%m/%Y").date() \
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
                                    db.session.add(cpo)
                                    db.session.commit()
                            except Exception as e:
                                print('Error loading', row)

                    if filename == 'compulsory-purchase-order-investigation.csv':
                        for row in content:
                            try:
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
                                    db.session.add(cpo)
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
