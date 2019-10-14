import click

from flask.cli import with_appcontext

from application.data.pdf_filenames import filenames
from application.models import CompulsoryPurchaseOrder


@click.command()
@with_appcontext
def load_pdfs():
    from application.extensions import db
    updates = []
    for cpo in CompulsoryPurchaseOrder.query.all():
        if cpo.pdf_filenames is not None:
            cpo.pdf_filenames = None
            updates.append(cpo)
            print(f'Delete pdf filenames for {cpo.compulsory_purchase_order}')

    db.session.bulk_save_objects(updates)
    db.session.commit()

    updates = []
    for filename in filenames:
        id = '/'.join(filename.split('_')[:-1])
        cpo = CompulsoryPurchaseOrder.query.get(id)
        if cpo is not None:
            if cpo.pdf_filenames is None:
                cpo.pdf_filenames = []
            cpo.pdf_filenames.append(filename)
            updates.append(cpo)
            print(f'Added pdf {filename} to {cpo.compulsory_purchase_order}')
        else:
            print(f'No cpo found for id {id}')

    db.session.bulk_save_objects(updates)
    db.session.commit()
    print('Done')