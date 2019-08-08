from application.extensions import db
from functools import total_ordering


class OrderedMixin:

    def __eq__(self, other):
        return self.start_date == other.start_date

    def __lt__(self, other):
        return self.start_date < other.start_date


@total_ordering
class CompulsoryPurchaseOrder(db.Model, OrderedMixin):

    compulsory_purchase_order = db.Column(db.String(), primary_key=True, nullable=False)
    name = db.Column(db.String())
    organisation = db.Column(db.String())
    compulsory_purchase_order_type = db.Column(db.String())
    description = db.Column(db.String())
    start_date = db.Column(db.Date())
    end_date = db.Column(db.Date())

    legislation = db.Column(db.String())
    legislation_name = db.Column(db.String())
    legislation_url = db.Column(db.String())

    investigations = db.relationship('CompulsoryPurchaseOrderInvestigation',
                                     lazy=True,
                                     back_populates='compulsory_purchase_order',
                                     order_by='CompulsoryPurchaseOrderInvestigation.start_date')

    statuses = db.relationship('CompulsoryPurchaseOrderStatus',
                               lazy=True,
                               back_populates='compulsory_purchase_order',
                               order_by='CompulsoryPurchaseOrderStatus.start_date')



@total_ordering
class CompulsoryPurchaseOrderInvestigation(db.Model, OrderedMixin):

    compulsory_purchase_order_investigation = db.Column(db.Integer(), primary_key=True, nullable=False)
    status = db.Column(db.String())
    inspector_report_url = db.Column(db.String())
    decision_url = db.Column(db.String())
    start_date = db.Column(db.Date())
    end_date = db.Column(db.Date())

    compulsory_purchase_order_id = db.Column(db.String, db.ForeignKey('compulsory_purchase_order.compulsory_purchase_order'))
    compulsory_purchase_order = db.relationship('CompulsoryPurchaseOrder',  back_populates='investigations')


@total_ordering
class CompulsoryPurchaseOrderStatus(db.Model, OrderedMixin):

    compulsory_purchase_order_status = db.Column(db.Integer(), primary_key=True, nullable=False)
    status = db.Column(db.String())
    document_url = db.Column(db.String())
    start_date = db.Column(db.Date())
    end_date = db.Column(db.Date())

    compulsory_purchase_order_id = db.Column(db.String, db.ForeignKey('compulsory_purchase_order.compulsory_purchase_order'))
    compulsory_purchase_order = db.relationship('CompulsoryPurchaseOrder', back_populates='statuses')
